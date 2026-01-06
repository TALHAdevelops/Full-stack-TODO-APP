from sqlmodel import SQLModel, Session, create_engine
from config import settings

# Create engine tuned for serverless deployments (Neon with pooled connections)
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=1,
    max_overflow=5,
)


def create_db_and_tables() -> None:
    """Create all database tables when the app starts."""
    from models import SQLModel as Models

    Models.metadata.create_all(engine)


def get_session():
    """FastAPI dependency yielding a database session."""
    with Session(engine) as session:
        yield session
