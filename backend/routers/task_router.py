from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db_connect.db import get_db
from repository.task_repository import TaskRepository
from schemas.task_schema import Task, TaskCreate, TaskUpdate, TaskWithDetails

router = APIRouter(prefix="/tasks", tags=["tasks"])

def get_task_repository(db: Session = Depends(get_db)) -> TaskRepository:
    return TaskRepository(db)

@router.get("/", response_model=List[Task])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    repo: TaskRepository = Depends(get_task_repository)
):
    return repo.get_all_tasks(skip=skip, limit=limit)

@router.get("/with-details", response_model=List[TaskWithDetails])
async def list_tasks_with_details(
    repo: TaskRepository = Depends(get_task_repository)
):
    return repo.get_tasks_with_details()

@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    repo: TaskRepository = Depends(get_task_repository)
):
    task = repo.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.get("/project/{project_id}", response_model=List[Task])
async def get_tasks_by_project(
    project_id: int,
    repo: TaskRepository = Depends(get_task_repository)
):
    return repo.get_tasks_by_project(project_id)

@router.get("/employee/{employee_id}", response_model=List[Task])
async def get_tasks_by_employee(
    employee_id: int,
    repo: TaskRepository = Depends(get_task_repository)
):
    return repo.get_tasks_by_employee(employee_id)

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    repo: TaskRepository = Depends(get_task_repository)
):
    try:
        return repo.create_task(task_data.model_dump())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    repo: TaskRepository = Depends(get_task_repository)
):
    try:
        task = repo.update_task(task_id, task_data.model_dump(exclude_unset=True))
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/{task_id}/assign/{employee_id}", response_model=Task)
async def assign_task(
    task_id: int,
    employee_id: int,
    repo: TaskRepository = Depends(get_task_repository)
):
    try:
        task = repo.assign_task_to_employee(task_id, employee_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/{task_id}/status", response_model=Task)
async def update_task_status(
    task_id: int,
    status: str,
    repo: TaskRepository = Depends(get_task_repository)
):
    task = repo.update_task_status(task_id, status)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.patch("/{task_id}/priority", response_model=Task)
async def update_task_priority(
    task_id: int,
    priority: str,
    repo: TaskRepository = Depends(get_task_repository)
):
    task = repo.update_task_priority(task_id, priority)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    repo: TaskRepository = Depends(get_task_repository)
):
    result = repo.delete_task(task_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )