from fastapi import FastAPI
from uuid import UUID
from pydantic.main import BaseModel
from fetchsys import SystemDescription
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from fastapi import Body, FastAPI, Form, Request

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


@app.post("/tasks", status_code=201)
def run_task(payload = Body(...)):
    task_type = payload["type"]
    task = create_task.delay(int(task_type))
    return JSONResponse({"task_id": task.id})


@app.get("/tasks/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)