# GCP Deployment Guide — Project 11 Document Clustering & Topic Modeling

---

## GCP Services for Document Clustering & Topic Modeling

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Cloud Natural Language API**       | Extract entities and categories from documents as topic signals              | Replace your LDA/NMF keyword extraction            |
| **Vertex AI Gemini**                 | Gemini Pro for zero-shot topic labeling and document clustering via prompt   | When you need interpretable topic labels           |
| **Vertex AI Matching Engine**        | Vector clustering over document embeddings at scale                          | When you need scalable document clustering         |

> **Vertex AI Embeddings + Matching Engine** together replace your TF-IDF + KMeans pipeline with managed vector clustering.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Cloud Run**              | Run backend + nlp-service containers — serverless, scales to zero   | Best match for your current microservice architecture |
| **Artifact Registry**      | Store your Docker images                                            | Used with Cloud Run or GKE                            |

### 3. Frontend Hosting

| Service                    | What it does                                                              |
|----------------------------|---------------------------------------------------------------------------| 
| **Firebase Hosting**       | Host your React frontend — free tier, auto CI/CD from GitHub              |

### 4. Supporting Services

| Service                        | Purpose                                                                   |
|--------------------------------|---------------------------------------------------------------------------|
| **Cloud Storage**              | Store document collections and clustering results                         |
| **Secret Manager**             | Store API keys and connection strings instead of .env files               |
| **Cloud Monitoring + Logging** | Track clustering latency, topic coherence, request volume                 |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Firebase Hosting — React Frontend                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Cloud Run — Backend (FastAPI :8000)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal HTTPS
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Cloud Run         │    │ Vertex AI Embeddings               │
│ NLP Service :8001 │    │ + Vertex AI Matching Engine        │
│ LDA/NMF/KMeans    │    │ No model maintenance needed        │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
gcloud auth login
gcloud projects create docclustering-project --name="Document Clustering"
gcloud config set project docclustering-project
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com language.googleapis.com \
  aiplatform.googleapis.com storage.googleapis.com cloudbuild.googleapis.com
```

---

## Step 1 — Create Artifact Registry and Push Images

```bash
GCP_REGION=europe-west2
gcloud artifacts repositories create docclustering-repo \
  --repository-format=docker --location=$GCP_REGION
gcloud auth configure-docker $GCP_REGION-docker.pkg.dev
AR=$GCP_REGION-docker.pkg.dev/docclustering-project/docclustering-repo
docker build -f docker/Dockerfile.nlp-service -t $AR/nlp-service:latest ./nlp-service
docker push $AR/nlp-service:latest
docker build -f docker/Dockerfile.backend -t $AR/backend:latest ./backend
docker push $AR/backend:latest
```

---

## Step 2 — Deploy to Cloud Run

```bash
gcloud run deploy nlp-service \
  --image $AR/nlp-service:latest --region $GCP_REGION \
  --port 8001 --no-allow-unauthenticated \
  --min-instances 1 --max-instances 3 --memory 2Gi --cpu 1

NLP_URL=$(gcloud run services describe nlp-service --region $GCP_REGION --format "value(status.url)")

gcloud run deploy backend \
  --image $AR/backend:latest --region $GCP_REGION \
  --port 8000 --allow-unauthenticated \
  --min-instances 1 --max-instances 5 --memory 1Gi --cpu 1 \
  --set-env-vars NLP_SERVICE_URL=$NLP_URL
```

---

## Option B — Use Vertex AI Embeddings

```python
from vertexai.language_models import TextEmbeddingModel
import vertexai

vertexai.init(project="docclustering-project", location="europe-west2")
model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")

def embed_documents(texts: list) -> list:
    embeddings = model.get_embeddings(texts)
    return [e.values for e in embeddings]
```

Add to requirements.txt: `google-cloud-aiplatform>=1.50.0`

---

## CI/CD — GitHub Actions

```yaml
name: Deploy to GCP
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      - uses: google-github-actions/setup-gcloud@v2
      - run: gcloud auth configure-docker europe-west2-docker.pkg.dev
      - run: |
          docker build -f docker/Dockerfile.backend \
            -t europe-west2-docker.pkg.dev/${{ secrets.GCP_PROJECT }}/docclustering-repo/backend:${{ github.sha }} ./backend
          docker push europe-west2-docker.pkg.dev/${{ secrets.GCP_PROJECT }}/docclustering-repo/backend:${{ github.sha }}
          gcloud run deploy backend \
            --image europe-west2-docker.pkg.dev/${{ secrets.GCP_PROJECT }}/docclustering-repo/backend:${{ github.sha }} \
            --region europe-west2 --platform managed
```

---

## Estimated Monthly Cost

| Service                    | Tier                  | Est. Cost          |
|----------------------------|-----------------------|--------------------|
| Cloud Run (backend)        | 1 vCPU / 1 GB         | ~$10–15/month      |
| Cloud Run (nlp-service)    | 1 vCPU / 2 GB         | ~$12–18/month      |
| Artifact Registry          | Storage               | ~$1–2/month        |
| Firebase Hosting           | Free tier             | $0                 |
| Vertex AI Embeddings       | Pay per 1k chars      | ~$1–3/month        |
| **Total (Option A)**       |                       | **~$23–35/month**  |
| **Total (Option B)**       |                       | **~$12–20/month**  |

For exact estimates → https://cloud.google.com/products/calculator

---

## Teardown

```bash
gcloud run services delete backend --region $GCP_REGION --quiet
gcloud run services delete nlp-service --region $GCP_REGION --quiet
gcloud artifacts repositories delete docclustering-repo --location=$GCP_REGION --quiet
gcloud projects delete docclustering-project
```
