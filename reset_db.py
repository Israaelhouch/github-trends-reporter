from src.db.database import engine
from src.db.models import Base
from src.utils.logger import setup_logger

logger = setup_logger("database")
def reset_db():
    logger.info("Dropping and recreating tables...")
    Base.metadata.drop_all(bind=engine)
    
reset_db()