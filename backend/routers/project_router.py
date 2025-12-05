# связи проектов
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db_connect.db import get_db
from schemas.project_schema import Project, ProjectCreate, ProjectUpdate

from repository.task_repository import TaskRepository
from handler.project_handler import ProjectHandler
from repository.project_repository import ProjectRepository

router = APIRouter(prefix="/projects", tags=["projects"])

def get_project_handler(db: Session = Depends(get_db)) -> ProjectHandler:
    """Получение обертки над репозиторием проектов"""
    return ProjectHandler(db, ProjectRepository(db), TaskRepository(db))

@router.get("/", response_model=List[Project])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    handler: ProjectHandler = Depends(get_project_handler)
):
    """Получение списка всех проектов"""
    return handler.get_all_projects(skip=skip, limit=limit)

@router.get("/{project_name}", response_model=Project)
async def get_project(
    project_name: str,
    handler: ProjectHandler = Depends(get_project_handler)
):
    """Получение проекта по названию"""
    project = handler.get_project_by_name(project_name)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден!"
        )
    return project

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    handler: ProjectHandler = Depends(get_project_handler)
):
    """Создание нового проекта"""
    project = handler.get_project_by_name(project_data.name)
    if project:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Проект с таким названием уже существует!"
        )
    return handler.create_project(project_data.model_dump())

@router.put("/{project_name}", response_model=Project)
async def update_project(
    project_name: str,
    project_data: ProjectUpdate,
    handler: ProjectHandler = Depends(get_project_handler)
):

    """Обновление проекта"""
    project = handler.update_project(project_name, project_data.model_dump(exclude_unset=True))
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден!"
        )
    return project

@router.delete("/{project_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_name: str,
    handler: ProjectHandler = Depends(get_project_handler)
):
    """Удаление проекта по названию"""
    result = handler.delete_project_by_name(project_name)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден!"
        )
    return None
