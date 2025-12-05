# Схемы (Pydantic модели) для проектов
from datetime import date
from typing import Optional

from pydantic import BaseModel


class ProjectBase(BaseModel):
    """Базовая схема для проекта"""
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    finish_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    """Схема для создания нового проекта"""
    pass


class ProjectUpdate(BaseModel):
    """Схема для обновления проекта"""
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    finish_date: Optional[date] = None


class Project(ProjectBase):
    """Схема для возврата информации о проекте"""
    id: int
    class Config:
        from_attributes = True