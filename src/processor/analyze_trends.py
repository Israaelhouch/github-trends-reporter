import re
import pandas as pd
from datetime import datetime
from collections import Counter
from src.utils.logger import setup_logger

logger = setup_logger("processor")

def analyze_trends(current_data, previous_data, topic="general"):
    """
    Analyze GitHub repository trends and return structured insights.
    """
    logger.info(f"Starting GitHub trend analysis for topic '{topic}'...")

    # --- Ignore forked repos
    current_data = current_data[current_data['fork'] == False]

    # --- Top Languages & Share
    top_languages = current_data['language'].value_counts().head(10).to_dict()
    language_share = {k: round(v / len(current_data) * 100, 2) for k, v in top_languages.items()}

    # --- Top Organizations
    top_organizations = current_data['owner'].value_counts().head(10).to_dict()

    # --- Top Repositories by Stars
    top_repos = current_data.nlargest(10, 'stargazers_count')[['full_name', 'stargazers_count', 'html_url']].to_dict(orient='records')

    # --- Keywords in repo names
    words = " ".join(current_data['full_name'].astype(str)).lower()
    words = re.findall(r'\b\w+\b', words)
    keywords = dict(Counter(words).most_common(10))

    results = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "topic": topic,
        "total_repos": len(current_data),
        "forked_repos": int(current_data['fork'].sum()),
        "top_languages": top_languages,
        "language_share": language_share,
        "top_organizations": top_organizations,
        "top_repos": top_repos,
        "keywords": keywords
    }

    # --- Compare with previous data
    if not(previous_data is None or previous_data.empty) :
        prev_names = set(previous_data['full_name'])
        curr_names = set(current_data['full_name'])
        new_repos = list(curr_names - prev_names)

        merged = current_data.merge(previous_data, on='full_name', suffixes=('', '_prev'))
        merged['stars_gained'] = merged['stargazers_count'] - merged['stargazers_count_prev']
        merged['stars_growth_pct'] = ((merged['stargazers_count'] - merged['stargazers_count_prev']) /
                                      merged['stargazers_count_prev'].replace(0, 1)) * 100

        fastest_growing = merged.nlargest(5, 'stars_gained')[['full_name', 'stars_gained']].to_dict(orient='records')
        fastest_growth_pct = merged.nlargest(5, 'stars_growth_pct')[['full_name', 'stars_growth_pct']].to_dict(orient='records')

        results.update({
            "new_trending_repos": new_repos,
            "fastest_growing_repos": fastest_growing,
            "fastest_growth_pct": fastest_growth_pct
        })
        
    return results
