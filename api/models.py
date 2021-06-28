from pydantic import BaseModel


class RequestData(BaseModel):
    pass


class Task(BaseModel):
    task_id: str
    status: str


class Result(BaseModel):
    task_id: str
    status: str
