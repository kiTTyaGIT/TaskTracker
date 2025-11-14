from sqlalchemy.orm import Session
from sqlalchemy import text
from entity.employee_project_entity import EmployeeProject


class EmployeeProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_employee_to_project(self, employee_id: int, project_id: int) -> bool:
        """Добавление сотрудника в проект"""
        try:
            # Проверяем существование сотрудника
            employee_exists = self.db.execute(
                text("SELECT 1 FROM employee WHERE id = :employee_id"),
                {"employee_id": employee_id}
            ).first()

            # Проверяем существование проекта
            project_exists = self.db.execute(
                text("SELECT 1 FROM project WHERE id = :project_id"),
                {"project_id": project_id}
            ).first()

            if not employee_exists or not project_exists:
                return False

            # Проверяем, не существует ли уже такая связь
            existing = self.db.query(EmployeeProject).filter(
                EmployeeProject.employee_id == employee_id,
                EmployeeProject.project_id == project_id
            ).first()

            if existing:
                return False

            # Создаем новую связь
            association = EmployeeProject(
                employee_id=employee_id,
                project_id=project_id
            )

            self.db.add(association)
            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            print(f"Error adding employee to project: {e}")
            return False

    def remove_employee_from_project(self, employee_id: int, project_id: int) -> bool:
        """Удаление сотрудника из проекта"""
        try:
            association = self.db.query(EmployeeProject).filter(
                EmployeeProject.employee_id == employee_id,
                EmployeeProject.project_id == project_id
            ).first()

            if not association:
                return False

            self.db.delete(association)
            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            print(f"Error removing employee from project: {e}")
            return False

    def get_project_employees(self, project_id: int):
        """Получение всех сотрудников проекта"""
        try:
            result = self.db.execute(
                text("""
                    SELECT e.* FROM employee e
                    JOIN employee_project ep ON e.id = ep.employee_id
                    WHERE ep.project_id = :project_id
                """),
                {"project_id": project_id}
            )

            employees = []
            for row in result:
                employees.append({
                    "id": row[0],
                    "name": row[1],
                    "surname": row[2],
                    "patronymic": row[3],
                    "phone_number": row[4],
                    "mail": row[5]
                })
            return employees

        except Exception as e:
            print(f"Error getting project employees: {e}")
            return []

    def get_employee_projects(self, employee_id: int):
        """Получение всех проектов сотрудника"""
        try:
            result = self.db.execute(
                text("""
                    SELECT p.* FROM project p
                    JOIN employee_project ep ON p.id = ep.project_id
                    WHERE ep.employee_id = :employee_id
                """),
                {"employee_id": employee_id}
            )

            projects = []
            for row in result:
                projects.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "start_date": row[3],
                    "finish_date": row[4]
                })
            return projects

        except Exception as e:
            print(f"Error getting employee projects: {e}")
            return []

    def get_all_associations(self):
        """Получение всех связей"""
        return self.db.query(EmployeeProject).all()