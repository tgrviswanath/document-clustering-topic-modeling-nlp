from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.service import run_lda, run_nmf, run_kmeans
from app.core.config import settings

router = APIRouter(prefix="/api/v1/nlp", tags=["clustering"])


class DocsInput(BaseModel):
    texts: list[str]
    n_topics: int = settings.N_TOPICS
    n_top_words: int = settings.N_TOP_WORDS


class ClusterInput(BaseModel):
    texts: list[str]
    n_clusters: int = settings.N_CLUSTERS


def _validate(texts: list[str], min_docs: int = 2):
    if len(texts) < min_docs:
        raise HTTPException(status_code=400, detail=f"Need at least {min_docs} documents")
    if any(not t.strip() for t in texts):
        raise HTTPException(status_code=400, detail="Empty documents are not allowed")


@router.post("/lda")
def lda_endpoint(body: DocsInput):
    _validate(body.texts, min_docs=body.n_topics)
    return run_lda(body.texts, body.n_topics, body.n_top_words)


@router.post("/nmf")
def nmf_endpoint(body: DocsInput):
    _validate(body.texts, min_docs=body.n_topics)
    return run_nmf(body.texts, body.n_topics, body.n_top_words)


@router.post("/cluster")
def cluster_endpoint(body: ClusterInput):
    _validate(body.texts, min_docs=body.n_clusters)
    return run_kmeans(body.texts, body.n_clusters)
