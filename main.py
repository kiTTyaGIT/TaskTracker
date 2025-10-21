from db import get_db
from repository.employee_repository import UserRepository


def main():
    db = next(get_db())
    user_repo = UserRepository(db)

    try:
        # Создание пользователя
        new_user = user_repo.create_user({
            "name": "Петя",
            "surname": "Петев",
            "mail": "petya@example.com",
            "phone_number": "+79999999997",
        })
        print(f"Created user: {new_user}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()