# Azure Deployment Guide — Project 11 Document Clustering & Topic Modeling

---

## Azure Services for Document Clustering & Topic Modeling

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Azure AI Language — Key Phrases**  | Extract key phrases as lightweight topic signals from documents              | Replace your LDA/NMF keyword extraction            |
| **Azure OpenAI Service**             | GPT-4 for zero-shot topic labeling and document clustering via prompt        | When you need interpretable topic labels           |
| **Azure AI Search**                  | Vector clustering over document embeddings with faceted navigation           | When you need scalable document clustering         |

> **Azure OpenAI with text-embedding-ada-002** + **Azure AI Search** together replace your TF-IDF + KMeans pipeline with managed vector clustering.

### 2. Host Your Own Model (Keep Current Stack)

| Service                        | What it does                                                        | When to use                                           |
|--------------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Azure Container Apps**       | Run your 3 Docker containers (frontend, backend, nlp-service)       | Best match for your current microservice architecture |
| **Azure Container Registry**   | Store your Docker images                                            | Used with Container Apps or AKS                       |

### 3. Train and Manage Your Model

| Service                        | What it does                                                              | When to use                                           |
|--------------------------------|---------------------------------------------------------------------------|-------------------------------------------------------|
| **Azure Machine Learning**     | Run LDA/NMF training jobs, track experiments, deploy endpoints            | Upgrade your pipeline to a full ML workflow           |

### 4. Frontend Hosting

| Service                   | What it does                                                               |
|---------------------------|----------------------------------------------------------------------------|
| **Azure Static Web Apps** | Host your React frontend — free tier available, auto CI/CD from GitHub     |

### 5. Supporting Services

| Service                       | Purpose                                                                  |
|-------------------------------|--------------------------------------------------------------------------|
| **Azure Blob Storage**        | Store document collections and clustering results                        |
| **Azure Key Vault**           | Store API keys and connection strings instead of .env files              |
| **Azure Monitor + App Insights** | Track clustering latency, topic coherence, request volume            |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Azure Static Web Apps — React Frontend                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Azure Container Apps — Backend (FastAPI :8000)             │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Container Apps    │    │ Azure OpenAI Embeddings            │
│ NLP Service :8001 │    │ + Azure AI Search (vector cluster) │
│ LDA/NMF/KMeans    │    │ No model maintenance needed        │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
az login
az group create --name rg-doc-clustering --location uksouth
az extension add --name containerapp --upgrade
```

---

## Step 1 — Create Container Registry and Push Images

```bash
az acr create --resource-group rg-doc-clustering --name docclusteringacr --sku Basic --admin-enabled true
az acr login --name docclusteringacr
ACR=docclusteringacr.azurecr.io
docker build -f docker/Dockerfile.nlp-service -t $ACR/nlp-service:latest ./nlp-service
docker push $ACR/nlp-service:latest
docker build -f docker/Dockerfile.backend -t $ACR/backend:latest ./backend
docker push $ACR/backend:latest
```

---

## Step 2 — Deploy Container Apps

```bash
az containerapp env create --name docclustering-env --resource-group rg-doc-clustering --location uksouth

az containerapp create \
  --name nlp-service --resource-group rg-doc-clustering \
  --environment docclustering-env --image $ACR/nlp-service:latest \
  --registry-server $ACR --target-port 8001 --ingress internal \
  --min-replicas 1 --max-replicas 3 --cpu 1 --memory 2.0Gi

az containerapp create \
  --name backend --resource-group rg-doc-clustering \
  --environment docclustering-env --image $ACR/backend:latest \
  --registry-server $ACR --target-port 8000 --ingress external \
  --min-replicas 1 --max-replicas 5 --cpu 0.5 --memory 1.0Gi \
  --env-vars NLP_SERVICE_URL=http://nlp-service:8001
```

---

## Option B — Use Azure OpenAI Embeddings + Azure AI Search

```python
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-01"
)

def embed_documents(texts: list) -> list:
    response = openai_client.embeddings.create(input=texts, model="text-embedding-ada-002")
    return [item.embedding for item in response.data]
```

Add to requirements.txt: `openai>=1.12.0 azure-search-documents>=11.4.0`

---

## CI/CD — GitHub Actions

```yaml
name: Deploy to Azure
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      - run: az acr login --name docclusteringacr
      - run: |
          docker build -f docker/Dockerfile.backend -t docclusteringacr.azurecr.io/backend:${{ github.sha }} ./backend
          docker push docclusteringacr.azurecr.io/backend:${{ github.sha }}
          az containerapp update --name backend --resource-group rg-doc-clustering \
            --image docclusteringacr.azurecr.io/backend:${{ github.sha }}
```

---

## Estimated Monthly Cost

| Service                  | Tier      | Est. Cost         |
|--------------------------|-----------|-------------------|
| Container Apps (backend) | 0.5 vCPU  | ~$10–15/month     |
| Container Apps (nlp-svc) | 1 vCPU    | ~$15–20/month     |
| Container Registry       | Basic     | ~$5/month         |
| Static Web Apps          | Free      | $0                |
| Azure OpenAI Embeddings  | Pay per token | ~$2–5/month   |
| **Total (Option A)**     |           | **~$30–40/month** |
| **Total (Option B)**     |           | **~$17–25/month** |

For exact estimates → https://calculator.azure.com

---

## Teardown

```bash
az group delete --name rg-doc-clustering --yes --no-wait
```
