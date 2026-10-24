"""
FASTAPI TUTORIAL - Lesson 9: a full CRUD API

CRUD = Create, Read, Update, Delete: the four basic things an API does.
This lesson combines everything from lessons 4-8 into one working app.

Run:  uv run fastapi dev 09_crud_api.py
"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Lesson 9 - CRUD API")


# --- Step 1: three models for three jobs --------------------------------------
# BookCreate : what the client sends to create (no id: WE generate it)
# BookUpdate : every field optional, for PATCH (change only what you send)
# Book       : what we return (adds the id)
class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0)


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    author: str | None = Field(default=None, min_length=1, max_length=50)
    price: float | None = Field(default=None, gt=0)


class Book(BookCreate):
    id: int


# --- Step 2: the in-memory "database" and an id counter -----------------------
# Lost on restart. Lesson 10 replaces this with a real database.
books_db: dict[int, Book] = {}
next_id = 1


# Reused from Lesson 8: shared pagination.
def pagination(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=50),
):
    return {"skip": skip, "limit": limit}


Pagination = Annotated[dict, Depends(pagination)]


# --- Step 3: CREATE -> POST /books --------------------------------------------
@app.post("/books", response_model=Book, status_code=201)
def create_book(book: BookCreate):
    global next_id
    new_book = Book(id=next_id, **book.model_dump())
    books_db[next_id] = new_book
    next_id += 1
    return new_book


# --- Step 4: READ all -> GET /books -------------------------------------------
@app.get("/books", response_model=list[Book])
def list_books(page: Pagination):
    all_books = list(books_db.values())
    return all_books[page["skip"] : page["skip"] + page["limit"]]


# --- Step 5: READ one -> GET /books/{id} --------------------------------------
@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    return books_db[book_id]


# --- Step 6: UPDATE (replace) -> PUT /books/{id} ------------------------------
# PUT = send the WHOLE book again. Every field is required (BookCreate).
@app.put("/books/{book_id}", response_model=Book)
def replace_book(book_id: int, book: BookCreate):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    books_db[book_id] = Book(id=book_id, **book.model_dump())
    return books_db[book_id]


# --- Step 7: UPDATE (partial) -> PATCH /books/{id} ----------------------------
# PATCH = send ONLY the fields to change. exclude_unset=True skips fields
# the client did not send, so they keep their old values.
@app.patch("/books/{book_id}", response_model=Book)
def update_book(book_id: int, changes: BookUpdate):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    stored = books_db[book_id]
    updated = stored.model_copy(update=changes.model_dump(exclude_unset=True))
    books_db[book_id] = updated
    return updated


# --- Step 8: DELETE -> DELETE /books/{id} -------------------------------------
# 204 = "done, nothing to send back".
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    del books_db[book_id]
