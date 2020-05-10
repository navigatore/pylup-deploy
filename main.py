from fastapi import FastAPI, HTTPException, status, Depends, Cookie, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates

from hashlib import sha256
import secrets
import sqlite3

app = FastAPI()
app.mydata = {}
app.mydata["secret_key"] = "Lorem Ipsum Dolor Sit Amet"
app.mydata[
    "allowed_token"
] = "c10b55dfdeddfc4718d210214d13277ed4555ce77857e688eeaa49412074c3b8"
app.mydata["patients"] = {}

templates = Jinja2Templates(directory="templates")
security = HTTPBasic()


class MethodResp(BaseModel):
    method: str


class PatientName(BaseModel):
    name: str
    surname: str


class PatientResp(BaseModel):
    id: int
    patient: PatientName


def checkAuthorization(session_token: str):
    if session_token != app.mydata["allowed_token"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("chinook.db")


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/tracks")
async def tracks(page: int = 0, per_page: int = 10):
    app.db_connection.row_factory = sqlite3.Row
    return app.db_connection.execute(
        "SELECT * FROM tracks LIMIT ? OFFSET ?", (per_page, page * per_page)
    ).fetchall()


@app.post("/logout")
def logout(*, session_token: str = Cookie(None)):
    checkAuthorization(session_token)
    response = RedirectResponse("/", 302)
    response.delete_cookie(key="session_token")
    return response


@app.post("/login")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "trudnY")
    correct_password = secrets.compare_digest(credentials.password, "PaC13Nt")

    if not correct_username or not correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    session_token = sha256(
        bytes(
            f"{credentials.username}{credentials.password}{app.mydata['secret_key']}",
            "utf8",
        )
    ).hexdigest()
    response: RedirectResponse = RedirectResponse("/welcome", 302)
    response.set_cookie(key="session_token", value=session_token)
    return response


@app.get("/")
def hello_world():
    return {"message": "Hello World during the coronavirus pandemic!"}


@app.get("/welcome")
def welcome(*, session_token: str = Cookie(None), request: Request):
    checkAuthorization(session_token)
    return templates.TemplateResponse(
        "welcome.html", {"request": request, "user": "trudnY"}
    )


@app.get("/method")
def method_get():
    return MethodResp(method="GET")


@app.post("/method")
def method_post():
    return MethodResp(method="POST")


@app.delete("/method")
def method_delete():
    return MethodResp(method="DELETE")


@app.put("/method")
def method_put():
    return MethodResp(method="PUT")


@app.post("/patient")
def patient(patient_name: PatientName, session_token: str = Cookie(None)):
    checkAuthorization(session_token)
    new_id = len(app.mydata["patients"])
    app.mydata["patients"][new_id] = patient_name
    response = RedirectResponse(f"/patient/{new_id}", status_code=status.HTTP_302_FOUND)
    return response


@app.get("/patient")
def get_all_patients(session_token: str = Cookie(None)):
    checkAuthorization(session_token)
    if not app.mydata["patients"]:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    return app.mydata["patients"]


@app.get("/patient/{pk}")
def get_patient(pk: int, session_token: str = Cookie(None)):
    checkAuthorization(session_token)
    if pk not in app.mydata["patients"]:
        raise HTTPException(status_code=204, detail="Nonexisting patient ID")
    return app.mydata["patients"][pk]


@app.delete("/patient/{pk}")
def delete_patient(pk: int, response: Response, session_token: str = Cookie(None)):
    checkAuthorization(session_token)
    if pk in app.mydata["patients"]:
        del app.mydata["patients"][pk]
    response.status_code = status.HTTP_204_NO_CONTENT
    response.headers["Location"] = f"/patient/{pk}"
    return response
