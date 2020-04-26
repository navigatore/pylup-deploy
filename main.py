from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

patients = {}


class MethodResp(BaseModel):
    method: str


class PatientName(BaseModel):
    name: str
    surename: str


class PatientResp(BaseModel):
    id: int
    patient: PatientName


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
