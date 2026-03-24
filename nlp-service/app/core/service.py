"""
Document Clustering + Topic Modeling service.
- LDA  : probabilistic topic model (Gensim)
- NMF  : matrix factorization topic model (scikit-learn)
- KMeans: document clustering (scikit-learn TF-IDF + KMeans)
"""
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
import numpy as np
from app.core.preprocess import preprocess
from app.core.config import settings


def _top_words(model, feature_names: list[str], n: int) -> list[list[str]]:
    return [
        [feature_names[i] for i in topic.argsort()[:-n - 1:-1]]
        for topic in model.components_
    ]


def run_lda(texts: list[str], n_topics: int, n_top_words: int) -> dict:
    cleaned = preprocess(texts)
    vec = CountVectorizer(max_df=0.95, min_df=1, max_features=1000)
    dtm = vec.fit_transform(cleaned)
    lda = LatentDirichletAllocation(
        n_components=n_topics, random_state=42, max_iter=20
    )
    doc_topics = lda.fit_transform(dtm)
    feature_names = vec.get_feature_names_out().tolist()
    topics = _top_words(lda, feature_names, n_top_words)
    doc_dominant = doc_topics.argmax(axis=1).tolist()
    return {
        "method": "LDA",
        "n_topics": n_topics,
        "topics": [{"id": i, "words": w} for i, w in enumerate(topics)],
        "doc_topic_distribution": [
            {"doc_index": i, "dominant_topic": int(doc_dominant[i]),
             "distribution": [round(float(v), 4) for v in doc_topics[i]]}
            for i in range(len(texts))
        ],
    }


def run_nmf(texts: list[str], n_topics: int, n_top_words: int) -> dict:
    cleaned = preprocess(texts)
    vec = TfidfVectorizer(max_df=0.95, min_df=1, max_features=1000)
    tfidf = vec.fit_transform(cleaned)
    nmf = NMF(n_components=n_topics, random_state=42, max_iter=400)
    doc_topics = nmf.fit_transform(tfidf)
    feature_names = vec.get_feature_names_out().tolist()
    topics = _top_words(nmf, feature_names, n_top_words)
    doc_dominant = doc_topics.argmax(axis=1).tolist()
    return {
        "method": "NMF",
        "n_topics": n_topics,
        "topics": [{"id": i, "words": w} for i, w in enumerate(topics)],
        "doc_topic_distribution": [
            {"doc_index": i, "dominant_topic": int(doc_dominant[i]),
             "distribution": [round(float(v), 4) for v in doc_topics[i]]}
            for i in range(len(texts))
        ],
    }


def run_kmeans(texts: list[str], n_clusters: int) -> dict:
    cleaned = preprocess(texts)
    vec = TfidfVectorizer(max_df=0.95, min_df=1, max_features=1000)
    tfidf = vec.fit_transform(cleaned)
    tfidf_norm = normalize(tfidf)
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(tfidf_norm)
    feature_names = vec.get_feature_names_out()
    # Top terms per cluster from cluster centers
    cluster_terms = []
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    for i in range(n_clusters):
        terms = [feature_names[ind] for ind in order_centroids[i, :10]]
        cluster_terms.append({"cluster_id": i, "top_terms": terms,
                               "size": int((labels == i).sum())})
    return {
        "method": "KMeans",
        "n_clusters": n_clusters,
        "clusters": cluster_terms,
        "doc_assignments": [
            {"doc_index": i, "cluster_id": int(labels[i])}
            for i in range(len(texts))
        ],
    }
