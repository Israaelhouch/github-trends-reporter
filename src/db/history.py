"""Snapshot history: one small record per repository per day, used to compute star growth.

Two interchangeable backends:
- CsvHistory (default): `data/history/<topic>/<YYYY-MM-DD>.csv`, ~10 KB per run. Plain text, so the
  scheduled workflow can commit it to git without bloating the repository.
- SqlHistory: any SQLAlchemy URL (e.g. PostgreSQL), enabled by setting DATABASE_URL.

Saving the same day twice overwrites that day, so manual re-runs never compare a week against itself.
"""

import logging
import os
from datetime import date
from typing import Protocol

import pandas as pd
from sqlalchemy import create_engine, delete, func, insert, select
from sqlalchemy.engine import make_url

from src.db.models import Base, SnapshotRow
from src.processor.storage import slugify

logger = logging.getLogger(__name__)

COLUMNS = ["full_name", "stargazers_count", "forks_count"]


class History(Protocol):
    def save(self, df: pd.DataFrame, topic: str, day: date) -> None: ...

    def load_previous(self, topic: str, before: date) -> pd.DataFrame | None:
        """Most recent snapshot strictly before `before`, with a `snapshot_date` column; None if none."""
        ...


class CsvHistory:
    def __init__(self, root: str):
        self.root = root

    def _dir(self, topic: str) -> str:
        return os.path.join(self.root, slugify(topic))

    def save(self, df: pd.DataFrame, topic: str, day: date) -> None:
        os.makedirs(self._dir(topic), exist_ok=True)
        path = os.path.join(self._dir(topic), f"{day.isoformat()}.csv")
        df[COLUMNS].sort_values("full_name").to_csv(path, index=False)
        logger.info("Saved %d-row snapshot to %s", len(df), path)

    def load_previous(self, topic: str, before: date) -> pd.DataFrame | None:
        if not os.path.isdir(self._dir(topic)):
            return None
        days = sorted(
            f.removesuffix(".csv")
            for f in os.listdir(self._dir(topic))
            if f.endswith(".csv") and f.removesuffix(".csv") < before.isoformat()
        )
        if not days:
            return None
        df = pd.read_csv(os.path.join(self._dir(topic), f"{days[-1]}.csv"))
        df["snapshot_date"] = days[-1]
        return df


class SqlHistory:
    def __init__(self, database_url: str):
        url = make_url(database_url)
        self.engine = create_engine(url)
        Base.metadata.create_all(self.engine)
        logger.info("Using database history (%s)", url.render_as_string(hide_password=True))

    def save(self, df: pd.DataFrame, topic: str, day: date) -> None:
        records = [
            {
                "topic": topic,
                "snapshot_date": day,
                "full_name": r["full_name"],
                "stargazers_count": int(r["stargazers_count"]),
                "forks_count": int(r["forks_count"]),
            }
            for r in df[COLUMNS].to_dict(orient="records")
        ]
        with self.engine.begin() as conn:
            conn.execute(delete(SnapshotRow).where(SnapshotRow.topic == topic, SnapshotRow.snapshot_date == day))
            conn.execute(insert(SnapshotRow), records)

    def load_previous(self, topic: str, before: date) -> pd.DataFrame | None:
        with self.engine.connect() as conn:
            prev_day = conn.execute(
                select(func.max(SnapshotRow.snapshot_date)).where(
                    SnapshotRow.topic == topic, SnapshotRow.snapshot_date < before
                )
            ).scalar()
            if prev_day is None:
                return None
            df = pd.read_sql(
                select(SnapshotRow.full_name, SnapshotRow.stargazers_count, SnapshotRow.forks_count).where(
                    SnapshotRow.topic == topic, SnapshotRow.snapshot_date == prev_day
                ),
                conn,
            )
        df["snapshot_date"] = str(prev_day)
        return df


def open_history(database_url: str | None, history_dir: str) -> History:
    return SqlHistory(database_url) if database_url else CsvHistory(history_dir)
