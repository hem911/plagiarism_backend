# plagiarism_backend/checker/google_api.py
import os
import requests

GOOGLE_API_KEY = os.getenv("AIzaSyB-3S5jsGvs6-tcgi2rTfjwMvzdINUErTI")
GOOGLE_CX = os.getenv("82767b0837f6e4688")
GOOGLE_API_URL = "https://www.googleapis.com/customsearch/v1"

def search_google(query, num=3):
    """
    Returns a list of results with 'title', 'snippet', 'link'. If API not configured, returns [].
    """
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        return []
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": num,
    }
    try:
        r = requests.get(GOOGLE_API_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        items = data.get("items", [])
        results = []
        for item in items:
            results.append({
                "title": item.get("title"),
                "snippet": item.get("snippet"),
                "link": item.get("link"),
            })
        return results
    except Exception:
        # On error, return empty list to keep pipeline running
        return []
