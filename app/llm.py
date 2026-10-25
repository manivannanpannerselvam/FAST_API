"""
FASTAPI TUTORIAL - Lesson 13, file 1: llm.py

Everything about talking to Gemini lives here, so the routers never touch the
API directly. To switch to another LLM later, only this file changes.
"""

import functools
import logging
import os
import time

from google import genai
from google.genai import types

from app.tools import count_books, list_authors, search_books

# "uvicorn.error" is the logger the server already prints to the terminal,
# so these lines show up next to the request lines.
logger = logging.getLogger("uvicorn.error")

# --- Step 2a: settings come from environment variables -------------------------
# The key is NEVER written in code. Set it in your terminal before starting:
#   export GEMINI_API_KEY="your-key"
# GEMINI_MODEL is optional. "flash-lite" models are small and cheap.
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Cap the length of every answer, so one request can never produce a huge bill.
MAX_OUTPUT_TOKENS = 500


class LLMNotConfigured(Exception):
    """GEMINI_API_KEY is missing."""


# --- Step 2b: create the client once, on first use ------------------------------
# Lazy on purpose: the app can start (and /docs can open) even without a key;
# only /chat fails, with a clear message.
_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise LLMNotConfigured("GEMINI_API_KEY is not set")
        # timeout is in milliseconds: give up after 30 s instead of waiting forever.
        _client = genai.Client(
            api_key=api_key, http_options=types.HttpOptions(timeout=30_000)
        )
    return _client


# --- Step 7a: tell Gemini what it is for and when to use the tools --------------
SYSTEM_INSTRUCTION = (
    "You are the assistant of a books database. "
    "For ANY question about books, authors, prices or pages in the database, "
    "you MUST use the tools and answer only from what they return. "
    "Never invent books or authors. If the tools return nothing, say so. "
    "For other questions, answer normally."
)


# --- Step 7b: log every tool Gemini calls, and remember which ones --------------
# functools.wraps keeps the name, arguments and docstring that Gemini reads.
# `used` is a list that belongs to ONE request; each tool call adds its name.
def _logged(tool, used: list[str]):
    @functools.wraps(tool)
    def wrapper(*args, **kwargs):
        logger.info("Gemini: tool called -> %s(%s)", tool.__name__, kwargs)
        used.append(tool.__name__)
        return tool(*args, **kwargs)

    return wrapper


# --- Step 2c: ask Gemini one question -------------------------------------------
# Returns (answer text, names of the tools Gemini used). An empty list means
# Gemini answered on its own, without touching the database.
def ask_gemini(message: str) -> tuple[str, list[str]]:
    logger.info("Gemini: calling %s (message length %d)", MODEL, len(message))
    started = time.perf_counter()

    # Fresh list + fresh wrappers for every request, so requests never mix.
    tools_used: list[str] = []
    tools = [_logged(t, tools_used) for t in (search_books, list_authors, count_books)]

    # Step 7c: tools=... hands the functions to Gemini. The library then runs the
    # loop: Gemini asks for a tool -> we run it -> the result goes back to Gemini
    # -> Gemini writes the final answer. maximum_remote_calls stops endless loops.
    response = get_client().models.generate_content(
        model=MODEL,
        contents=message,
        config=types.GenerateContentConfig(
            max_output_tokens=MAX_OUTPUT_TOKENS,
            system_instruction=SYSTEM_INSTRUCTION,
            tools=tools,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                maximum_remote_calls=5
            ),
        ),
    )

    # usage_metadata is what Gemini says it counted (and what you are billed on).
    usage = response.usage_metadata
    logger.info(
        "Gemini: answered in %.2fs, tokens in=%s out=%s",
        time.perf_counter() - started,
        usage.prompt_token_count if usage else "?",
        usage.candidates_token_count if usage else "?",
    )
    return response.text or "", tools_used
