from fastapi import FastAPI, HTTPException, status, Depends, Cookie, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates

from hashlib import sha256
import secrets

app = FastAPI()
app.secret_key = "Lorem Ipsum Dolor Sit Amet"
app.allowed_token = "c10b55dfdeddfc4718d210214d13277ed4555ce77857e688eeaa49412074c3b8"

templates = Jinja2Templates(directory="templates")

patients = {}


class MethodResp(BaseModel):
    method: str


class PatientName(BaseModel):
    name: str
    surename: str


class PatientResp(BaseModel):
    id: int
    patient: PatientName


security = HTTPBasic()


@app.post("/logout")
def logout(*, session_token: str = Cookie(None)):
    if session_token != app.allowed_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
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
        bytes(f"{credentials.username}{credentials.password}{app.secret_key}", "utf8")
    ).hexdigest()
    response: RedirectResponse = RedirectResponse("/welcome", 302)
    response.set_cookie(key="session_token", value=session_token)
    return response


@app.get("/")
def hello_world():
    return {"message": "Hello World during the coronavirus pandemic!"}


@app.get("/welcome")
def welcome(*, session_token: str = Cookie(None), request: Request):
    if session_token != app.allowed_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
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
def patient(patient_name: PatientName):
    new_id = len(patients)
    patients[new_id] = patient_name
    return PatientResp(id=new_id, patient=patient_name)


@app.get("/patient/{pk}")
def get_patient(pk: int):
    if pk not in patients:
        raise HTTPException(status_code=204, detail="Nonexisting patient ID")
    return patients[pk]
