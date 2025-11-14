from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db_connect.db import get_db
from repository.project_repository import ProjectRepository
from schemas.project_schema import Project, ProjectCreate, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])

def get_project_repository(db: Session = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(db)

@router.get("/", response_model=List[Project])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    repo: ProjectRepository = Depends(get_project_repository)
):
    return repo.get_all_projects(skip=skip, limit=limit)

@router.get("/{project_name}", response_model=Project)
async def get_project(
    project_name: str,
    repo: ProjectRepository = Depends(get_project_repository)
):
    project = repo.get_project_by_name(project_name)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COMMON_NOT_FOUND_EXCEPTION_MESSAGE
        )
    return project

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    repo: ProjectRepository = Depends(get_project_repository)
):
    return repo.create_project(project_data.model_dump())

@router.put("/{project_name}", response_model=Project)
async def update_project(
    project_name: str,
    project_data: ProjectUpdate,
    repo: ProjectRepository = Depends(get_project_repository)
):
    project = repo.update_project(project_name, project_data.model_dump(exclude_unset=True))
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COMMON_NOT_FOUND_EXCEPTION_MESSAGE
        )
    return project

@router.delete("/{project_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_name: str,
    repo: ProjectRepository = Depends(get_project_repository)
):
    result = repo.delete_project_by_name(project_name)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COMMON_NOT_FOUND_EXCEPTION_MESSAGE
        )
    return None

COMMON_NOT_FOUND_EXCEPTION_MESSAGE = "Project not found"