import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def semantic_search(df, query, top_k=10):
    if not query.strip():
        return pd.DataFrame()
    searchable = df.fillna("").astype(str)
    corpus = searchable.apply(lambda row: " | ".join(row.values), axis=1)
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(corpus.tolist() + [query])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    result = df.copy()
    result["_semantic_score"] = scores
    return result.sort_values("_semantic_score", ascending=False).head(top_k)
