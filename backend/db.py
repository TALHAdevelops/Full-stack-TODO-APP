from sqlmodel import create_engine, SQLModel, Session
from .config import settings

# Create engine with Neon PostgreSQL connection
# Note: Neon requires sslmode=require which should be in DATABASE_URL
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Log SQL queries (disable in production)
    pool_pre_ping=True,  # Verify connections before use
    pool_size=5,  # Connection pool size
    max_overflow=10  # Maximum overflow connections
)

def create_db_and_tables():
    """Create all database tables"""
    from . import models  # Ensure models are registered
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for getting database session"""
    with Session(engine) as session:
        yield session
