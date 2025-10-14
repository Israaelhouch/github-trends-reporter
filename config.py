import os
from dotenv import load_dotenv
load_dotenv()

# GitHub API
GITHUB_API_URL = "https://api.github.com/search/repositories"
HEADERS = {"Accept": "application/vnd.github.v3+json"}
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
PER_PAGE = 100

# Fetcher params
TOP_N = 200
TOPIC = "machine learning"

# Email settings
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587

# Paths
DATA_RAW_DIR = "data/raw"
DATA_OUTPUT_DIR = "data/outputs"
LOG_DIR = "logs"
ASSETS_DIR = "assets"
