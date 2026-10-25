"""
FASTAPI TUTORIAL - Lesson 11, file 4: main.py

The front door of the app. It does only three things:
  1. create the app
  2. create the database tables at startup
  3. plug in the routers

Run:  uv run fastapi dev app/main.py
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import auth, authors, books, chat


# --- Step 4a: run code once at startup ----------------------------------------
# Code before `yield` runs when the app starts, code after it when it stops
# (the same yield idea as Lesson 8).
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


# --- Step 4b: create the app --------------------------------------------------
app = FastAPI(title="Lesson 11 - Routers", lifespan=lifespan)

# --- Step 4c: plug in the routers ---------------------------------------------
# Each include_router adds all the routes of that router (with its prefix).
app.include_router(books.router)
app.include_router(authors.router)  # Step 5: one more line = a whole new resource
app.include_router(auth.router)  # Lesson 12
app.include_router(chat.router)  # Lesson 13
