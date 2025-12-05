# Схемы (Pydantic модели) для задач
from typing import Optional
from pydantic import BaseModel

class TaskBase(BaseModel):
    """Базовая схема для задачи"""
    name: str
    description: Optional[str] = None
    needed_hours: Optional[int] = None
    status: Optional[str] = "Новая"
    priority: Optional[str] = "Низкий"
    employee_id: Optional[int] = None
    project_id: int

class TaskCreate(TaskBase):
    """Схема для создания новой задачи"""
    pass

class TaskUpdate(BaseModel):
    """Схема для обновления задачи"""
    name: Optional[str] = None
    description: Optional[str] = None
    needed_hours: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    employee_id: Optional[int] = None
    project_id: Optional[int] = None

class Task(TaskBase):
    """Схема для возврата информации о задаче"""
    id: int
    class Config:
        from_attributes = True

class TaskWithDetails(Task):
    """Схема задачи с дополнительными деталями"""
    employee_name: Optional[str] = None
    project_name: Optional[str] = None