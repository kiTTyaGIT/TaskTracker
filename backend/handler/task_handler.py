#обертка над слоем репозитория задачи
from sqlalchemy.orm import Session
from sqlalchemy import text
from entity.task_entity import Task
from repository.project_repository import ProjectRepository
from repository.task_repository import TaskRepository
from repository.employee_repository import EmployeeRepository


class TaskHandler:
    def __init__(self, db: Session, task_repository: TaskRepository, project_repository: ProjectRepository, employee_repository: EmployeeRepository):
        self.db = db
        self.task_repository = task_repository
        self.project_repository = project_repository
        self.employee_repository = employee_repository


    def create_task(self, task_data: dict) -> Task:
        """Создание новой задачи"""
        # Проверяем существование проекта
        project_exists = self.project_repository.is_project_exists(task_data['project_id'])

        if not project_exists:
            raise ValueError("Проект с таким ID не найден")

        # Проверяем существование сотрудника если указан
        if task_data.get("employee_id"):
            employee_exists = self.employee_repository.is_employee_exists(task_data['employee_id'])

            if not employee_exists:
                raise ValueError("Сотрудник с таким ID не найден")

        return self.task_repository.create_task(task_data)

    def get_all_tasks(self, skip: int = 0, limit: int = 100):
        """Получение всех задач"""
        return self.task_repository.get_all_tasks(skip=skip, limit=limit)

    def get_task_by_id(self, task_id: int) -> Task:
        """Получение задачи по ID"""
        return self.task_repository.get_task_by_id(task_id)

    def get_tasks_by_project(self, project_id: int):
        """Получение задач по проекту"""
        return self.task_repository.get_tasks_by_project(project_id)

    def get_tasks_by_employee(self, employee_id: int):
        """Получение задач по сотруднику"""
        return self.task_repository.get_tasks_by_employee(employee_id)

    def update_task(self, task_id: int, update_data: dict) -> Task:
        """Обновление задачи"""
        task = self.get_task_by_id(task_id)
        if not task:
            return None

        # Проверяем существование проекта если обновляется
        if "project_id" in update_data:
            project_exists = self.project_repository.is_project_exists(update_data["project_id"])

            if not project_exists:
                raise ValueError("Проект с таким ID не найден")

        # Проверяем существование сотрудника если обновляется
        if "employee_id" in update_data and update_data["employee_id"] is not None:
            employee_exists = self.employee_repository.is_employee_exists(update_data["employee_id"])
            if not employee_exists:
                raise ValueError("Сотрудник с таким ID не найден")
        return self.task_repository.update_task(task, update_data)

    def delete_task(self, task_id: int) -> bool:
        """Удаление задачи"""
        return self.task_repository.delete_task(task_id)

    def delete_all_tasks_by_project_id(self, project_id: int) -> bool:
        """Каскадное удаление задач проекта"""
        return self.task_repository.delete_all_tasks_by_project_id(project_id)

    def assign_task_to_employee(self, task_id: int, employee_id: int) -> Task:
        """Назначение задачи сотруднику"""
        task = self.get_task_by_id(task_id)
        if not task:
            return None

        # Проверяем существование сотрудника
        employee_exists = self.employee_repository.is_employee_exists(employee_id)

        if not employee_exists:
            raise ValueError("Сотрудник с таким ID не найден")
        return self.task_repository.assign_task_to_employee(task_id, employee_id)

    def update_task_status(self, task_id: int, status: str) -> Task:
        """Обновление статуса задачи"""
        return self.task_repository.update_task_status(task_id, status)

    def update_task_priority(self, task_id: int, priority: str) -> Task:
        """Обновление приоритета задачи"""
        return self.task_repository.update_task_priority(task_id, priority)
