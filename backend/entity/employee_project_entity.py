# Модель для связи многие-ко-многим между сотрудниками и проектами.
from sqlalchemy import Column, Integer
from db_connect.db import Base

# Реализует отношение многие-ко-многим между таблицами Employee и Project.
# Каждая запись связывает одного сотрудника с одним проектом.
class EmployeeProject(Base):
    __tablename__ = "employee_project"

    employee_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, primary_key=True)

# Метод для строкового представления объекта
    def __repr__(self):
        return f"<EmployeeProject(employee_id={self.employee_id}, project_id={self.project_id})>"