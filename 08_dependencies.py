"""
FASTAPI TUTORIAL - Lesson 8: dependencies (Depends)

Some logic is needed in MANY routes: pagination, an API-key check,
a database session. Write it once as a function, and let FastAPI run it
BEFORE your route with Depends().

Run:  uv run fastapi dev 08_dependencies.py
"""

from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query

app = FastAPI(title="Lesson 8 - Dependencies")

items_db = [{"id": i, "name": f"item-{i}"} for i in range(1, 21)]  # 20 items


# --- Step 1: a simple dependency ----------------------------------------------
# A normal function. Its return value is handed to the route.
def get_greeting():
    return "Hello from a dependency"


@app.get("/greet")
def greet(message: Annotated[str, Depends(get_greeting)]):
    return {"message": message}


# --- Step 2: shared query parameters ------------------------------------------
# skip/limit are needed by every list endpoint. Define them ONCE here.
def pagination(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=6, ge=1, le=20),
):
    return {"skip": skip, "limit": limit}


Pagination = Annotated[dict, Depends(pagination)]  # a reusable shortcut


@app.get("/items")
def list_items(page: Pagination):
    return items_db[page["skip"] : page["skip"] + page["limit"]]


@app.get("/products")
def list_products(page: Pagination):  # same rules, zero repeated code
    return {"page": page, "products": ["pen", "book", "bag"]}


# --- Step 3: a dependency that can reject the request -------------------------
# Reads the X-API-Key header. Wrong or missing key -> 401, route never runs.
def verify_api_key(x_api_key: Annotated[str | None, Header()] = None):
    if x_api_key != "secret-key-123":
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/secure-data", dependencies=[Depends(verify_api_key)])
def secure_data():
    return {"data": "only for people with the key"}


# --- Step 4: a dependency that depends on another dependency ------------------
# get_current_user needs the key check to pass first, then returns the user.
def get_current_user(x_api_key: Annotated[str | None, Header()] = None):
    verify_api_key(x_api_key)
    return {"username": "mani", "role": "admin"}


CurrentUser = Annotated[dict, Depends(get_current_user)]


@app.get("/me")
def read_me(user: CurrentUser):
    return user


# --- Step 5: yield = setup, then cleanup --------------------------------------
# Code before `yield` runs before the route, code after runs AFTER the
# response. Lesson 10 uses this for opening/closing database sessions.
def get_db():
    print("DB opened")
    dbs = {"connected": True}
    try:
        yield dbs
    finally:
        print("DB closed")


@app.get("/db-status")
def db_status(db: Annotated[dict, Depends(get_db)]):
    return db


# --- Step 6: protect a whole group of routes at once --------------------------
# One Depends on the app/router guards every route inside it. (Routers are
# covered properly in Lesson 11.)
from fastapi import APIRouter  # noqa: E402

admin = APIRouter(prefix="/admin", dependencies=[Depends(verify_api_key)])


@admin.get("/stats")
def admin_stats():
    return {"users": 42}


@admin.get("/logs")
def admin_logs():
    return {"logs": ["started", "running", "stopped"]}


app.include_router(admin)
