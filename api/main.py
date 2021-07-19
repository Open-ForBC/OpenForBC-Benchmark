from fastapi import FastAPI
from uuid import UUID
from pydantic.main import BaseModel
from fetchsys import SystemDescription

app = FastAPI()
Inapp = SystemDescription()


@app.put("/")
def home():
    return "hello! Welcome to the Benchmarking Tool!"


@app.put("/gpu/{gpu_id}")
def give_gpu_info(gpu_id: int):
    return Inapp.get_gpu_info(gpuid=gpu_id)


@app.put("/sys/")
def give_sys_info():
    return Inapp.get_system_info()
