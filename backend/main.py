import uvicorn
from fastapi import FastAPI
from routers import employee_router, project_router, employee_project_router, task_router

app = FastAPI(
    title="Management API",
    description="API",
    version="1.0.0"
)

app.include_router(task_router.router)
app.include_router(employee_router.router)
app.include_router(project_router.router)
app.include_router(employee_project_router.router)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8090,
        reload=False
    )
