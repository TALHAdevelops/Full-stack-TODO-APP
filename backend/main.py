"""TaskFlow API - FastAPI entry point with event-driven architecture."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from db import create_db_and_tables
from routes import tasks, auth_routes, users, chat, events
from routes import websocket as ws_routes
from config import settings
from handlers.event_processor import register_handler, start_consumers, stop_consumers
from handlers.websocket_handler import on_task_event
from services.event_log import log_event
from services.scheduler import spawn_recurring_tasks, check_pending_reminders
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    # Startup
    create_db_and_tables()
    logger.info("Database tables initialized")

    # Register event handlers
    register_handler("*", log_event)  # Log ALL events for audit trail
    register_handler("*", on_task_event)  # Broadcast ALL events to WebSocket clients
    logger.info("Event handlers registered")

    # Start event consumers (direct Kafka when USE_DAPR=false)
    await start_consumers()
    logger.info("Event system started (USE_DAPR=%s)", settings.USE_DAPR)

    # Start APScheduler for recurring tasks and reminders (non-Dapr mode)
    scheduler = AsyncIOScheduler()
    if not settings.USE_DAPR:
        scheduler.add_job(spawn_recurring_tasks, "interval", minutes=1, max_instances=1, id="recurring_tasks")
        scheduler.add_job(check_pending_reminders, "interval", minutes=1, max_instances=1, id="reminders_check")
        scheduler.start()
        logger.info("APScheduler started for recurring tasks and reminders")

    yield

    # Shutdown
    if scheduler.running:
        scheduler.shutdown(wait=False)
    await stop_consumers()
    logger.info("Event system stopped")


app = FastAPI(
    title="TaskFlow API",
    version="5.0.0",
    description="Phase 5: Event-Driven Architecture with real-time sync, recurring tasks, reminders",
    lifespan=lifespan,
)

# Configure CORS origins from settings + hardcoded defaults
cors_origins = settings.cors_origins + [
    "http://localhost:3000",
    "https://talha-taskflow-web.vercel.app",
    "https://taskflow-frontend-muhammad-talhas-projects-d748a6fc.vercel.app",
]
# Deduplicate
cors_origins = list(set(cors_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include routers
app.include_router(tasks.router)
app.include_router(auth_routes.router)
app.include_router(users.router)
app.include_router(chat.router)
app.include_router(events.router)
app.include_router(ws_routes.router)


@app.get("/")
def read_root():
    return {
        "message": "TaskFlow API Phase 5",
        "status": "running",
        "version": "5.0.0",
        "features": ["events", "websocket", "recurring-tasks", "reminders"],
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "5.0.0"}


# Dapr cron binding endpoints (called when USE_DAPR=true)
@app.post("/api/scheduler/tick")
async def dapr_scheduler_tick():
    """Dapr cron binding endpoint: spawn recurring tasks."""
    await spawn_recurring_tasks()
    return {"status": "ok"}


@app.post("/api/reminders/check")
async def dapr_reminders_check():
    """Dapr cron binding endpoint: check pending reminders."""
    await check_pending_reminders()
    return {"status": "ok"}
