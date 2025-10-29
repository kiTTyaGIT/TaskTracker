from sqlalchemy.orm import Session
from sqlalchemy import text
from entity.task_entity import Task


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, task_data: dict) -> Task:
        """Создание новой задачи"""
        # Проверяем существование проекта
        project_exists = self.db.execute(
            text("SELECT 1 FROM project WHERE id = :project_id"),
            {"project_id": task_data["project_id"]}
        ).first()

        if not project_exists:
            raise ValueError("Project does not exist")

        # Проверяем существование сотрудника если указан
        if task_data.get("employee_id"):
            employee_exists = self.db.execute(
                text("SELECT 1 FROM employee WHERE id = :employee_id"),
                {"employee_id": task_data["employee_id"]}
            ).first()

            if not employee_exists:
                raise ValueError("Employee does not exist")

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

    def get_tasks_with_details(self):
        """Получение задач с информацией о сотрудниках и проектах"""
        result = self.db.execute(text("""
            SELECT t.*, 
                   e.name as employee_name, 
                   e.surname as employee_surname,
                   p.name as project_name
            FROM task t
            LEFT JOIN employee e ON t.employee_id = e.id
            JOIN project p ON t.project_id = p.id
            ORDER BY t.id
        """))

        tasks = []
        for row in result:
            task_dict = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "needed_hours": row[3],
                "status": row[4],
                "employee_id": row[5],
                "project_id": row[6],
                "employee_name": f"{row[7]} {row[8]}" if row[7] else None,
                "project_name": row[9]
            }
            tasks.append(task_dict)

        return tasks

    def update_task(self, task_id: int, update_data: dict) -> Task:
        """Обновление задачи"""
        task = self.get_task_by_id(task_id)
        if not task:
            return None

        # Проверяем существование проекта если обновляется
        if "project_id" in update_data:
            project_exists = self.db.execute(
                text("SELECT 1 FROM project WHERE id = :project_id"),
                {"project_id": update_data["project_id"]}
            ).first()

            if not project_exists:
                raise ValueError("Project does not exist")

        # Проверяем существование сотрудника если обновляется
        if "employee_id" in update_data and update_data["employee_id"] is not None:
            employee_exists = self.db.execute(
                text("SELECT 1 FROM employee WHERE id = :employee_id"),
                {"employee_id": update_data["employee_id"]}
            ).first()

            if not employee_exists:
                raise ValueError("Employee does not exist")

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

    def assign_task_to_employee(self, task_id: int, employee_id: int) -> Task:
        """Назначение задачи сотруднику"""
        task = self.get_task_by_id(task_id)
        if not task:
            return None

        # Проверяем существование сотрудника
        employee_exists = self.db.execute(
            text("SELECT 1 FROM employee WHERE id = :employee_id"),
            {"employee_id": employee_id}
        ).first()

        if not employee_exists:
            raise ValueError("Employee does not exist")

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