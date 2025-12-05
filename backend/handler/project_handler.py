#обертка над слоем репозитория проекта
from sqlalchemy import text, Boolean
from sqlalchemy.orm import Session
from entity.project_entity import Project
from repository.task_repository import TaskRepository
from repository.project_repository import ProjectRepository


class ProjectHandler:
    def __init__(self, db: Session, project_repository: ProjectRepository, task_repository: TaskRepository):
        self.db = db
        self.project_repository = project_repository
        self.task_repository = task_repository

    def create_project(self, project_data: dict) -> Project:
        """Создание нового проекта"""
        return self.project_repository.create_project(project_data)

    def get_all_projects(self, skip: int = 0, limit: int = 100) -> list[type[Project]]:
        """Получение всех проектов"""
        return self.project_repository.get_all_projects(skip=skip, limit=limit)

    def get_project_by_name(self, project_name: str) -> Project:
        """Получение проекта по имени"""
        return self.project_repository.get_project_by_name(project_name)

    def get_project_by_id(self, project_id: int) -> Project:
        """Получение проекта по ID"""
        return self.project_repository.get_project_by_id(project_id)

    def is_project_exists(self, project_id: int) -> Boolean:
        """Проверка существования проекта"""
        return self.project_repository.is_project_exists(project_id)

    def delete_project_by_name(self, project_name: str) -> bool:
        """Удаление проекта по имени"""
        project = self.get_project_by_name(project_name)
        if not project:
            return False
        self.task_repository.delete_all_tasks_by_project_id(project.id)
        return self.project_repository.delete_project_by_name(project)

    def update_project(self, project_name: str, update_data: dict) -> Project:
        """Обновление информации проекта"""
        return self.project_repository.update_project(project_name, update_data)