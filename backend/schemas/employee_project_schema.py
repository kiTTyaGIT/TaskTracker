from typing import Optional, List
from pydantic import BaseModel

class EmployeeProjectBase(BaseModel):
    employee_id: int
    project_id: int

class EmployeeProjectCreate(EmployeeProjectBase):
    pass

class EmployeeProjectResponse(EmployeeProjectBase):
    class Config:
        from_attributes = True

class EmployeeShort(BaseModel):
    id: int
    name: str
    surname: str
    patronymic: Optional[str] = None

class ProjectShort(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

class ProjectWithEmployees(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    employees: List[EmployeeShort] = []

class EmployeeWithProjects(BaseModel):
    id: int
    name: str
    surname: str
    patronymic: Optional[str] = None
    projects: List[ProjectShort] = []