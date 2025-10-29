from sqlalchemy import Column, Integer, Text
from db import Base

class Employee(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(Text)
    surname = Column(Text)
    patronymic = Column(Text)
    phone_number = Column(Text)
    mail = Column(Text)

    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.name}')>"