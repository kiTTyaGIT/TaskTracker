# Слой доступа к данным проектов
from sqlalchemy import text, Boolean
from sqlalchemy.orm import Session

from entity.project_entity import Project
from repository.task_repository import TaskRepository


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_project(self, project_data: dict) -> Project:
        """Создание нового проекта"""
        prj = Project(**project_data)
        self.db.add(prj)
        self.db.commit()
        self.db.refresh(prj)
        return prj

    def get_all_projects(self, skip: int = 0, limit: int = 100) -> list[type[Project]]:
        """Получение всех проектов"""
        return self.db.query(Project).offset(skip).limit(limit).all()

    def get_project_by_name(self, project_name: str) -> Project:
        """Получение проекта по имени"""
        return self.db.query(Project).filter(Project.name == project_name).first()

    def get_project_by_id(self, project_id: int) -> Project:
        """Получение проекта по ID"""
        return self.db.query(Project).filter(Project.id == project_id).first()

    def is_project_exists(self, project_id: int) -> Boolean:
        """Проверка существования проекта"""
        return self.db.query(Project).filter(Project.id == project_id).first()

    def delete_project_by_name(self, project) -> bool:
        """Удаление проекта по имени"""
        self.db.delete(project)
        self.db.commit()
        return True

    def update_project(self, project_name: str, update_data: dict) -> Project:
        """Обновление информации проекта"""
        project = self.get_project_by_name(project_name)
        if not project:
            return None

        for field, value in update_data.items():
            if hasattr(project, field):
                setattr(project, field, value)

        self.db.commit()
        self.db.refresh(project)
        return project
