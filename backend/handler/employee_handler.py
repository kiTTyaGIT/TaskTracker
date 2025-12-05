#обертка над слоем репозитория сотрудника
from entity.employee_entity import Employee
from sqlalchemy import Boolean
from sqlalchemy.orm import Session
from repository.employee_repository import EmployeeRepository


class EmployeeHandler:
    def __init__(self, db: Session, employee_repository: EmployeeRepository):
        """конструктор сотрудников"""
        self.db = db
        self.employee_repository = employee_repository

    def create_employee(self, employee_data: dict) -> Employee:
        """Создание нового пользователя"""
        return self.employee_repository.create_employee(employee_data)

    def get_all_employees(self, skip: int = 0, limit: int = 100) -> list[type[Employee]]:
        """Получение всех сотрудников"""
        return self.employee_repository.get_all_employees(skip=skip, limit=limit)

    def get_employee_by_id(self, employee_id: int) -> Employee:
        """Получение сотрудника по ID"""
        return self.employee_repository.get_employee_by_id(employee_id)

    def delete_employee_by_id(self, employee_id: int) -> bool:
        """Удаление сотрудника по ID"""
        return self.employee_repository.delete_employee_by_id(employee_id)

    def update_employee(self, employee_id: int, update_data: dict) -> Employee:
        """Обновление информации сотрудника"""
        return self.employee_repository.update_employee(employee_id, update_data)

    def is_employee_exists(self, employee_id: int) -> Boolean:
        """Проверка существования сотрудника"""
        return self.employee_repository.is_employee_exists(employee_id)