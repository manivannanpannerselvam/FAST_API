# FastAPI Learning Project

URLs and request payloads for every lesson, so you can run and test them later.

**Base URL:** `http://127.0.0.1:8000`  |  **Swagger UI (try requests in the browser):** `http://127.0.0.1:8000/docs`

**Setup (one time):** `uv sync`

**Run a lesson (one at a time, they all use port 8000):** `uv run fastapi dev <file>.py`

**Notes**
- `GET` and `DELETE` have no payload.
- For `POST`, `PUT` and `PATCH`, send the payload as JSON with header `Content-Type: application/json`.
- Lessons 4, 6, 7 and 9 keep data in memory. It is lost whenever the server reloads, so create the data again with POST.
- Lessons 10 and 11 need PostgreSQL running and a database named `bookdb` (`createdb -h localhost bookdb`).

---

## Lesson 1 - Hello world
Run: `uv run fastapi dev 01_hello_world.py`

```
GET http://127.0.0.1:8000/
GET http://127.0.0.1:8000/hello
GET http://127.0.0.1:8000/welcome
```

---

## Lesson 2 - Path parameters
Run: `uv run fastapi dev 02_path_params.py`

```
GET http://127.0.0.1:8000/users/me
GET http://127.0.0.1:8000/users/42
GET http://127.0.0.1:8000/users/abc                       (422 error: not a number)
GET http://127.0.0.1:8000/models/resnet                   (allowed: alexnet, resnet, lenet)
GET http://127.0.0.1:8000/models/gpt                      (422 error: not allowed)
GET http://127.0.0.1:8000/files/home/notes/todo.txt
```

---

## Lesson 3 - Query parameters
Run: `uv run fastapi dev 03_query_params.py`

```
GET http://127.0.0.1:8000/items
GET http://127.0.0.1:8000/items?skip=2&limit=2
GET http://127.0.0.1:8000/search?q=pen
GET http://127.0.0.1:8000/search?q=pen&in_stock=yes&max_price=5.5
GET http://127.0.0.1:8000/search                          (422 error: q is required)
GET http://127.0.0.1:8000/filter?tag=red&tag=small
GET http://127.0.0.1:8000/users/7/items/3?detail=true
GET http://127.0.0.1:8000/jobs
GET http://127.0.0.1:8000/jobs?location=Chennai
GET http://127.0.0.1:8000/jobs?skill=sql
GET http://127.0.0.1:8000/jobs?skill=python&skill=fastapi&location=Chennai
```

---

## Lesson 4 - Request body
Run: `uv run fastapi dev 04_request_body.py`

**Create an item**
```
POST http://127.0.0.1:8000/items
```
```json
{
  "name": "Pen",
  "price": 1.5,
  "description": "blue pen",
  "tax": 0.1,
  "tags": ["red"]
}
```
Only `name` and `price` are required.

**Read items**
```
GET http://127.0.0.1:8000/items
GET http://127.0.0.1:8000/items/1
```

**Replace an item** (path + query + body)
```
PUT http://127.0.0.1:8000/items/1?notify=true
```
```json
{
  "name": "Pen v2",
  "price": 2
}
```

**Create an order**
```
POST http://127.0.0.1:8000/orders
```
```json
{
  "seller": { "name": "Asha", "email": "asha@example.com" },
  "items": [
    { "name": "Pen", "price": 1.5 },
    { "name": "Book", "price": 10 }
  ]
}
```

**Read orders**
```
GET http://127.0.0.1:8000/orders
GET http://127.0.0.1:8000/orders/1
```

---

## Lesson 5 - Validation
Run: `uv run fastapi dev 05_validation.py`

**Create an item**
```
POST http://127.0.0.1:8000/items
```
```json
{
  "name": "Pen",
  "price": 10.5,
  "tax": 0.18
}
```
Rules: `name` 2-20 characters, `price` greater than 0, `tax` optional (0 or more, less than 1).

**Search**
```
GET http://127.0.0.1:8000/search?q=pen&limit=5
```
Rules: `q` is required (2-20 characters), `limit` is 1-50 (default 10).

---

## Lesson 6 - Response models
Run: `uv run fastapi dev 06_response_models.py`

**Create a user** (the password is never returned)
```
POST http://127.0.0.1:8000/users
POST http://127.0.0.1:8000/users-created          (same, but returns status 201)
```
```json
{
  "username": "mani",
  "email": "mani@example.com",
  "password": "secret123"
}
```

**Read users**
```
GET http://127.0.0.1:8000/users
GET http://127.0.0.1:8000/users/mani
```

---

## Lesson 7 - Error handling
Run: `uv run fastapi dev 07_error_handling.py`

**Create a user** (send it twice to see the 409 error)
```
POST http://127.0.0.1:8000/users
```
```json
{
  "username": "mani",
  "email": "mani@example.com",
  "password": "secret123"
}
```

**Other requests** (no payload)
```
GET    http://127.0.0.1:8000/users/mani
GET    http://127.0.0.1:8000/users/bob                           (404 error)
POST   http://127.0.0.1:8000/users/mani/email?email=new@example.com
POST   http://127.0.0.1:8000/users/mani/email?email=bad          (400 error)
DELETE http://127.0.0.1:8000/users/mani
GET    http://127.0.0.1:8000/ask?calls_made=1
GET    http://127.0.0.1:8000/ask?calls_made=3                    (429 error)
```

---

## Lesson 8 - Dependencies
Run: `uv run fastapi dev 08_dependencies.py`

All requests are GET, with no payload.

```
GET http://127.0.0.1:8000/greet
GET http://127.0.0.1:8000/items
GET http://127.0.0.1:8000/items?skip=3&limit=2
GET http://127.0.0.1:8000/products?limit=1
GET http://127.0.0.1:8000/db-status
```

**These need a header:** `X-API-Key: secret-key-123` (without it you get a 401 error)
```
GET http://127.0.0.1:8000/secure-data
GET http://127.0.0.1:8000/me
GET http://127.0.0.1:8000/admin/stats
GET http://127.0.0.1:8000/admin/logs
```
```bash
curl http://127.0.0.1:8000/secure-data -H "X-API-Key: secret-key-123"
```

---

## Lesson 9 - CRUD (in memory)
Run: `uv run fastapi dev 09_crud_api.py`

**Create a book**
```
POST http://127.0.0.1:8000/books
```
```json
{
  "title": "Clean Code",
  "author": "Robert Martin",
  "price": 30
}
```

**Read books**
```
GET http://127.0.0.1:8000/books
GET http://127.0.0.1:8000/books?skip=0&limit=10
GET http://127.0.0.1:8000/books/1
```

**Replace a book** (PUT needs all fields)
```
PUT http://127.0.0.1:8000/books/1
```
```json
{
  "title": "Clean Code 2nd Edition",
  "author": "Robert Martin",
  "price": 35
}
```

**Change part of a book** (PATCH needs only the fields to change)
```
PATCH http://127.0.0.1:8000/books/1
```
```json
{
  "price": 25
}
```

**Delete a book**
```
DELETE http://127.0.0.1:8000/books/1
```

---

## Lesson 10 - PostgreSQL (single file)
Run: `uv run fastapi dev 10_database.py`

Data is saved in PostgreSQL, so it survives restarts.

**Create a book**
```
POST http://127.0.0.1:8000/books
```
```json
{
  "title": "Clean Code",
  "author": "Robert Martin",
  "price": 30,
  "page": 464
}
```
`page` is optional (default 0).

**Read books**
```
GET http://127.0.0.1:8000/books
GET http://127.0.0.1:8000/books?skip=0&limit=10
GET http://127.0.0.1:8000/books/1
```

**Replace a book** (PUT needs title, author and price)
```
PUT http://127.0.0.1:8000/books/1
```
```json
{
  "title": "Clean Code 2nd Edition",
  "author": "Robert Martin",
  "price": 35,
  "page": 500
}
```

**Change part of a book** (any of title, author, price, page)
```
PATCH http://127.0.0.1:8000/books/1
```
```json
{
  "price": 25
}
```

**Delete a book** (permanent)
```
DELETE http://127.0.0.1:8000/books/1
```

**Rules**
- `title` and `author`: only letters, digits, spaces, `'` and `-`. Something like `"Bad ."` gives a 422 error. Spaces at the start and end are removed.
- Same title + same author twice gives a 409 error.
- `price` must be greater than 0.

---

## Lesson 11 - Routers (app folder)
Run: `uv run fastapi dev app/main.py` (from the project root, not from inside `app/`)

**Books:** the same URLs and payloads as Lesson 10.
Since Lesson 12, `POST`, `PUT`, `PATCH` and `DELETE` on `/books` also need the login token header (see Lesson 12).
`GET` requests stay open.

**Authors** (GET only, no payload)
```
GET http://127.0.0.1:8000/authors
GET http://127.0.0.1:8000/authors/Manivannan/books
GET http://127.0.0.1:8000/authors/Manivannan%20v1/books        (%20 means a space)
```
Author names must match exactly, including capital letters.

---

## Lesson 12 - Authentication (login and token)
Run: `uv run fastapi dev app/main.py` (same app as Lesson 11, now with users and login)

Flow: **1. register once, 2. login to get a token, 3. send the token on every protected request.**
The token is valid for 30 minutes. After that you get a 401 error, so login again.

**Step 1: Register a user (once)**
```
POST http://127.0.0.1:8000/auth/register
```
Header:
```
Content-Type: application/json
```
Payload:
```json
{
  "username": "mani",
  "password": "secret123"
}
```
- `username`: 3-20 characters, letters, digits and `_` only.
- `password`: 6-72 characters.
- Registering the same username again gives a 409 error.

**Step 2: Login to get the token**
```
POST http://127.0.0.1:8000/auth/login
```
Header:
```
Content-Type: application/x-www-form-urlencoded
```
Payload (form fields, **not JSON**; in Postman choose Body, then x-www-form-urlencoded):
```
username=mani
password=secret123
```
Response:
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```
```bash
curl -X POST http://127.0.0.1:8000/auth/login -d "username=mani&password=secret123"
```
A wrong username or password gives a 401 error.

**Step 3: Use the token on protected requests**

These need the header below: `POST`, `PUT`, `PATCH` and `DELETE` on `/books`.
`GET` requests need no header.
```
Authorization: Bearer eyJhbGciOi...
```
In Postman: Authorization tab, Type **Bearer Token**, paste only the token (without the word `Bearer`).

Example, create a book:
```
POST http://127.0.0.1:8000/books
```
Headers:
```
Authorization: Bearer eyJhbGciOi...
Content-Type: application/json
```
Payload:
```json
{
  "title": "Clean Code",
  "author": "Robert Martin",
  "price": 30,
  "page": 464
}
```

Example, replace a book:
```
PUT http://127.0.0.1:8000/books/4
```
Headers: `Authorization: Bearer <token>` and `Content-Type: application/json`
```json
{
  "title": "FAST API tutorial v2 put",
  "author": "Manivannan v2",
  "price": 35,
  "page": 501
}
```

Example, change part of a book:
```
PATCH http://127.0.0.1:8000/books/4
```
Headers: `Authorization: Bearer <token>` and `Content-Type: application/json`
```json
{
  "price": 25
}
```

Example, delete a book (no payload):
```
DELETE http://127.0.0.1:8000/books/4
```
Header: `Authorization: Bearer <token>`

**Errors**

| You see | Reason |
|---|---|
| `401 Not authenticated` | no `Authorization` header on a protected request |
| `401 Could not validate credentials` | token is wrong, edited or expired. Login again |
| `422` on login | you sent JSON. Send form fields instead |

**Postman tip: save the token automatically.** In the Login request, open the Scripts tab (Tests in older Postman) and add:
```javascript
pm.environment.set("token", pm.response.json().access_token);
```
Then in other requests use Bearer Token with the value `{{token}}`. Select an environment in Postman (top right).

**Secret key:** tokens are signed with `SECRET_KEY`. The code has a learning-only default.
On a real server set your own: `SECRET_KEY=$(openssl rand -hex 32)`.

---

## Project layout
```
Fast_API/
├── 01_hello_world.py ... 10_database.py     lessons 1-10
├── app/                                     lessons 11-12
│   ├── main.py            creates the app and plugs in the routers
│   ├── database.py        connection and session
│   ├── models.py          tables and request/response models
│   ├── security.py        password hashing and tokens
│   ├── dependencies.py    get_current_user (the login check)
│   └── routers/
│       ├── books.py       /books endpoints
│       ├── authors.py     /authors endpoints
│       └── auth.py        /auth/register and /auth/login
├── pyproject.toml / uv.lock
└── README.md
```
