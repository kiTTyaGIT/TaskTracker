#Основной файл приложения
import uvicorn
from fastapi import FastAPI
from routers import employee_router, project_router, employee_project_router, task_router

# Создание экземпляра FastAPI приложения
app = FastAPI(
    title="Management API",
    description="API",
    version="1.0.0"
)

# Подключение маршрутизаторов
app.include_router(task_router.router)
app.include_router(employee_router.router)
app.include_router(project_router.router)
app.include_router(employee_project_router.router)

# Настройка CORS (Cross-Origin Resource Sharing)
# механизм безопасности в браузерах, который ограничивает доступ к API
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True, # Разрешить все кукисы, авторизацю
    allow_methods=["*"], # Разрешить все методы
    allow_headers=["*"], # Разрешить все заголовки
)
# Точка входа для запуска приложения
if __name__ == "__main__":
    # Запуск сервера Uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0", # Доступ со всех интерфейсов
        port=8090, # Порт приложения
        reload=False # Автоматическая перезагрузка при изменении кода
    )
