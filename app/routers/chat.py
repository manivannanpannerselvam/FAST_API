"""
FASTAPI TUTORIAL - Lesson 13, file 2: routers/chat.py

POST /chat: send a message, get Gemini's answer.
"""

import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException
from google.genai import errors as genai_errors

from app.dependencies import get_current_user
from app.llm import LLMNotConfigured, ask_gemini
from app.models import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger("uvicorn.error")


# --- Step 3b: CHAT -> POST /chat ----------------------------------------------
# Same pattern as every route so far: validate the body, do the work, return.
# The "work" is one call to ask_gemini(), which lives in llm.py.
#
# Step 5: dependencies=[Depends(get_current_user)] = "must be logged in".
# Every chat costs money, so only people with a valid token can use it.
@router.post(
    "", response_model=ChatResponse, dependencies=[Depends(get_current_user)]
)
def chat(request: ChatRequest):
    # --- Step 4: turn every way the AI call can fail into a clear error ---
    # The client gets a short, safe message. The real details go to the server
    # log only (they can mention internals the client should not see).
    try:
        answer, tools_used = ask_gemini(request.message)
    except LLMNotConfigured:
        # Our mistake (no key on the server), not the client's.
        raise HTTPException(status_code=503, detail="Chat is not configured on the server")
    except httpx.TimeoutException:
        logger.exception("Gemini timed out")
        raise HTTPException(status_code=504, detail="The AI service took too long to answer")
    except httpx.TransportError:
        logger.exception("Could not reach Gemini")
        raise HTTPException(status_code=502, detail="Could not reach the AI service")
    except genai_errors.APIError as e:
        logger.exception("Gemini returned an error (code %s)", e.code)
        if e.code == 429:  # quota or rate limit reached
            raise HTTPException(status_code=429, detail="AI quota reached, try again later")
        raise HTTPException(status_code=502, detail="The AI service returned an error")

    if not answer:  # Gemini replied, but with no text (for example, blocked)
        raise HTTPException(status_code=502, detail="The AI service returned an empty answer")
    # source tells the client which path produced the answer.
    source = "gemini+database" if tools_used else "gemini"
    return {"answer": answer, "source": source, "tools_used": tools_used}
