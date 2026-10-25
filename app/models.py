"""
FASTAPI TUTORIAL - Lesson 11, file 2: models.py

Every model (the table and the request/response shapes) lives here.
Routers import from this file, so each shape is defined exactly once.
"""

from typing import Annotated

from pydantic import StringConstraints
from sqlmodel import Field, SQLModel

# Text that is trimmed FIRST (strip_whitespace), THEN checked for length and
# characters. So "   " becomes "" and fails min_length=1, " Clean Code " is saved
# as "Clean Code", and "Clean Code ." is rejected because of the "." .
# pattern: only letters (any language), digits, space, apostrophe and hyphen.
NonBlankStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        pattern=r"^(?:[^\W_]|[ '\-])+$",
    ),
]


# --- Step 2a: what the CLIENT sends (POST and PUT) ----------------------------
# No id: the database makes it.
class BookBase(SQLModel):
    title: NonBlankStr = Field(max_length=100)
    author: NonBlankStr = Field(max_length=50)
    price: float = Field(gt=0)
    page: int = Field(default=0, ge=0)


# --- Step 2b: the database TABLE ----------------------------------------------
# table=True makes this class a real table named "book" (BookBase + id).
class Book(BookBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


# --- Step 2c: what we RETURN --------------------------------------------------
# Plain types on purpose: the input rules (NonBlankStr) are for what clients
# SEND. If old rows in the table break those rules, reading them must not fail.
class BookPublic(SQLModel):
    title: str
    author: str
    price: float
    page: int
    id: int


# --- Lesson 12, Step 2a: users ------------------------------------------------
# The table has the HASH, never the password. The table is called "users"
# (plural) because "user" is a reserved word in PostgreSQL.
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)  # the database enforces unique
    hashed_password: str


# What the client sends to register.
class UserCreate(SQLModel):
    username: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=3,
            max_length=20,
            pattern=r"^[A-Za-z0-9_]+$",  # letters, digits and underscore only
        ),
    ]
    password: str = Field(min_length=6, max_length=72)


# What we return: NO password, NO hash.
class UserPublic(SQLModel):
    id: int
    username: str


# What login returns (the names are the OAuth2 standard).
class Token(SQLModel):
    access_token: str
    token_type: str


# --- Step 5a: what GET /authors returns ---------------------------------------
# Not a table: it is a summary computed from the book table.
class AuthorPublic(SQLModel):
    author: str
    book_count: int


# --- Step 2d: what the client sends for PATCH ---------------------------------
# Every field is optional: the client sends ONLY what it wants to change.
class BookUpdate(SQLModel):
    title: NonBlankStr | None = Field(default=None, max_length=100)
    author: NonBlankStr | None = Field(default=None, max_length=50)
    price: float | None = Field(default=None, gt=0)
    page: int | None = Field(default=None, ge=0)
