from datetime import date

from sqlalchemy import Date, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SnapshotRow(Base):
    """Star/fork counts for one repository on one day - all that week-over-week growth needs."""

    __tablename__ = "star_snapshots"
    __table_args__ = (Index("ix_snapshot_topic_date", "topic", "snapshot_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic: Mapped[str] = mapped_column(String(200))
    snapshot_date: Mapped[date] = mapped_column(Date)
    full_name: Mapped[str] = mapped_column(String(300))
    stargazers_count: Mapped[int] = mapped_column(Integer)
    forks_count: Mapped[int] = mapped_column(Integer)
