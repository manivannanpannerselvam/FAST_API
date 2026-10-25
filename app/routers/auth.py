"""
FASTAPI TUTORIAL - Lesson 12, file 2: routers/auth.py

Register and (in Step 3) log in.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app.database import SessionDep
from app.models import Token, User, UserCreate, UserPublic
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


# --- Step 2b: REGISTER -> POST /auth/register ---------------------------------
@router.post("/register", response_model=UserPublic, status_code=201)
def register(user: UserCreate, session: SessionDep):
    # 409 if the username is taken (same idea as the duplicate book check).
    existing = session.exec(select(User).where(User.username == user.username)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already taken")

    # Store the HASH. The plain password is never saved anywhere.
    db_user = User(username=user.username, hashed_password=hash_password(user.password))
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user  # response_model=UserPublic strips the hash


# --- Step 3c: LOGIN -> POST /auth/login ---------------------------------------
# OAuth2PasswordRequestForm reads FORM fields (username, password), not JSON.
# That is the standard way, and it is what the Authorize button in /docs uses.
@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    user = session.exec(select(User).where(User.username == form.username)).first()

    # SAME message for "no such user" and "wrong password", so an attacker
    # cannot use login to find out which usernames exist.
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"access_token": create_access_token(user.username), "token_type": "bearer"}
