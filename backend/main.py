from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import create_db_and_tables
from routes import tasks, auth_routes, users
from config import settings

app = FastAPI(
    title="TaskFlow API",
    version="2.0.0",
    description="Phase 2: Multi-user Todo API with authentication"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router)
app.include_router(auth_routes.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {
        "message": "TaskFlow API Phase 2",
        "status": "running",
        "version": "2.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
