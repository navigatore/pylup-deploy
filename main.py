from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class MethodResp(BaseModel):
    method: str


class PatientName(BaseModel):
    name: str
    surename: str


class PatientResp(BaseModel):
    id: int
    patient: PatientName


@app.get('/')
def hello_world():
    return {"message": "Hello World during the coronavirus pandemic!"}


@app.get('/method')
def method_get():
    return MethodResp(method="GET")


@app.post('/method')
def method_post():
    return MethodResp(method="POST")


@app.delete('/method')
def method_delete():
    return MethodResp(method="DELETE")


@app.put('/method')
def method_put():
    return MethodResp(method="PUT")


@app.post('/patient')
def patient(patient_name: PatientName):
    patient.ctr += 1
    return PatientResp(id=patient.ctr, patient=patient_name)


patient.ctr = -1
