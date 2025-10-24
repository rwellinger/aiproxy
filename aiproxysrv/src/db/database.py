"""Database configuration and engine setup"""

import re

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import (
    DATABASE_ECHO,
    DATABASE_MAX_OVERFLOW,
    DATABASE_POOL_PRE_PING,
    DATABASE_POOL_RECYCLE,
    DATABASE_POOL_SIZE,
    DATABASE_URL,
)
from utils.logger import logger  # Direct import to avoid circular dependency with utils.__init__


def sanitize_url_for_logging(url):
    """Remove password from URL for safe logging"""
    return re.sub(r"://([^:]+):([^@]+)@", r"://\1:***@", url)


logger.debug("Database connection initiated", database_url=sanitize_url_for_logging(DATABASE_URL))
try:
    # Create engine with configurable connection pool settings
    # Pool settings can be configured via environment variables (see env_template)
    engine = create_engine(
        DATABASE_URL,
        echo=DATABASE_ECHO,
        pool_size=DATABASE_POOL_SIZE,
        max_overflow=DATABASE_MAX_OVERFLOW,
        pool_pre_ping=DATABASE_POOL_PRE_PING,
        pool_recycle=DATABASE_POOL_RECYCLE,
    )
    logger.debug(
        "Database engine created",
        echo=DATABASE_ECHO,
        pool_size=DATABASE_POOL_SIZE,
        max_overflow=DATABASE_MAX_OVERFLOW,
        pool_pre_ping=DATABASE_POOL_PRE_PING,
        pool_recycle=DATABASE_POOL_RECYCLE,
    )
except Exception as e:
    logger.error("Database engine creation failed", error=str(e), error_type=type(e).__name__)
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Get database session"""
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        logger.error("Database session creation failed", error=str(e), error_type=type(e).__name__)
        raise
    finally:
        try:
            db.close()
        except Exception as e:
            logger.error("Database session close failed", error=str(e), error_type=type(e).__name__)
