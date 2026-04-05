import asyncio
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
async def lda_endpoint(body: DocsInput):
    _validate(body.texts, min_docs=body.n_topics)
    try:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, run_lda, body.texts, body.n_topics, body.n_top_words)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/nmf")
async def nmf_endpoint(body: DocsInput):
    _validate(body.texts, min_docs=body.n_topics)
    try:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, run_nmf, body.texts, body.n_topics, body.n_top_words)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cluster")
async def cluster_endpoint(body: ClusterInput):
    _validate(body.texts, min_docs=body.n_clusters)
    try:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, run_kmeans, body.texts, body.n_clusters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
