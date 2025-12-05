# Схемы (Pydantic модели) для сотрудников
from typing import Optional

from pydantic import BaseModel


class EmployeeBase(BaseModel):
    """Базовая схема для сотрудника"""
    name: str
    surname: str
    patronymic: Optional[str] = None
    phone_number: Optional[str] = None
    mail: Optional[str] = None
    role: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    """Схема для создания нового сотрудника"""
    pass


class EmployeeUpdate(BaseModel):
    """Схема для обновления сотрудника"""
    name: Optional[str] = None
    surname: Optional[str] = None
    patronymic: Optional[str] = None
    phone_number: Optional[str] = None
    mail: Optional[str] = None
    role: Optional[str] = None


class Employee(EmployeeBase):
    """Схема для возврата информации о сотруднике"""
    id: int
    class Config:
        from_attributes = True