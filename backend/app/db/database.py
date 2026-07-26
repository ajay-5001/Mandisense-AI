"""
MandiSense Database Connection
==============================
SQLAlchemy engine and session setup for SQLite.
Designed to be easily swappable to PostgreSQL for production.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import DB_PATH


# ─── SQLAlchemy Base ──────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# ─── Engine Setup ─────────────────────────────────────────────────────────────
# SQLite connection string. For production, swap to:
#   postgresql://user:pass@host:5432/mandisense
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set True for SQL debug logging
    connect_args={"check_same_thread": False}  # Required for SQLite + FastAPI
)

# Enable SQLite foreign key enforcement (off by default in SQLite)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# ─── Session Factory ─────────────────────────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for FastAPI — yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables():
    """Create all tables defined in models.py. Safe to call multiple times."""
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """Drop all tables. Used for re-seeding."""
    Base.metadata.drop_all(bind=engine)
