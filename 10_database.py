"""
FASTAPI TUTORIAL - Lesson 10: a real database (PostgreSQL + SQLModel)

Lesson 9 kept books in a dictionary, lost on every restart.
Lesson 10 stores them in PostgreSQL, so they survive.

Run:  uv run fastapi dev 10_database.py
"""

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import StringConstraints
from sqlmodel import Field, Session, SQLModel, create_engine, select


# --- Step 3a: connect to the database -----------------------------------------
# The URL says: driver://user@host:port/database_name
# Local PostgreSQL lets this user in without a password.
DATABASE_URL = "postgresql+psycopg://manivannanp@localhost:5432/bookdb"

# The engine is the connection to the database. Create it ONCE.
# echo=True prints the SQL that SQLModel runs: great for learning.
engine = create_engine(DATABASE_URL, echo=True)


# --- Step 3b: a table is a class ----------------------------------------------
# table=True makes this class a real database table named "book".
# Without it, this would be a plain Pydantic model (like Lesson 9).
# --- Step 4a: split the fields from the table ---------------------------------
# BookBase : the fields the CLIENT may send (no id: the database makes it)
# Book     : the real table = BookBase + id
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


class BookBase(SQLModel):
    title: NonBlankStr = Field(max_length=100)
    author: NonBlankStr = Field(max_length=50)
    price: float = Field(gt=0)
    page: int = Field(default=0, ge=0)


class Book(BookBase, table=True):
    id: int | None = Field(default=None, primary_key=True)  # the DB makes the id


# --- Step 4d: a model for what we RETURN --------------------------------------
# Fields come out in declared order: title, author, price, page, then id.
# Plain types on purpose: the input rules (NonBlankStr) are for what clients
# SEND. If old rows in the table break those rules, reading them must not fail.
class BookPublic(SQLModel):
    title: str
    author: str
    price: float
    page: int
    id: int


# --- Step 6a: a model for PATCH -----------------------------------------------
# Every field is optional: the client sends ONLY what it wants to change.
class BookUpdate(SQLModel):
    title: NonBlankStr | None = Field(default=None, max_length=100)
    author: NonBlankStr | None = Field(default=None, max_length=50)
    price: float | None = Field(default=None, gt=0)
    page: int | None = Field(default=None, ge=0)


# --- Step 3c: create the tables when the app starts ---------------------------
# Runs once at startup. Creates the "book" table if it does not exist yet.
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="Lesson 10 - Database", lifespan=lifespan)


# --- Step 4b: a session per request -------------------------------------------
# A Session is your "conversation" with the database: add rows, commit.
# Same yield pattern as Lesson 8: open before the route, close after it.
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# --- Step 4c: CREATE -> POST /books -------------------------------------------
@app.post("/books", response_model=BookPublic, status_code=201)
def create_book(book: BookBase, session: SessionDep):
    # --- Step 2: refuse duplicates (same title + same author) ---
    # Look for an existing row first. 409 = "clashes with something that exists".
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


# --- Step 5a: READ all -> GET /books ------------------------------------------
# select(Book) = "SELECT * FROM book". offset/limit give us pagination
# (the skip/limit idea from Lesson 8), done by the DATABASE this time.
@app.get("/books", response_model=list[BookPublic])
def list_books(
    session: SessionDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=50),
):
    statement = select(Book).order_by(Book.id).offset(skip).limit(limit)
    return session.exec(statement).all()


# --- Step 5b: READ one -> GET /books/{id} -------------------------------------
# session.get(Book, id) looks a row up by its primary key.
# It returns None when there is no such row -> we answer 404 (Lesson 7).
@app.get("/books/{book_id}", response_model=BookPublic)
def get_book(book_id: int, session: SessionDep):
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


# --- Step 6b: UPDATE (replace) -> PUT /books/{id} -----------------------------
# PUT = send the WHOLE book again; every field is required (BookBase).
# sqlmodel_update copies the new values onto the row we loaded.
@app.put("/books/{book_id}", response_model=BookPublic)
def replace_book(book_id: int, book: BookBase, session: SessionDep):
    db_book = session.get(Book, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db_book.sqlmodel_update(book.model_dump())
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book



# --- Step 6c: UPDATE (partial) -> PATCH /books/{id} ---------------------------
# PATCH = send ONLY the fields to change. exclude_unset=True drops the
# fields the client did not send, so they keep their old values.
@app.patch("/books/{book_id}", response_model=BookPublic)
def update_book(book_id: int, changes: BookUpdate, session: SessionDep):
    db_book = session.get(Book, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db_book.sqlmodel_update(changes.model_dump(exclude_unset=True))
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


# --- Step 7: DELETE -> DELETE /books/{id} -------------------------------------
# Load the row, then session.delete() + commit removes it from the table.
# We return a message with 200 so the client can SEE what happened.
# (The strict REST convention is 204 with an empty body; both are fine.)
@app.delete("/books/{book_id}")
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
