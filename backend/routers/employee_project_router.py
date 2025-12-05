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
    return EmployeeProjectHandler(db, EmployeeProjectRepository(db),  EmployeeRepository(db), ProjectRepository(db))


@router.post("/", response_model=EmployeeProjectResponse, status_code=status.HTTP_201_CREATED)
async def add_employee_to_project(
        data: EmployeeProjectCreate,
        handler: EmployeeProjectHandler = Depends(get_employee_project_handler)
):
    success = handler.add_employee_to_project(data.employee_id, data.project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add employee to project. Check if both exist and relationship doesn't already exist."
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
    # Проверяем существование проекта
    project_exists = handler.project_repository.is_project_exists(project_id)

    if not project_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден!"
        )

    # Получаем проект
    # project_result = handler.db.execute(
    #     text("SELECT id, name, description FROM project WHERE id = :project_id"),
    #     {"project_id": project_id}
    # ).first()
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
    # Проверяем существование сотрудника
    employee_exists = handler.employee_repository.is_employee_exists(employee_id)

    if not employee_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден!"
        )

    # Получаем сотрудника
    # employee_result = handler.db.execute(
    #     text("SELECT id, name, surname, patronymic FROM employee WHERE id = :employee_id"),
    #     {"employee_id": employee_id}
    # ).first()
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
    return handler.get_all_associations()