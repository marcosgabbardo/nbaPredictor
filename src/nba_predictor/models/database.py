"""Database configuration and session management."""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from nba_predictor.core.config import get_settings
from nba_predictor.core.logger import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# Global engine and session factory
_engine = None
_SessionLocal = None


def init_db() -> None:
    """Initialize database engine and session factory."""
    global _engine, _SessionLocal

    settings = get_settings()
    logger.info("Initializing database", db_url=settings.database.url.split("@")[1])

    _engine = create_engine(
        settings.database.url,
        echo=settings.app.env == "development",
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    logger.info("Database initialized successfully")


def create_tables() -> None:
    """Create all tables in the database."""
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    logger.info("Creating database tables")
    Base.metadata.create_all(bind=_engine)
    logger.info("Database tables created successfully")


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session context manager.

    Yields:
        Database session

    Example:
        with get_db() as db:
            teams = db.query(Team).all()
    """
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    db = _SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
