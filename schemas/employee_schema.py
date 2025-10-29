from typing import Optional

from pydantic import BaseModel


class EmployeeBase(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str] = None
    phone_number: Optional[str] = None
    mail: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    patronymic: Optional[str] = None
    phone_number: Optional[str] = None
    mail: Optional[str] = None


class Employee(EmployeeBase):
    id: int

    class Config:
        from_attributes = True