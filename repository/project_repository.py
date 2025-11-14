from sqlalchemy import text
from sqlalchemy.orm import Session

from entity.project_entity import Project


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
        return self.db.query(Project).offset(skip).limit(limit).all()

    def get_project_by_name(self, project_name: str) -> Project:
        return self.db.query(Project).filter(Project.name == project_name).first()

    def delete_project_by_name(self, project_name: str) -> bool:
        project = self.get_project_by_name(project_name)
        if not project:
            return False

        self.db.execute(
            text(""" 
                DELETE FROM task t
                WHERE t.project_id = :project_id
            """),
            {"project_id": project.id}
        )
        self.db.delete(project)
        self.db.commit()
        return True

    def update_project(self, project_name: str, update_data: dict) -> Project:
        project = self.get_project_by_name(project_name)
        if not project:
            return None

        for field, value in update_data.items():
            if hasattr(project, field):
                setattr(project, field, value)

        self.db.commit()
        self.db.refresh(project)
        return project
