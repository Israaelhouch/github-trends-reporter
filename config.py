import os
# preventing interference from a local .env file inside the container.
# from dotenv import load_dotenv 
# load_dotenv()

# -------------------------------
# GitHub API Settings
# -------------------------------
GITHUB_API_URL = "https://api.github.com/search/repositories"
HEADERS = {"Accept": "application/vnd.github.v3+json"}
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") 
PER_PAGE = 100

# -------------------------------
# Fetcher Default Parameters
# -------------------------------
TOP_N = 200
TOPIC = "machine learning"

# -------------------------------
# Email Settings
# -------------------------------
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")  # This is an App Password, NOT your Gmail login password!
EMAIL_RECEIVER = os.getenv("EMAIL_TO")
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587

# -------------------------------
# Database Settings
# -------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres_user:postgres_password@localhost:5432/github_trends"
)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set!")

# -------------------------------
# Paths / Folders
# -------------------------------
DATA_RAW_DIR = "data/raw"
DATA_OUTPUT_DIR = "data/outputs"
LOG_DIR = "logs"
ASSETS_DIR = "assets"