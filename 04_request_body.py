"""
FASTAPI TUTORIAL - Lesson 4: request bodies with Pydantic models

When a client SENDS data (POST/PUT), it goes in the request BODY as JSON,
not in the URL. You describe the expected shape with a Pydantic model:

    class Item(BaseModel):
        name: str                       <- required
        price: float                    <- required
        description: str | None = None  <- optional

    @app.post("/items")
    def create_item(item: Item): ...

How FastAPI decides where each argument comes from:

    in the path ({item_id})      -> path parameter
    a simple type (int, str...)  -> query parameter
    a Pydantic model             -> request body (JSON)

FastAPI reads the JSON, validates it against the model, and hands you a real
Python object (item.name, item.price). Bad or missing fields -> 422 with an
exact explanation. Models can nest: `tags: list[str]`, `seller: Seller`.

TRY IT (easiest in /docs -> "Try it out"):
  1. POST /items with {"name": "Pen", "price": 1.5}
  2. Same, but "price": "cheap"        -> 422, read the "loc" and "msg"
  3. Same, but "price": "2.5"          -> works! Pydantic converts the string
  4. GET /items          -> every item you created so far
     GET /items/1        -> just item 1;  GET /items/99 -> 404 Not Found
  5. PUT /items/1?notify=true with a body - path + query + body in one call
  6. POST /orders with a nested seller and a list of items
     then GET /orders  and  GET /orders/1
  From curl:
     curl -X POST http://127.0.0.1:8000/items \
          -H "Content-Type: application/json" \
          -d '{"name": "Pen", "price": 1.5, "tax": 0.1}'

Run:  uv run fastapi dev 04_request_body.py
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Lesson 4 - Request Body")


class Item(BaseModel):
    name: str
    price: float
    description: str | None = None
    tax: float | None = None
    tags: list[str] = []


# Our "database" for now: a dict of {id: item data}. It lives in memory, so it
# is EMPTY again every time the server restarts (including auto-reload when
# you save this file). Lesson 11 replaces it with a real database.
ITEMS = {}
next_id = 1


@app.post("/items")
def create_item(item: Item):
    global next_id

    # `item` is a real object - attribute access, autocomplete, type-checked.
    data = item.model_dump()  # -> plain dict
    if item.tax is not None:
        data["price_with_tax"] = round(item.price * (1 + item.tax), 2)

    # Save it under a new id, so it can be fetched later with GET.
    data["id"] = next_id
    ITEMS[next_id] = data
    next_id = next_id + 1
    return data


@app.get("/items")
def list_items():
    # Every item saved so far, as a list.
    return list(ITEMS.values())


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in ITEMS:
        # Sends a proper "404 Not Found" response. Lesson 7 covers errors.
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return ITEMS[item_id]


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item, notify: bool = False):
    #             ^ path        ^ body      ^ query
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

    data = item.model_dump()
    data["id"] = item_id
    ITEMS[item_id] = data  # replace the old item with the new one
    return {"notify": notify, "item": data}


# --- nested models ----------------------------------------------------------
class Seller(BaseModel):
    name: str
    email: str


class Order(BaseModel):
    seller: Seller        # a model inside a model
    items: list[Item]     # a list of models


# Orders get their own in-memory store, just like ITEMS above.
ORDERS = {}
next_order_id = 1


@app.post("/orders")
def create_order(order: Order):
    global next_order_id

    total = 0
    for item in order.items:
        total = total + item.price

    # Save the full order (seller + items) plus the computed fields.
    data = order.model_dump()
    data["id"] = next_order_id
    data["item_count"] = len(order.items)
    data["total"] = total
    ORDERS[next_order_id] = data
    next_order_id = next_order_id + 1
    return data


@app.get("/orders")
def list_orders():
    return list(ORDERS.values())


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    if order_id not in ORDERS:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return ORDERS[order_id]
