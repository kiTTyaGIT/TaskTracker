from typing import Optional
from pydantic import BaseModel

class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    needed_hours: Optional[int] = None
    status: Optional[str] = "новая"
    employee_id: Optional[int] = None
    project_id: int

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    needed_hours: Optional[int] = None
    status: Optional[str] = None
    employee_id: Optional[int] = None
    project_id: Optional[int] = None

class Task(TaskBase):
    id: int

    class Config:
        from_attributes = True

class TaskWithDetails(Task):
    employee_name: Optional[str] = None
    project_name: Optional[str] = None