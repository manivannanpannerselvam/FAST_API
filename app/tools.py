"""
FASTAPI TUTORIAL - Lesson 13, file 3: tools.py

"Tools" are plain Python functions that Gemini is allowed to call. Gemini does
not see your database; it only sees the NAME, the DOCSTRING and the ARGUMENTS
of each function below, and decides when one of them is useful.

So: write clear docstrings. They are the instructions Gemini reads.

Rules for tools:
  - READ ONLY. Gemini never gets a function that changes or deletes data.
  - Always limit the amount of data returned (you pay for tokens).
"""

from sqlmodel import Session, func, select

from app.database import engine
from app.models import Book

MAX_RESULTS = 20


# --- Step 6a: search books by title and/or author -----------------------------
def search_books(title: str = "", author: str = "") -> list[dict]:
    """Search the books database.

    Args:
        title: part of a book title to look for (case-insensitive). Leave empty
            to not filter by title.
        author: part of an author name to look for (case-insensitive). Leave
            empty to not filter by author.

    Returns:
        A list of matching books (at most 20), each with id, title, author,
        price and page. An empty list means nothing matched.
    """
    statement = select(Book).order_by(Book.id).limit(MAX_RESULTS)
    # autoescape=True makes "%" and "_" typed by the user match literally.
    if title.strip():
        statement = statement.where(Book.title.icontains(title.strip(), autoescape=True))
    if author.strip():
        statement = statement.where(Book.author.icontains(author.strip(), autoescape=True))

    with Session(engine) as session:
        books = session.exec(statement).all()
    return [
        {"id": b.id, "title": b.title, "author": b.author, "price": b.price, "page": b.page}
        for b in books
    ]


# --- Step 6b: list the authors with their number of books ---------------------
def list_authors() -> list[dict]:
    """List every author in the database with how many books they have.

    Returns:
        A list like [{"author": "Name", "book_count": 2}, ...].
    """
    statement = (
        select(Book.author, func.count(Book.id)).group_by(Book.author).order_by(Book.author)
    )
    with Session(engine) as session:
        rows = session.exec(statement).all()
    return [{"author": author, "book_count": count} for author, count in rows]


# --- Step 6c: count all the books ---------------------------------------------
def count_books() -> int:
    """Return the total number of books in the database."""
    with Session(engine) as session:
        return session.exec(select(func.count(Book.id))).one()
