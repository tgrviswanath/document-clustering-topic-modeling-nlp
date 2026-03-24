from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)

MOCK_LDA = {
    "method": "LDA", "n_topics": 2,
    "topics": [{"id": 0, "words": ["market", "stock"]}, {"id": 1, "words": ["science", "space"]}],
    "doc_topic_distribution": [{"doc_index": 0, "dominant_topic": 0, "distribution": [0.8, 0.2]}],
}

MOCK_CLUSTER = {
    "method": "KMeans", "n_clusters": 2,
    "clusters": [{"cluster_id": 0, "top_terms": ["market", "stock"], "size": 1}],
    "doc_assignments": [{"doc_index": 0, "cluster_id": 0}],
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


@patch("app.core.service.run_lda", new_callable=AsyncMock, return_value=MOCK_LDA)
def test_lda_endpoint(mock_lda):
    r = client.post("/api/v1/lda", json={"texts": ["doc1", "doc2"], "n_topics": 2})
    assert r.status_code == 200
    assert r.json()["method"] == "LDA"


@patch("app.core.service.run_nmf", new_callable=AsyncMock, return_value=MOCK_LDA)
def test_nmf_endpoint(mock_nmf):
    r = client.post("/api/v1/nmf", json={"texts": ["doc1", "doc2"], "n_topics": 2})
    assert r.status_code == 200


@patch("app.core.service.run_kmeans", new_callable=AsyncMock, return_value=MOCK_CLUSTER)
def test_cluster_endpoint(mock_cluster):
    r = client.post("/api/v1/cluster", json={"texts": ["doc1", "doc2"], "n_clusters": 2})
    assert r.status_code == 200
    assert r.json()["method"] == "KMeans"
