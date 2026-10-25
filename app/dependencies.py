"""
FASTAPI TUTORIAL - Lesson 12, file 3: dependencies.py

get_current_user: the dependency that guards a route.
It reads the token from the "Authorization: Bearer <token>" header, checks it,
and returns the logged-in user. Any problem -> 401 and the route never runs.
Same Depends idea as the API-key check in Lesson 8.
"""

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select

from app.database import SessionDep
from app.models import User
from app.security import decode_access_token

# tokenUrl tells /docs where to log in; it also makes the Authorize button appear.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    credentials_error = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    username = decode_access_token(token)
    if username is None:  # fake, edited or expired token
        raise credentials_error

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:  # token is fine but the user no longer exists
        raise credentials_error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
