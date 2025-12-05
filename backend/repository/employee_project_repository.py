# Слой доступа к данным сотрудников-проектов
from sqlalchemy.orm import Session
from sqlalchemy import text
from entity.employee_project_entity import EmployeeProject

from repository.employee_repository import EmployeeRepository
from repository.project_repository import ProjectRepository


class EmployeeProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_employee_to_project(self, employee_id: int, project_id: int) -> bool:
        """Добавление сотрудника в проект"""
        # Проверяем, не существует ли уже такая связь
        existing = self.db.query(EmployeeProject).filter(
            EmployeeProject.employee_id == employee_id,
            EmployeeProject.project_id == project_id
        ).first()

        if existing:
            return False

        # Создаем новую связь
        association = EmployeeProject(
            employee_id=employee_id,
            project_id=project_id
        )

        self.db.add(association)
        self.db.commit()
        return True

    def remove_employee_from_project(self, employee_id: int, project_id: int) -> bool:
        """Удаление сотрудника из проекта"""
        association = self.db.query(EmployeeProject).filter(
            EmployeeProject.employee_id == employee_id,
            EmployeeProject.project_id == project_id
        ).first()

        if not association:
            return False

        self.db.delete(association)
        self.db.commit()
        return True

    def get_all_associations(self):
        """Получение всех связей"""
        return self.db.query(EmployeeProject).all()

    def get_all_employees_by_project_id(self, project_id: int):
        """Получение всех сотрудников проекта по его ID"""
        employee_ids = self.db.query(EmployeeProject.employee_id).filter(EmployeeProject.project_id == project_id).all()
        return [eid[0] for eid in employee_ids]

    def get_all_projects_by_employee_id(self, employee_id: int):
        """Получение всех ID проектов сотрудника по его ID"""
        project_ids = self.db.query(EmployeeProject.project_id).filter(EmployeeProject.employee_id == employee_id).all()
        return [pid[0] for pid in project_ids]