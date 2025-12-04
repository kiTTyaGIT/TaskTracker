# Модель задачи для системы управления задачами
from sqlalchemy import Column, Integer, Text
from db_connect.db import Base

class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    needed_hours = Column(Integer)
    status = Column(Text)
    priority = Column(Text)
    employee_id = Column(Integer)
    project_id = Column(Integer, nullable=False)

# Метод для строкового представления объекта
    def __repr__(self):
        return f"<Task(id={self.id}, name='{self.name}', status='{self.status}', priority='{self.priority}')>"