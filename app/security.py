"""
FASTAPI TUTORIAL - Lesson 12, file 1: security.py

Passwords are NEVER stored as plain text. We store a HASH: a scrambled value
that cannot be turned back into the password. To check a login, we hash what
the user typed and compare it with the stored hash.
"""

import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

# --- Step 1a: the hasher (Argon2 is a modern, slow-on-purpose algorithm) -------
password_hash = PasswordHash.recommended()


# --- Step 1b: turn a password into a hash -------------------------------------
# The same password gives a DIFFERENT hash every time (a random "salt" is mixed
# in), so two users with the same password do not look the same in the table.
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# --- Step 1c: check a typed password against a stored hash --------------------
def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


# --- Lesson 12, Step 3a: JWT settings -----------------------------------------
# SECRET_KEY signs every token. Anyone who knows it can forge tokens, so on a
# real server set it as an environment variable. This default is for learning
# only. (Make a good one with:  openssl rand -hex 32)
SECRET_KEY = os.getenv(
    "SECRET_KEY", "learning-only-secret-change-me-on-a-real-server-0123456789"
)
ALGORITHM = "HS256"
TOKEN_MINUTES = 30


# --- Step 3b: create a token --------------------------------------------------
# A JWT is three parts: header.payload.signature. The payload here says
#   sub = "subject": who the token is for (the username)
#   exp = "expires": when it stops working
# The signature proves the server made it and nobody changed it.
def create_access_token(username: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTES)
    payload = {"sub": username, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# --- Lesson 12, Step 4a: read a token back ------------------------------------
# Returns the username inside a valid token, or None if the token is fake,
# edited, or expired (jwt.decode checks the signature AND the exp time).
def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        return None
    return payload.get("sub")
