"""
Top headline retrieval via NewsAPI (https://newsapi.org).
"""

import requests

from config import NEWS_API_KEY, NEWS_COUNTRY, NEWS_MAX_HEADLINES

BASE_URL = "https://newsapi.org/v2/top-headlines"


def get_headlines() -> str:
    """Return a spoken-friendly rundown of the day's top headlines."""
    if not NEWS_API_KEY:
        return (
            "I can't read the news yet because no NewsAPI key is configured. "
            "Add one to config.py or the NEWS_API_KEY environment variable."
        )

    params = {
        "apiKey": NEWS_API_KEY,
        "country": NEWS_COUNTRY,
        "pageSize": NEWS_MAX_HEADLINES,
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
    except requests.RequestException as e:
        return f"I couldn't reach the news service: {e}"

    if response.status_code != 200:
        return "The news service returned an error, please try again later."

    articles = response.json().get("articles", [])
    if not articles:
        return "I couldn't find any headlines right now."

    lines = [f"{i}. {a['title']}" for i, a in enumerate(articles, start=1)]
    spoken = "Here are today's top headlines. " + " ... ".join(lines)
    return spoken