import requests
import pandas as pd
from datetime import datetime
import time
from src.utils.logger import setup_logger
from config import GITHUB_API_URL, HEADERS, PER_PAGE

logger = setup_logger("fetcher")

def fetch_trending_repos(topic: str = "machine learning", top_n: int = 200, delay: float = 1.0):
    """
    Fetch top trending repositories for a given topic from GitHub.
    Handles pagination and basic rate limiting.
    Raises exception if no repositories could be fetched.
    """
    repos = []
    total_pages = (top_n + PER_PAGE - 1) // PER_PAGE 
    logger.info(f"Fetching {top_n} repositories for topic '{topic}' over {total_pages} pages")

    for page in range(1, total_pages + 1):
        params = {
            "q": f"{topic} in:name,description",
            "sort": "stars",
            "order": "desc",
            "per_page": PER_PAGE,
            "page": page
        }

        logger.info(f"Page {page}/{total_pages} request to GitHub API...")
        try:
            response = requests.get(GITHUB_API_URL, headers=HEADERS, params=params)
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            continue

        if response.status_code == 403:
            logger.warning("Rate limit hit. Waiting 60 seconds...")
            time.sleep(60)
            continue

        if not response.ok:
            logger.error(f"Request failed with status code {response.status_code}: {response.text}")
            continue

        data = response.json().get("items", [])
        logger.info(f"Retrieved {len(data)} repos from page {page}")
        repos.extend(data)
        time.sleep(delay)

    if not repos:
        raise ValueError(f"No repositories fetched for topic '{topic}' — check API or network.")

    df = pd.DataFrame([{
        "full_name": repo["full_name"],
        "html_url": repo["html_url"],
        "stargazers_count": repo["stargazers_count"],
        "language": repo["language"],
        "owner": repo["owner"]["login"],
        "fork": repo["fork"],
        "created_at": repo["created_at"],
        "updated_at": repo["updated_at"],
        "fetched_at": datetime.utcnow().strftime("%Y-%m-%d")
    } for repo in repos])

    logger.info(f"Total fetched repos: {len(df)} for topic '{topic}'")
    return df
