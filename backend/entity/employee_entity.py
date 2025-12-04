# Модуль с моделями данных SQLAlchemy.
# Определяет структуру таблицы сотрудников (Employee).

from sqlalchemy import Column, Integer, Text
# Импортируем базовый класс для моделей
from db_connect.db import Base


class Employee(Base):
    #соотносит класс к таблице БД
    __tablename__ = "employee"

    # primary_key=True - первичный ключ
    # autoincrement=True - автоматическое увеличение значения
    # index=True - создание индекса для ускорения поиска
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(Text)
    surname = Column(Text)
    patronymic = Column(Text)
    phone_number = Column(Text)
    mail = Column(Text)
    role = Column(Text)

    # Метод для строкового представления объекта
    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.name}', role='{self.role}')>"