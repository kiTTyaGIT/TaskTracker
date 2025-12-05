# Схемы (Pydantic модели) для связей сотрудников и проектов
from typing import Optional, List
from pydantic import BaseModel

class EmployeeProjectBase(BaseModel):
    """Базовая схема для связи сотрудника и проекта"""
    employee_id: int
    project_id: int

class EmployeeProjectCreate(EmployeeProjectBase):
    """Схема для создания новой связи"""
    pass

class EmployeeProjectResponse(EmployeeProjectBase):
    """Схема для возврата информации о связи"""
    class Config:
        from_attributes = True

class EmployeeShort(BaseModel):
    """Сокращенная схема сотрудника"""
    id: int
    name: str
    surname: str
    patronymic: Optional[str] = None

class ProjectShort(BaseModel):
    """Сокращенная схема проекта"""
    id: int
    name: str
    description: Optional[str] = None

class ProjectWithEmployees(BaseModel):
    """Схема проекта со списком сотрудников"""
    id: int
    name: str
    description: Optional[str] = None
    employees: List[EmployeeShort] = []

class EmployeeWithProjects(BaseModel):
    """Схема сотрудника со списком проектов"""
    id: int
    name: str
    surname: str
    patronymic: Optional[str] = None
    projects: List[ProjectShort] = []