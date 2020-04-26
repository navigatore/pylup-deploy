from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from hashlib import sha256
import secrets

app = FastAPI()
app.secret_key = "Lorem Ipsum Dolor Sit Amet"

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
@app.get("/welcome")
def hello_world():
    return {"message": "Hello World during the coronavirus pandemic!"}


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
