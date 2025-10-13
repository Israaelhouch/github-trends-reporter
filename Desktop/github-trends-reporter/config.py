import os

# GitHub API
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Email settings
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587

# Paths
DATA_RAW_DIR = "data/raw"
DATA_OUTPUT_DIR = "data/outputs"
LOG_DIR = "logs"
ASSETS_DIR = "assets"
