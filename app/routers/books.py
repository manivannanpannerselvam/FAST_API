"""
FASTAPI TUTORIAL - Lesson 11, file 3: routers/books.py

All the /books endpoints, in an APIRouter instead of directly on `app`.
main.py plugs this router into the app (Step 4).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select

from app.database import SessionDep
from app.dependencies import get_current_user
from app.models import Book, BookBase, BookPublic, BookUpdate

# --- Step 3a: the router ------------------------------------------------------
# prefix="/books" is put in front of every path below, so "" means /books and
# "/{book_id}" means /books/{book_id}. tags groups these routes in /docs.
router = APIRouter(prefix="/books", tags=["books"])


# --- Step 3b: CREATE -> POST /books -------------------------------------------
# Lesson 12: dependencies=[Depends(get_current_user)] = "must be logged in".
@router.post(
    "",
    response_model=BookPublic,
    status_code=201,
    dependencies=[Depends(get_current_user)],
)
def create_book(book: BookBase, session: SessionDep):
    # Refuse duplicates (same title + same author). 409 = "clashes with
    # something that already exists".
    existing = session.exec(
        select(Book).where(Book.title == book.title, Book.author == book.author)
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Book '{book.title}' by {book.author} already exists (id {existing.id})",
        )

    db_book = Book.model_validate(book)  # BookBase -> Book (a table row object)
    session.add(db_book)  # stage it
    session.commit()  # write it to PostgreSQL
    session.refresh(db_book)  # reload it so we get the id the database made
    return db_book


# --- Step 3c: READ all -> GET /books ------------------------------------------
# offset/limit give pagination, done by the DATABASE.
@router.get("", response_model=list[BookPublic])
def list_books(
    session: SessionDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=50),
):
    statement = select(Book).order_by(Book.id).offset(skip).limit(limit)
    return session.exec(statement).all()


# --- Step 3d: READ one -> GET /books/{id} -------------------------------------
@router.get("/{book_id}", response_model=BookPublic)
def get_book(book_id: int, session: SessionDep):
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


# --- Step 3e: UPDATE (replace) -> PUT /books/{id} -----------------------------
# PUT = send the WHOLE book again; every field is required (BookBase).
@router.put(
    "/{book_id}", response_model=BookPublic, dependencies=[Depends(get_current_user)]
)
def replace_book(book_id: int, book: BookBase, session: SessionDep):
    db_book = session.get(Book, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db_book.sqlmodel_update(book.model_dump())
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


# --- Step 3f: UPDATE (partial) -> PATCH /books/{id} ---------------------------
# PATCH = send ONLY the fields to change. exclude_unset=True drops the
# fields the client did not send, so they keep their old values.
@router.patch(
    "/{book_id}", response_model=BookPublic, dependencies=[Depends(get_current_user)]
)
def update_book(book_id: int, changes: BookUpdate, session: SessionDep):
    db_book = session.get(Book, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db_book.sqlmodel_update(changes.model_dump(exclude_unset=True))
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


# --- Step 3g: DELETE -> DELETE /books/{id} ------------------------------------
@router.delete("/{book_id}", dependencies=[Depends(get_current_user)])
def delete_book(book_id: int, session: SessionDep):
    db_book = session.get(Book, book_id)
    if db_book is None:
        raise HTTPException(
            status_code=404,
            detail=f"Book {book_id} not found in the database, nothing was deleted",
        )
    session.delete(db_book)
    session.commit()
    return {"message": f"Book {book_id} deleted successfully"}
