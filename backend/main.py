"""TaskFlow API - FastAPI entry point for Vercel deployment."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:  # Support both package and standalone execution
    from db import create_db_and_tables  # type: ignore
    from routes import tasks, auth_routes, users  # type: ignore
    from config import settings  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    from db import create_db_and_tables
    from routes import tasks, auth_routes, users
    from config import settings


app = FastAPI(
    title="TaskFlow API",
    version="2.0.0",
    description="Phase 2: Multi-user Todo API with authentication",
)

cors_origins = settings.cors_origins or ["http://localhost:3000"]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
