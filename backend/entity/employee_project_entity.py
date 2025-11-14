from sqlalchemy import Column, Integer
from db_connect.db import Base

class EmployeeProject(Base):
    __tablename__ = "employee_project"

    employee_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f"<EmployeeProject(employee_id={self.employee_id}, project_id={self.project_id})>"