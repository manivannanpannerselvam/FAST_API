"""
FASTAPI TUTORIAL - Lesson 3: query parameters

Query parameters come after the "?" in a URL, joined by "&":

    GET /items?skip=0&limit=10

RULE: any function argument that is NOT in the path is a query parameter.

    def list_items(skip: int = 0, limit: int = 10)
                   ^ has a default -> optional
    def search(q: str)
               ^ no default      -> REQUIRED (missing -> 422 error)
    def search(q: str | None = None)
               ^ None default    -> optional, may be absent

`bool` is forgiving: ?active=true, =1, =yes, =on all mean True.

To accept the same parameter several times (?tag=a&tag=b) use `list[str]`
with Query() - otherwise FastAPI would treat a list as a request body.

TRY IT:
  1. GET /items                      (defaults kick in)
  2. GET /items?skip=2&limit=2
  3. GET /search                     (q is required -> 422)
  4. GET /search?q=pen&in_stock=yes
  5. GET /filter?tag=red&tag=small
  6. GET /users/7/items/3?detail=true  (path + query params together)
  7. GET /jobs?skill=python&skill=fastapi&skill=sql&location=Chennai
     then /jobs?location=Chennai,  /jobs?skill=sql,  /jobs

Run:  uv run fastapi dev 03_query_params.py
"""

from fastapi import FastAPI, Query

app = FastAPI(title="Lesson 3 - Query Parameters")

FAKE_ITEMS = [{"name": n} for n in ["pen", "book", "lamp", "mug", "desk", "chair"]]


@app.get("/items")
def list_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit, "items": FAKE_ITEMS[skip : skip + limit]}


@app.get("/search")
def search(q: str, in_stock: bool = False, max_price: float | None = None):
    # Same as the one-liner: [item for item in FAKE_ITEMS if q.lower() in item["name"]]
    results = []
    for item in FAKE_ITEMS:
        if q.lower() in item["name"]:
            results.append(item)

    return {"q": q, "in_stock": in_stock, "max_price": max_price, "results": results}


@app.get("/filter")
def filter_by_tags(tag: list[str] = Query(default=[])):
    return {"tags": tag}



# --- a realistic example: job search with a list param + an optional param ---
# FastAPI only hands us `skill` and `location`. WHERE we search is up to us -
# here a Python list; in Lesson 11 a real database.
JOBS = [
    {"title": "Backend Developer", "skills": ["python", "fastapi"], "location": "Chennai"},
    {"title": "Data Analyst",      "skills": ["sql", "excel"],      "location": "Bangalore"},
    {"title": "ML Engineer",       "skills": ["python", "pytorch"], "location": "Chennai"},
    {"title": "Java Developer",    "skills": ["java", "spring"],    "location": "Chennai"},
]


@app.get("/jobs")
def search_jobs(skill: list[str] = Query(default=[]), location: str | None = None):
    results = []
    for job in JOBS:
        # 1. location filter (only if the user gave one)
        if location is not None and job["location"].lower() != location.lower():
            continue  # wrong city, skip this job

        # 2. skill filter: keep the job if it needs ANY of the requested skills
        if skill:
            matched = False
            for s in skill:
                if s.lower() in job["skills"]:
                    matched = True
            if not matched:
                continue  # no matching skill, skip this job

        results.append(job)

    return {"skill": skill, "location": location, "count": len(results), "results": results}



@app.get("/users/{user_id}/items/{item_id}")
def user_item(user_id: int, item_id: int, detail: bool = False):
    item = {"user_id": user_id, "item_id": item_id}
    if detail:
        item["description"] = "A long, detailed description of this item."
    return item
