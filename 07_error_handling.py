"""
FASTAPI TUTORIAL - Lesson 7: error handling

Things go wrong: a user is missing, a username is taken, input is bad.
Good APIs answer with the RIGHT status code and a CLEAR message.

Run:  uv run fastapi dev 07_error_handling.py
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Lesson 7 - Error Handling")

users_db = {}


class UserIn(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str
    password: str = Field(min_length=6)


class UserOut(BaseModel):
    username: str
    email: str


# --- Step 1: raise an error with HTTPException --------------------------------
# 404 = "Not Found". `detail` is the message the client sees.
@app.get("/users/{username}", response_model=UserOut)
def get_user(username: str):
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[username]


# --- Step 2: 409 Conflict (fixes the Lesson 6 gap) ----------------------------
# In Lesson 6, posting the same username twice silently overwrote the first.
# Now we refuse. 409 = "this clashes with something that already exists".
@app.post("/users", response_model=UserOut, status_code=201)
def create_user(user: UserIn):
    if user.username in users_db:
        raise HTTPException(status_code=409, detail="Username already taken")
    users_db[user.username] = user
    return user


# --- Step 3: 400 Bad Request for rules a Field() cannot express ---------------
# Field() checks one value at a time. Some rules need your own logic.
@app.post("/users/{username}/email", response_model=UserOut)
def change_email(username: str, email: str):
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Email must contain '@'")
    users_db[username].email = email
    return users_db[username]


# --- Step 4: extra headers on an error ----------------------------------------
# `headers` adds HTTP headers to the error response.
@app.delete("/users/{username}", status_code=204)
def delete_user(username: str):
    if username not in users_db:
        raise HTTPException(
            status_code=404,
            detail="User not found",
            headers={"X-Error-Source": "delete_user"},
        )
    del users_db[username]


# --- Step 5: your own exception + a handler -----------------------------------
# A custom exception class, plus one function that decides how EVERY
# raise of it is turned into a response. Gives one consistent error format.
class QuotaExceeded(Exception):
    def __init__(self, limit: int):
        self.limit = limit


@app.exception_handler(QuotaExceeded)
def quota_exceeded_handler(request: Request, exc: QuotaExceeded):
    return JSONResponse(
        status_code=429,  # 429 = "Too Many Requests"
        content={"error": "quota_exceeded", "limit": exc.limit},
    )


@app.get("/ask")
def ask(calls_made: int):
    # Pretend each user may make 3 calls (think: an LLM API quota).
    if calls_made >= 3:
        raise QuotaExceeded(limit=3)
    return {"answer": "Here is your answer", "calls_left": 3 - calls_made - 1}
