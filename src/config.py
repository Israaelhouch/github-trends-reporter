"""Central configuration, read from environment variables (and an optional .env file).

`load_dotenv()` never overrides variables that are already set, so values injected by
Docker Compose or GitHub Actions always win over a local .env file.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    return value if value not in (None, "") else default


# -------------------------------
# GitHub API
# -------------------------------
GITHUB_API_URL = "https://api.github.com/search/repositories"
GITHUB_TOKEN = _env("GITHUB_TOKEN")
PER_PAGE = 100
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3

# -------------------------------
# Pipeline defaults
# -------------------------------
TOPIC = _env("TOPIC", "machine learning")
TOP_N = int(_env("TOP_N", "200"))
RISING_DAYS = int(_env("RISING_DAYS", "30"))  # "rising" = created within the last N days
RISING_N = int(_env("RISING_N", "30"))

# -------------------------------
# AI insights (optional, free): an open model served by Ollama
# -------------------------------
OLLAMA_HOST = _env("OLLAMA_HOST", "http://localhost:11434")
AI_MODEL = _env("AI_MODEL", "qwen2.5:3b")
AI_TIMEOUT = int(_env("AI_TIMEOUT", "600"))  # seconds; CPU inference on CI runners is slow

# -------------------------------
# Email (optional)
# -------------------------------
EMAIL_USER = _env("EMAIL_USER")
# An App Password, NOT your Gmail login password. Spaces/newlines from copy-pasting are removed.
EMAIL_PASS = "".join((_env("EMAIL_PASS") or "").split()) or None
EMAIL_RECEIVER = _env("EMAIL_TO")
EMAIL_SMTP_SERVER = _env("EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(_env("EMAIL_SMTP_PORT", "587"))

# -------------------------------
# Storage
# -------------------------------
# By default, history is kept as small CSV snapshots in HISTORY_DIR (git-friendly).
# Set DATABASE_URL (e.g. PostgreSQL) to keep it in a database instead.
DATABASE_URL = _env("DATABASE_URL")
HISTORY_DIR = _env("HISTORY_DIR", "data/history")
DATA_OUTPUT_DIR = _env("DATA_OUTPUT_DIR", "data/outputs")
REPORTS_DIR = _env("REPORTS_DIR", "reports")
LOG_DIR = _env("LOG_DIR", "logs")
