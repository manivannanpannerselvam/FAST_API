"""
FASTAPI TUTORIAL - Lesson 2: path parameters

Part of the URL can be a variable. Put it in {braces} in the path, and give
the function an argument with the SAME name:

    @app.get("/users/{user_id}")
    def get_user(user_id: int): ...

    GET /users/42   ->  get_user(user_id=42)

The type hint (`int`) is not decoration - FastAPI uses it to:
    1. CONVERT  the text "42" from the URL into the int 42
    2. VALIDATE it - GET /users/abc returns a 422 error explaining why
    3. DOCUMENT it in /docs

An Enum restricts a parameter to a fixed set of values.

ORDER MATTERS: FastAPI checks routes top to bottom. /users/me is declared
BEFORE /users/{user_id}, otherwise "me" would be matched as a user_id (and
fail int validation).

TRY IT:
  1. GET /users/42        then  /users/abc   (read the 422 error body)
  2. GET /users/me
  3. GET /models/resnet   then  /models/gpt  (not in the Enum -> 422)
  4. GET /files/home/notes/todo.txt   (the :path converter keeps the slashes)
  5. Move the /users/me function below /users/{user_id} and see what breaks.

Run:  uv run fastapi dev 02_path_params.py
"""

from enum import Enum

from fastapi import FastAPI

app = FastAPI(title="Lesson 2 - Path Parameters")


@app.get("/users/me")
def get_current_user():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "type": type(user_id).__name__}


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/models/{model_name}")
def get_model(model_name: ModelName):
    # model_name is an Enum member, so you can compare against members.
    if model_name is ModelName.resnet:
        return {"model": model_name, "note": "Deep residual learning!"}
    return {"model": model_name, "note": "A classic CNN"}


# `{file_path:path}` lets the parameter contain "/" characters.
@app.get("/files/{file_path:path}")
def read_file(file_path: str):
    return {"file_path": file_path}
