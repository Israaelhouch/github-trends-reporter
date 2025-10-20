from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from src.db.models import Base, GitHubRepo
from config import DATABASE_URL
from src.utils.logger import setup_logger
from datetime import datetime
import pandas as pd

logger = setup_logger("database")


class GitHubDB:
    def __init__(self, database_url=DATABASE_URL):
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.init_db()
        self.session: Session | None = None

    def init_db(self):
        """Create tables if missing. Safe to call multiple times."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database initialized: tables created if missing.")
        except OperationalError as e:
            logger.error("Failed to initialize database", exc_info=e)

    def connect(self):
        """Open a session."""
        self.session = self.SessionLocal()
        return self.session

    def close(self):
        """Close session if open."""
        if self.session:
            self.session.close()
            self.session = None
            logger.debug("Database session closed.")

    def save_repos(self, df: pd.DataFrame, topic: str) -> datetime:
        """Save DataFrame of repos to the database."""
        if df.empty:
            raise ValueError(f"No data to save for topic '{topic}'")

        session = self.session or self.connect()
        fetched_at = datetime.utcnow()

        try:
            for _, row in df.iterrows():
                repo = GitHubRepo(
                    topic=topic,
                    full_name=row["full_name"],
                    html_url=row["html_url"],
                    stargazers_count=row.get("stargazers_count"),
                    language=row.get("language"),
                    owner=row.get("owner"),
                    fork=row.get("fork"),
                    created_at=row.get("created_at"),
                    updated_at=row.get("updated_at"),
                    fetched_at=fetched_at
                )
                session.add(repo)
            session.commit()
            logger.info(f"Saved {len(df)} repositories for topic '{topic}'")
            return fetched_at
        except Exception as e:
            session.rollback()
            logger.exception(f"Failed to save data for topic '{topic}': {e}")
            raise

    def load_latest_fetches(self, topic: str) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
        """
        Load the most recent and previous fetches for a topic.
        Returns (current_data, previous_data) as pandas DataFrames.
        """
        session = self.session or self.connect()

        timestamps = (
            session.query(GitHubRepo.fetched_at)
            .filter(GitHubRepo.topic == topic)
            .distinct()
            .order_by(GitHubRepo.fetched_at.desc())
            .limit(2)
            .all()
        )

        if not timestamps:
            return None, None

        current_time = timestamps[0][0]
        previous_time = timestamps[1][0] if len(timestamps) > 1 else None

        current_data = pd.read_sql(
            session.query(GitHubRepo).filter(
                GitHubRepo.topic == topic, GitHubRepo.fetched_at == current_time
            ).statement,
            session.bind
        )

        previous_data = None
        if previous_time:
            previous_data = pd.read_sql(
                session.query(GitHubRepo).filter(
                    GitHubRepo.topic == topic, GitHubRepo.fetched_at == previous_time
                ).statement,
                session.bind
            )

        logger.info(f"Loaded current and previous fetches for topic '{topic}'")
        return current_data, previous_data
