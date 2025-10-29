from entity.employee_entity import Employee


class UserRepository:
    def __init__(self, db):
        self.db = db

    def create_user(self, user_data: dict):
        """Создание нового пользователя"""
        empl = Employee(**user_data)
        self.db.add(empl)
        self.db.commit()
        self.db.refresh(empl)
        return empl

    def get_user_by_email(self, mail: str):
        """Получение пользователя по email"""
        return self.db.query(Employee).filter(Employee.mail == mail).first()

    def get_all_users(self, skip: int = 0, limit: int = 100):
        """Получение всех пользователей с пагинацией"""
        return self.db.query(Employee).offset(skip).limit(limit).all()