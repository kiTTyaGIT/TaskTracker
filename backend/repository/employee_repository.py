# Слой доступа к данным сотрудников
from entity.employee_entity import Employee
from sqlalchemy import Boolean
from sqlalchemy.orm import Session


class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_employee(self, employee_data: dict) -> Employee:
        """Создание нового пользователя"""
        empl = Employee(**employee_data)
        self.db.add(empl)
        self.db.commit()
        self.db.refresh(empl)
        return empl

    def get_all_employees(self, skip: int = 0, limit: int = 100) -> list[type[Employee]]:
        """Получение всех сотрудников"""
        return self.db.query(Employee).offset(skip).limit(limit).all()

    def get_employee_by_id(self, employee_id: int) -> Employee:
        """Получение сотрудника по ID"""
        return self.db.query(Employee).filter(Employee.id == employee_id).first()

    def delete_employee_by_id(self, employee_id: int) -> bool:
        """Удаление сотрудника по ID"""
        employee = self.get_employee_by_id(employee_id)
        if not employee:
            return False

        self.db.delete(employee)
        self.db.commit()
        return True

    def update_employee(self, employee_id: int, update_data: dict) -> Employee:
        """Обновление информации сотрудника"""
        employee = self.get_employee_by_id(employee_id)
        if not employee:
            return None

        for field, value in update_data.items():
            if hasattr(employee, field):
                setattr(employee, field, value)

        self.db.commit()
        self.db.refresh(employee)
        return employee

    def is_employee_exists(self, employee_id: int) -> Boolean:
        """Проверка существования сотрудника"""
        return self.db.query(Employee).filter(Employee.id == employee_id).first()
