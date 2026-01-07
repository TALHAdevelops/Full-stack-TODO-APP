"""TaskFlow API - FastAPI entry point for Vercel deployment."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import create_db_and_tables
from routes import tasks, auth_routes, users
from config import settings


app = FastAPI(
    title="TaskFlow API",
    version="2.0.0",
    description="Phase 2: Multi-user Todo API with authentication",
)

# Configure CORS origins
cors_origins = settings.cors_origins or ["http://localhost:3000"]

# Add production frontend explicitly if not in list
if "https://talha-taskflow-web.vercel.app" not in cors_origins:
    cors_origins.append("https://talha-taskflow-web.vercel.app")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(tasks.router)
app.include_router(auth_routes.router)
app.include_router(users.router)


@app.on_event("startup")
def on_startup():
    """Initialize resources for each cold start."""
    create_db_and_tables()


@app.get("/")
def read_root():
    return {
        "message": "TaskFlow API Phase 2",
        "status": "running",
        "version": "2.0.0",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
