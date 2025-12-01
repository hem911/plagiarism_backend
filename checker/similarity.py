# plagiarism_backend/checker/similarity.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_best_similarity(chunk_text, results):
    """
    results: list of {'title','snippet','link'}
    returns: best_similarity (float between 0 and 1), best_result (dict)
    If no results, returns 0.0, None
    """
    if not results:
        return 0.0, None

    # Build corpus: chunk first, then snippets/titles
    docs = [chunk_text]
    for r in results:
        snippet = r.get("snippet") or ""
        title = r.get("title") or ""
        docs.append(title + " . " + snippet)
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf = vectorizer.fit_transform(docs)
        # cosine similarity between first doc (chunk) and others
        sims = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
        best_idx = int(sims.argmax())
        best_score = float(sims[best_idx])
        best_result = results[best_idx]
        return best_score, best_result
    except Exception:
        return 0.0, None
