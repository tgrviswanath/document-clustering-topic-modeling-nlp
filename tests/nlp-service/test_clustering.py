from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

SAMPLE_TEXTS = [
    "The stock market rallied on strong earnings from tech companies.",
    "Federal Reserve paused interest rate hikes amid cooling inflation.",
    "Apple unveiled a new iPhone with advanced AI capabilities.",
    "Scientists discovered an exoplanet in a nearby star system.",
    "The Premier League title race intensified with a dramatic draw.",
    "NASA completed a lunar orbit test for the Artemis mission.",
    "Google updated its search algorithm with large language models.",
    "WHO issued new guidelines on antibiotic resistance prevention.",
]


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_lda():
    r = client.post("/api/v1/nlp/lda", json={"texts": SAMPLE_TEXTS, "n_topics": 3, "n_top_words": 5})
    assert r.status_code == 200
    data = r.json()
    assert data["method"] == "LDA"
    assert len(data["topics"]) == 3
    assert all(len(t["words"]) == 5 for t in data["topics"])
    assert len(data["doc_topic_distribution"]) == len(SAMPLE_TEXTS)


def test_nmf():
    r = client.post("/api/v1/nlp/nmf", json={"texts": SAMPLE_TEXTS, "n_topics": 3, "n_top_words": 5})
    assert r.status_code == 200
    data = r.json()
    assert data["method"] == "NMF"
    assert len(data["topics"]) == 3


def test_cluster():
    r = client.post("/api/v1/nlp/cluster", json={"texts": SAMPLE_TEXTS, "n_clusters": 3})
    assert r.status_code == 200
    data = r.json()
    assert data["method"] == "KMeans"
    assert len(data["clusters"]) == 3
    assert len(data["doc_assignments"]) == len(SAMPLE_TEXTS)


def test_lda_too_few_docs():
    r = client.post("/api/v1/nlp/lda", json={"texts": ["only one doc"], "n_topics": 3})
    assert r.status_code == 400


def test_cluster_too_few_docs():
    r = client.post("/api/v1/nlp/cluster", json={"texts": ["doc1", "doc2"], "n_clusters": 5})
    assert r.status_code == 400
