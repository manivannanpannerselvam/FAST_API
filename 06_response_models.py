"""
FASTAPI TUTORIAL - Lesson 6: response models and status codes

Lesson 5 controlled what comes IN (the request).
Lesson 6 controls what goes OUT (the response).

Run:  uv run fastapi dev 06_response_models.py
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Lesson 6 - Response Models")

# A fake "database": a dict in memory, keyed by username.
# It is emptied every time the server restarts.
users_db = {}


# --- Step 1: a model for what the client SENDS --------------------------------
class UserIn(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str
    password: str = Field(min_length=6)  # secret: must never be sent back


# --- Step 2: a model for what the client GETS BACK ----------------------------
# Same as UserIn, but without the password.
class UserOut(BaseModel):
    username: str
    email: str


# --- Step 3: response_model filters the output --------------------------------
# We return the full user (with password), but FastAPI only sends the
# fields listed in UserOut.
@app.post("/users", response_model=UserOut)
def create_user(user: UserIn):
    users_db[user.username] = user  # save it (password included)
    return user


# --- Step 4: status_code sets the success code --------------------------------
# 201 = "Created". It is the correct code when a POST creates something.
# The default for every route is 200.
@app.post("/users-created", response_model=UserOut, status_code=201)
def create_user_201(user: UserIn):
    users_db[user.username] = user
    return user


# --- Step 5: GET all users ----------------------------------------------------
# list[UserOut] = "a list of users, each filtered to UserOut" (no passwords).
@app.get("/users", response_model=list[UserOut])
def list_users():
    return list(users_db.values())


# --- Step 6: GET one user by username -----------------------------------------
@app.get("/users/{username}", response_model=UserOut)
def get_user(username: str):
    if username not in users_db:
        # 404 = "Not Found". HTTPException is covered fully in Lesson 7.
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[username]
