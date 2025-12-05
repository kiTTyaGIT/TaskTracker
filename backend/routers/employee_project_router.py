# связи сотрудника и проекта
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List

from db_connect.db import get_db
from entity.employee_project_entity import EmployeeProject
from repository.employee_project_repository import EmployeeProjectRepository
from schemas.employee_project_schema import (
    EmployeeProjectCreate,
    EmployeeProjectResponse,
    ProjectWithEmployees,
    EmployeeWithProjects
)

from handler.employee_project_handler import EmployeeProjectHandler
from repository.employee_repository import EmployeeRepository
from repository.project_repository import ProjectRepository

router = APIRouter(prefix="/employee-projects", tags=["employee-projects"])


def get_employee_project_handler(db: Session = Depends(get_db)) -> EmployeeProjectHandler:
    """Получение обертки над репозиторием сотрудников-проектов"""
    return EmployeeProjectHandler(db, EmployeeProjectRepository(db),  EmployeeRepository(db), ProjectRepository(db))


@router.post("/", response_model=EmployeeProjectResponse, status_code=status.HTTP_201_CREATED)
async def add_employee_to_project(
        data: EmployeeProjectCreate,
        handler: EmployeeProjectHandler = Depends(get_employee_project_handler)
):
    """Добавление сотрудника к проекту"""
    success = handler.add_employee_to_project(data.employee_id, data.project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Операция добавления сотрудника к проекту не выполнена. "
                   "Убедитесь в существовании проекта и сотрудника, а также в отсутствии уже установленной связи между ними."
        )

    # Возвращаем созданную связь
    association = handler.db.query(EmployeeProject).filter(
        EmployeeProject.employee_id == data.employee_id,
        EmployeeProject.project_id == data.project_id
    ).first()

    return association


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def remove_employee_from_project(
        employee_id: int,
        project_id: int,
        handler: EmployeeProjectHandler = Depends(get_employee_project_handler)
):
    """Удаление сотрудника из проекта"""
    success = handler.remove_employee_from_project(employee_id, project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена!"
        )


@router.get("/projects/{project_id}/employees", response_model=ProjectWithEmployees)
async def get_project_employees(
        project_id: int,
        handler: EmployeeProjectHandler = Depends(get_employee_project_handler)
):
    """Получение всех сотрудников проекта"""
    # Проверяем существование проекта
    project_exists = handler.project_repository.is_project_exists(project_id)

    if not project_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден!"
        )

    project_result = handler.project_repository.get_project_by_id(project_id)

    employees = handler.get_project_employees(project_id)

    return ProjectWithEmployees(
        id=project_result.id,
        name=project_result.name,
        description=project_result.description,
        employees=employees
    )


@router.get("/employees/{employee_id}/projects", response_model=EmployeeWithProjects)
async def get_employee_projects(
        employee_id: int,
        handler: EmployeeProjectHandler = Depends(get_employee_project_handler)
):
    """Получение всех проектов сотрудника"""
    # Проверяем существование сотрудника
    employee_exists = handler.employee_repository.is_employee_exists(employee_id)

    if not employee_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден!"
        )

    employee_result = handler.employee_repository.get_employee_by_id(employee_id)

    projects = handler.get_employee_projects(employee_id)

    return EmployeeWithProjects(
        id=employee_result.id,
        name=employee_result.name,
        surname=employee_result.surname,
        patronymic=employee_result.patronymic,
        projects=projects
    )


@router.get("/", response_model=List[EmployeeProjectResponse])
async def get_all_associations(
        handler: EmployeeProjectHandler = Depends(get_employee_project_handler)
):
    """Получение всех связей сотрудников и проектов"""
    return handler.get_all_associations()