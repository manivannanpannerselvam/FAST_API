"""
FASTAPI TUTORIAL - Lesson 11, file 1: database.py

Everything about CONNECTING to the database lives here and nowhere else.
Other files import `SessionDep` and never need to know the connection URL.
"""

import os
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

# --- Step 1a: the connection URL comes from an environment variable ------------
# os.getenv("NAME", default) reads the variable NAME, and falls back to the
# default when it is not set. Locally the default is fine. On a server you set
# DATABASE_URL instead of editing code (and real passwords never enter the code).
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://manivannanp@localhost:5432/bookdb",
)

# The engine is the connection to the database. Create it ONCE.
engine = create_engine(DATABASE_URL)


# --- Step 1b: create the tables -----------------------------------------------
# Called once at startup (from main.py). Creates any table that is missing.
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# --- Step 1c: a session per request -------------------------------------------
# Same yield pattern as Lesson 8: open before the route, close after it.
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
