from sqlmodel import SQLModel, Session, create_engine

try:  # Support both package and direct execution contexts
    from backend.config import settings  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    from .config import settings  # type: ignore

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
    try:
        from backend import models  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover
        from . import models  # type: ignore

    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency yielding a database session."""
    with Session(engine) as session:
        yield session
