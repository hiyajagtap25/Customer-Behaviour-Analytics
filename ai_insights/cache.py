import json
import os


CACHE_FILE = "ai_cache.json"


def load_cache():
    """
    Load cached AI insights from JSON file.
    Returns empty dict if file doesn't exist.
    """

    if not os.path.exists(CACHE_FILE):
        return {}

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cache(cache):
    """
    Save insights dictionary to JSON file.
    """

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def clear_cache():
    """
    Deletes cache file.
    Useful for regenerating insights.
    """

    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)