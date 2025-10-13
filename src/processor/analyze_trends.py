import pandas as pd
from datetime import datetime
from collections import Counter
import re
from src.utils.logger import setup_logger

logger = setup_logger("processor")

def analyze_trends(current_data, previous_data=None, topic="general"):
    """
    Analyze GitHub repository trends and return structured insights.
    """
    logger.info(f"Starting GitHub trend analysis for topic '{topic}'...")

    # --- Ensure column compatibility
    df = pd.DataFrame(current_data)
    
    # --- Ignore forked repos
    df = df[df['fork'] == False]

    # --- Top Languages & Share
    top_languages = df['language'].value_counts().head(10).to_dict()
    language_share = {k: round(v / len(df) * 100, 2) for k, v in top_languages.items()}

    # --- Top Organizations
    top_organizations = df['owner'].value_counts().head(10).to_dict()

    # --- Top Repositories by Stars
    top_repos = df.nlargest(10, 'stargazers_count')[['full_name', 'stargazers_count', 'html_url']].to_dict(orient='records')

    # --- Keywords in repo names
    words = " ".join(df['full_name'].astype(str)).lower()
    words = re.findall(r'\b\w+\b', words)
    keywords = dict(Counter(words).most_common(10))

    results = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "topic": topic,
        "total_repos": len(df),
        "forked_repos": int(current_data['fork'].sum()),
        "top_languages": top_languages,
        "language_share": language_share,
        "top_organizations": top_organizations,
        "top_repos": top_repos,
        "keywords": keywords
    }

    # --- Compare with previous data
    if previous_data is not None and not previous_data.empty:
        prev_df = pd.DataFrame(previous_data)
        prev_names = set(prev_df['full_name'])
        curr_names = set(df['full_name'])
        new_repos = list(curr_names - prev_names)

        merged = df.merge(prev_df, on='full_name', suffixes=('', '_prev'))
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

    logger.info(f"Trend analysis for topic '{topic}' complete.")
    return results
