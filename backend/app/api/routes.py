from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.service import run_lda, run_nmf, run_kmeans
import httpx

router = APIRouter(prefix="/api/v1", tags=["clustering"])


class DocsInput(BaseModel):
    texts: list[str]
    n_topics: int = 5
    n_top_words: int = 10


class ClusterInput(BaseModel):
    texts: list[str]
    n_clusters: int = 5


def _handle(e: Exception):
    if isinstance(e, httpx.ConnectError):
        raise HTTPException(status_code=503, detail="NLP service unavailable")
    if isinstance(e, httpx.HTTPStatusError):
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/lda")
async def lda(body: DocsInput):
    try:
        return await run_lda(body.texts, body.n_topics, body.n_top_words)
    except Exception as e:
        _handle(e)


@router.post("/nmf")
async def nmf(body: DocsInput):
    try:
        return await run_nmf(body.texts, body.n_topics, body.n_top_words)
    except Exception as e:
        _handle(e)


@router.post("/cluster")
async def cluster(body: ClusterInput):
    try:
        return await run_kmeans(body.texts, body.n_clusters)
    except Exception as e:
        _handle(e)
