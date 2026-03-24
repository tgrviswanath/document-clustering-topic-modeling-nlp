# Project 11 - Document Clustering & Topic Modeling

Microservice NLP system for unsupervised document analysis using LDA, NMF, and KMeans.

## Architecture

```
Frontend :3000  →  Backend :8000  →  NLP Service :8001
  React/MUI        FastAPI/httpx      FastAPI/scikit-learn/spaCy
```

## What It Does

| Feature | Method | Tools |
|---|---|---|
| Topic Modeling | LDA | Gensim / scikit-learn |
| Topic Modeling | NMF | scikit-learn |
| Document Clustering | KMeans | scikit-learn TF-IDF |
| Preprocessing | Lemmatization + stopword removal | spaCy |

## Local Run

```bash
# Terminal 1 - NLP Service
cd nlp-service && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8001

# Terminal 2 - Backend
cd backend && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 3 - Frontend
cd frontend && npm install && npm start
```

- API docs: http://localhost:8001/docs (NLP Service)
- API docs: http://localhost:8000/docs (Backend)
- UI: http://localhost:3000

## Docker

```bash
docker-compose up --build
```

## Dataset

Uses 20 Newsgroups or any plain text documents (one per line in the UI).
