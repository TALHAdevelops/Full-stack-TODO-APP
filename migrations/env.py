"""Alembic environment configuration for TaskFlow migrations.

Note: TaskFlow uses SQLModel's create_all() for table creation in development.
These migration scripts serve as documentation of schema changes and can be
run manually against production databases when needed.

Usage:
    alembic upgrade head     # Apply all pending migrations
    alembic downgrade -1     # Rollback last migration
    alembic history          # Show migration history
"""

import os
import sys
from pathlib import Path

# Add backend directory to Python path for model imports
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Migration configuration
DATABASE_URL = os.getenv("DATABASE_URL", "")

MIGRATION_SCRIPTS = {
    "001": "001_add_recurring_fields.py",
    "002": "002_create_reminders_table.py",
    "003": "003_create_event_log_table.py",
}


def get_database_url() -> str:
    """Get database URL from environment."""
    url = os.getenv("DATABASE_URL", "")
    if not url:
        raise ValueError("DATABASE_URL environment variable is required")
    return url
