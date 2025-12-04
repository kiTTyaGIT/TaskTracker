from sqlalchemy.orm import Session
from entity.employee_project_entity import EmployeeProject

from repository.employee_repository import EmployeeRepository
from repository.project_repository import ProjectRepository
from repository.employee_project_repository import EmployeeProjectRepository


class EmployeeProjectHandler:
    def __init__(self, db: Session, employee_project_repository: EmployeeProjectRepository, employee_repository: EmployeeRepository, project_repository: ProjectRepository):
        self.db = db
        self.employee_project_repository = employee_project_repository
        self.employee_repository = employee_repository
        self.project_repository = project_repository

    def add_employee_to_project(self, employee_id: int, project_id: int) -> bool:
        """Добавление сотрудника в проект"""
        # Проверяем существование сотрудника
        employee_exists = self.employee_repository.is_employee_exists(employee_id)

        # Проверяем существование проекта
        project_exists = self.project_repository.is_project_exists(project_id)

        if not employee_exists or not project_exists:
            return False
        return self.employee_project_repository.add_employee_to_project(employee_id, project_id)

    def remove_employee_from_project(self, employee_id: int, project_id: int) -> bool:
        """Удаление сотрудника из проекта"""
        return self.employee_project_repository.remove_employee_from_project(employee_id, project_id)

    def get_all_associations(self):
        """Получение всех связей"""
        return self.employee_project_repository.get_all_associations()

    def get_project_employees(self, project_id: int):
        """Получение всех сотрудников проекта"""
        employees = []
        employee_ids = self.get_all_employees_by_project_id(project_id)
        for employee_id in employee_ids:
            current_employee = self.employee_repository.get_employee_by_id(employee_id)
            employees.append({
                "id": current_employee.id,
                "name": current_employee.name,
                "surname": current_employee.surname,
                "patronymic": current_employee.patronymic,
                "phone_number": current_employee.phone_number,
                "mail": current_employee.mail
            })

        return employees

    def get_employee_projects(self, employee_id: int):
        """Получение всех проектов сотрудника"""
        projects = []
        project_ids = self.get_all_projects_by_employee_id(employee_id)
        for project_id in project_ids:
            current_project = self.project_repository.get_project_by_id(project_id)
            projects.append({
                "id": current_project.id,
                "name": current_project.name,
                "description": current_project.description,
                "start_date": current_project.start_date,
                "finish_date": current_project.finish_date
            })
        return projects

    def get_all_employees_by_project_id(self, project_id: int):
        return self.employee_project_repository.get_all_employees_by_project_id(project_id)

    def get_all_projects_by_employee_id(self, employee_id: int):
        return self.employee_project_repository.get_all_projects_by_employee_id(employee_id)