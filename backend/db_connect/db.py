from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL для подключения к базе данных PostgreSQL
# Формат: postgresql://пользователь:пароль@хост:порт/имя_базы_данных
DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/task_tracker_db"

# Создание движка SQLAlchemy для подключения к базе данных
# Движок управляет пулом соединений и выполняет SQL-запросы
engine = create_engine(DATABASE_URL)

# Создание фабрики сессий для работы с базой данных
# - autocommit=False: отключаем автоматическое подтверждение транзакций
# - autoflush=False: отключаем автоматическую синхронизацию сессии с базой данных
# - bind=engine: привязываем сессии к созданному движку
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей (таблиц) базы данных
# Все модели будут наследоваться от этого класса
Base = declarative_base()


# Генератор сессий базы данных для использования в зависимостях FastAPI.
# Создает новую сессию для каждого запроса и гарантирует ее закрытие после завершения.
def get_db():
    # Создаем новую сессию базы данныхS QLAlchemy
    db = SessionLocal()
    try:
        # Возвращаем сессию для использования в обработчике запроса
        yield db
    finally:
        # Гарантированно закрываем сессию после завершения работы
        # (даже если в процессе возникло исключение)
        db.close()