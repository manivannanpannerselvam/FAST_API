"""
FASTAPI TUTORIAL - Lesson 11, file 5: routers/authors.py

A SECOND router. It has its own prefix and tag, reuses the same database
session and models, and main.py plugs it in with one line.
"""

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.database import SessionDep
from app.models import AuthorPublic, Book, BookPublic

# --- Step 5b: the router ------------------------------------------------------
router = APIRouter(prefix="/authors", tags=["authors"])


# --- Step 5c: GET /authors -> every author with how many books they have ------
# GROUP BY collapses all rows of one author into a single row; count() counts
# the rows in each group.
@router.get("", response_model=list[AuthorPublic])
def list_authors(session: SessionDep):
    statement = (
        select(Book.author, func.count(Book.id))
        .group_by(Book.author)
        .order_by(Book.author)
    )
    rows = session.exec(statement).all()
    return [{"author": author, "book_count": count} for author, count in rows]


# --- Step 5d: GET /authors/{author}/books -> the books of ONE author ----------
# A path can nest: /authors/Manivannan/books. 404 if the author has no books.
@router.get("/{author}/books", response_model=list[BookPublic])
def list_books_by_author(author: str, session: SessionDep):
    books = session.exec(
        select(Book).where(Book.author == author).order_by(Book.id)
    ).all()
    if not books:
        raise HTTPException(status_code=404, detail=f"No books found for author '{author}'")
    return books
