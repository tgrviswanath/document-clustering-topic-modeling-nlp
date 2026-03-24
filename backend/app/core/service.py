import httpx
from app.core.config import settings

NLP_URL = settings.NLP_SERVICE_URL


async def run_lda(texts: list[str], n_topics: int, n_top_words: int) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{NLP_URL}/api/v1/nlp/lda",
            json={"texts": texts, "n_topics": n_topics, "n_top_words": n_top_words},
            timeout=120.0,
        )
        r.raise_for_status()
        return r.json()


async def run_nmf(texts: list[str], n_topics: int, n_top_words: int) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{NLP_URL}/api/v1/nlp/nmf",
            json={"texts": texts, "n_topics": n_topics, "n_top_words": n_top_words},
            timeout=120.0,
        )
        r.raise_for_status()
        return r.json()


async def run_kmeans(texts: list[str], n_clusters: int) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{NLP_URL}/api/v1/nlp/cluster",
            json={"texts": texts, "n_clusters": n_clusters},
            timeout=120.0,
        )
        r.raise_for_status()
        return r.json()
