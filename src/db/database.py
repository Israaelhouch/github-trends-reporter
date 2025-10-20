from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from src.db.models import Base
from config import DATABASE_URL
from src.utils.logger import setup_logger

logger = setup_logger("database")

# SQLAlchemy engine & session factory
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize the database:
    - Creates tables if they don't exist.
    - Safe to call multiple times.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized: tables created if missing.")
    except OperationalError as e:
        logger.error("Failed to connect or initialize database", exc_info=e)


def get_db():
    """
    Dependency / helper: yield a database session.
    Properly closes session after usage.
    Usage:
        with get_db() as session:
            session.query(...)
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        logger.debug("Database session closed.")
