from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GitHubRepo(Base):
    __tablename__ = "github_repos"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    html_url = Column(String, nullable=False)
    stargazers_count = Column(Integer)
    language = Column(String)
    owner = Column(String)
    fork = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    fetched_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"<GitHubRepo(full_name={self.full_name}, topic={self.topic})>"
