# связи задач
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db_connect.db import get_db
from repository.task_repository import TaskRepository
from schemas.task_schema import Task, TaskCreate, TaskUpdate, TaskWithDetails
from repository.project_repository import ProjectRepository
from handler.task_handler import TaskHandler
from repository.employee_repository import EmployeeRepository

router = APIRouter(prefix="/tasks", tags=["tasks"])

def get_task_handler(db: Session = Depends(get_db)) -> TaskHandler:
    """Получение обертки над репозиторием задач"""
    return TaskHandler(db, TaskRepository(db), ProjectRepository(db), EmployeeRepository(db))

@router.get("/", response_model=List[Task])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    handler: TaskHandler = Depends(get_task_handler)
):
    """Получение списка всех задач"""
    return handler.get_all_tasks(skip=skip, limit=limit)

@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    handler: TaskHandler = Depends(get_task_handler)
):
    """Получение задачи по ID"""
    task = handler.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена!"
        )
    return task

@router.get("/project/{project_id}", response_model=List[Task])
async def get_tasks_by_project(
    project_id: int,
    handler: TaskHandler = Depends(get_task_handler)
):
    """Получение задач по проекту"""
    return handler.get_tasks_by_project(project_id)

@router.get("/employee/{employee_id}", response_model=List[Task])
async def get_tasks_by_employee(
    employee_id: int,
    handler: TaskHandler = Depends(get_task_handler)
):
    """Получение задач по сотруднику"""
    return handler.get_tasks_by_employee(employee_id)

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    handler: TaskHandler = Depends(get_task_handler)
):
    """Создание новоей задачи"""
    try:
        return handler.create_task(task_data.model_dump())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    handler: TaskHandler = Depends(get_task_handler)
):
    """Обновление задачи"""
    try:
        task = handler.update_task(task_id, task_data.model_dump(exclude_unset=True))
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена!"
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
    handler: TaskHandler = Depends(get_task_handler)
):
    """Назначение задачи сотруднику"""
    try:
        task = handler.assign_task_to_employee(task_id, employee_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена!"
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
    handler: TaskHandler = Depends(get_task_handler)
):
    """Обновление статуса задачи"""
    task = handler.update_task_status(task_id, status)
    task = handler.update_task_status(task_id, status)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена!"
        )
    return task

@router.patch("/{task_id}/priority", response_model=Task)
async def update_task_priority(
    task_id: int,
    priority: str,
    handler: TaskHandler = Depends(get_task_handler)
):
    """Обновление приоритета задачи"""
    task = handler.update_task_status(task_id, status)
    task = handler.update_task_priority(task_id, priority)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена!"
        )
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    handler: TaskHandler = Depends(get_task_handler)
):
    """Удаление задачи"""
    task = handler.update_task_status(task_id, status)
    result = handler.delete_task(task_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )