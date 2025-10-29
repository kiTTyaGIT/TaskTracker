import uvicorn
from fastapi import FastAPI
from routers import employee_router, project_router, employee_project_router

app = FastAPI(
    title="Management API",
    description="API",
    version="1.0.0"
)

app.include_router(employee_router.router)
app.include_router(project_router.router)
app.include_router(employee_project_router.router)

@app.get("/")
async def root():
    return {"message": "Management System"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8090,
        reload=False
    )
