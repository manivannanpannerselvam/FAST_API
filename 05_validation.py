"""
FASTAPI TUTORIAL - Lesson 5: validation rules

Types check the KIND of data ("price must be a number").
Validation rules check the VALUE ("price must be greater than 0").

Run:  uv run fastapi dev 05_validation.py
"""

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Lesson 5 - Validation")


# --- Step 1: a rule on one field ---------------------------------------------
class Item(BaseModel):
    # --- Step 2: rules on text ---
    name: str = Field(min_length=2, max_length=20)  # 2 to 20 characters
    price: float = Field(gt=0       )  # gt = "greater than" -> price must be > 0
    # --- Step 3: a range rule on an optional field ---
    tax: float | None = Field(default=None, ge=0, lt=1)  # 0 <= tax < 1, or missing


@app.post("/items")
def create_item(item: Item):
    return item


# --- Step 4: rules on query parameters ----------------------------------------
# Same rules as Field(), but for values in the URL:  /search?q=pen&limit=5
@app.get("/search")
def search(
    q: str = Query(min_length=2, max_length=20),  # required, 2-20 characters
    limit: int = Query(default=10, ge=1, le=50),  # optional, 1-50, default 10
):
    return {"q": q, "limit": limit}
