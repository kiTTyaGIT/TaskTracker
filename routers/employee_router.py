from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db import get_db
from repository.employee_repository import EmployeeRepository
from schemas.employee_schema import Employee, EmployeeCreate, EmployeeUpdate

router = APIRouter(prefix="/employees", tags=["employees"])

def get_user_repository(db: Session = Depends(get_db)) -> EmployeeRepository:
    return EmployeeRepository(db)

@router.get("/", response_model=List[Employee])
async def list_employees(
    skip: int = 0, 
    limit: int = 100,
    repo: EmployeeRepository = Depends(get_user_repository)
):
    return repo.get_all_employees(skip=skip, limit=limit)

@router.get("/{employee_id}", response_model=Employee)
async def get_employee(
    employee_id: int, 
    repo: EmployeeRepository = Depends(get_user_repository)
):
    employee = repo.get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return employee

@router.post("/", response_model=Employee, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate, 
    repo: EmployeeRepository = Depends(get_user_repository)
):
    return repo.create_employee(employee_data.model_dump())

@router.put("/{employee_id}", response_model=Employee)
async def update_employee(
    employee_id: int, 
    employee_data: EmployeeUpdate, 
    repo: EmployeeRepository = Depends(get_user_repository)
):
    employee = repo.update_employee(employee_id, employee_data.model_dump(exclude_unset=True))
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return employee

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: int, 
    repo: EmployeeRepository = Depends(get_user_repository)
):
    result = repo.delete_employee_by_id(employee_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return None


@router.patch("/employees/{employee_id}/role", status_code=status.HTTP_404_NOT_FOUND)
async def update_role(
    employee_id: int,
    repo: EmployeeRepository = Depends(get_user_repository)
):
    result = repo.delete_employee_by_id(employee_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return None