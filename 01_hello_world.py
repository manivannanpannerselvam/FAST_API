"""
FASTAPI TUTORIAL - Lesson 1: your first API

An API is a program that listens for HTTP requests and answers them, usually
with JSON. FastAPI lets you write one with plain Python functions:

    @app.get("/")          <- "when a GET request arrives for the path /"
    def root():            <- "...run this function"
        return {...}       <- "...and send this dict back as JSON"

The decorator pairs an HTTP METHOD with a PATH. The four methods you'll use
most are:

    GET     read something          POST    create something
    PUT     replace/update          DELETE  remove something

FastAPI doesn't serve requests by itself - a web server called Uvicorn does.
`fastapi dev` starts Uvicorn for you, and reloads it whenever you save.

TRY IT:
  1. Run the server (command below), then open http://127.0.0.1:8000
  2. Open http://127.0.0.1:8000/docs - interactive docs FastAPI generated for
     you from the code. Click an endpoint -> "Try it out" -> "Execute".
  3. Open http://127.0.0.1:8000/hello - then add a new endpoint below,
     e.g. GET /about, save the file, and refresh /docs. It appears instantly.
  4. From a terminal:  curl http://127.0.0.1:8000/hello

Run:  uv run fastapi dev 01_hello_world.py
"""

from fastapi import FastAPI

# The app object. Every endpoint gets registered on it.
app = FastAPI(title="Lesson 1 - Hello World")


@app.get("/")
def root():
    # Dicts, lists, strings, numbers, bools, None -> all become JSON.
    return {"message": "Hello, FastAPI!"}


@app.get("/hello")
def hello():
    return {"greeting": "Hi there", "lesson": 1, "topics": ["routes", "JSON", "docs"]}


@app.get("/welcome")
def welcome():
    return {"greeting": "Hi there", "lesson": 2, "topics": ["test1", "test2", "docs"]}
