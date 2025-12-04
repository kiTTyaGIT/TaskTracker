from sqlalchemy.orm import Session
from sqlalchemy import text
from entity.task_entity import Task


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, task_data: dict) -> Task:
        """Создание новой задачи"""
        task = Task(**task_data)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_all_tasks(self, skip: int = 0, limit: int = 100):
        """Получение всех задач"""
        return self.db.query(Task).offset(skip).limit(limit).all()

    def get_task_by_id(self, task_id: int) -> Task:
        """Получение задачи по ID"""
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_tasks_by_project(self, project_id: int):
        """Получение задач по проекту"""
        return self.db.query(Task).filter(Task.project_id == project_id).all()

    def get_tasks_by_employee(self, employee_id: int):
        """Получение задач по сотруднику"""
        return self.db.query(Task).filter(Task.employee_id == employee_id).all()

    def update_task(self, task, update_data: dict) -> Task:
        """Обновление задачи"""
        for field, value in update_data.items():
            if hasattr(task, field) and value is not None:
                setattr(task, field, value)

        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, task_id: int) -> bool:
        """Удаление задачи"""
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        self.db.delete(task)
        self.db.commit()
        return True

    def delete_all_tasks_by_project_id(self, project_id: int) -> bool:
        """Каскадное удаление задач проекта"""
        tasks = self.get_tasks_by_project(project_id)
        for task in tasks:
            self.db.delete(task)
        self.db.commit()
        return True

    def assign_task_to_employee(self, task, employee_id: int) -> Task:
        """Назначение задачи сотруднику"""
        task.employee_id = employee_id
        self.db.commit()
        self.db.refresh(task)
        return task

    def update_task_status(self, task_id: int, status: str) -> Task:
        """Обновление статуса задачи"""
        task = self.get_task_by_id(task_id)
        if not task:
            return None

        task.status = status
        self.db.commit()
        self.db.refresh(task)
        return task

    def update_task_priority(self, task_id: int, priority: str) -> Task:
        """Обновление приоритета задачи"""
        task = self.get_task_by_id(task_id)
        if not task:
            return None

        task.priority = priority
        self.db.commit()
        self.db.refresh(task)
        return task