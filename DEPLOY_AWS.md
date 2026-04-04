# AWS Deployment Guide — Project 11 Document Clustering & Topic Modeling

---

## AWS Services for Document Clustering & Topic Modeling

### 1. Ready-to-Use AI (No Model Needed)

| Service                    | What it does                                                                 | When to use                                        |
|----------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Amazon Comprehend**      | Built-in topic modeling — discovers topics across document collections       | Replace your LDA/NMF pipeline with one API call    |
| **Amazon Bedrock**         | Claude/Titan for zero-shot topic labeling and document clustering via prompt | When you need interpretable topic labels           |
| **Amazon OpenSearch**      | k-NN vector clustering over document embeddings                              | When you need scalable document clustering         |

> **Amazon Comprehend Topic Modeling** is the direct replacement for your LDA/NMF pipeline. Submit a batch of documents → get topic assignments and top keywords per topic.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **AWS App Runner**         | Run backend container — simplest, no VPC or cluster needed          | Quickest path to production                           |
| **Amazon ECS Fargate**     | Run backend + nlp-service containers in a private VPC               | Best match for your current microservice architecture |
| **Amazon ECR**             | Store your Docker images                                            | Used with App Runner, ECS, or EKS                     |

### 3. Train and Manage Your Model

| Service                         | What it does                                                        | When to use                                           |
|---------------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **AWS SageMaker**               | Run LDA/NMF training jobs, track experiments, deploy endpoints      | Upgrade your pipeline to a full ML workflow           |
| **SageMaker Built-in LDA**      | SageMaker's built-in LDA algorithm — no code needed                 | Scalable topic modeling on large document sets        |

### 4. Frontend Hosting

| Service               | What it does                                                                  |
|-----------------------|-------------------------------------------------------------------------------|
| **Amazon S3**         | Host your React build as a static website                                     |
| **Amazon CloudFront** | CDN in front of S3 — HTTPS, low latency globally                              |

### 5. Supporting Services

| Service                  | Purpose                                                                   |
|--------------------------|---------------------------------------------------------------------------|
| **Amazon S3**            | Store document collections and clustering results                         |
| **AWS Secrets Manager**  | Store API keys and connection strings instead of .env files               |
| **Amazon CloudWatch**    | Track clustering latency, topic coherence, request volume                 |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  S3 + CloudFront — React Frontend                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  AWS App Runner / ECS Fargate — Backend (FastAPI :8000)     │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ ECS Fargate       │    │ Amazon Comprehend Topic Modeling   │
│ NLP Service :8001 │    │ + SageMaker Built-in LDA           │
│ LDA/NMF/KMeans    │    │ No model maintenance needed        │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
aws configure
AWS_REGION=eu-west-2
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
```

---

## Step 1 — Create ECR and Push Images

```bash
aws ecr create-repository --repository-name docclustering/nlp-service --region $AWS_REGION
aws ecr create-repository --repository-name docclustering/backend --region $AWS_REGION
ECR=$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR
docker build -f docker/Dockerfile.nlp-service -t $ECR/docclustering/nlp-service:latest ./nlp-service
docker push $ECR/docclustering/nlp-service:latest
docker build -f docker/Dockerfile.backend -t $ECR/docclustering/backend:latest ./backend
docker push $ECR/docclustering/backend:latest
```

---

## Step 2 — Deploy with App Runner

```bash
aws apprunner create-service \
  --service-name docclustering-backend \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ECR'/docclustering/backend:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "NLP_SERVICE_URL": "http://nlp-service:8001"
        }
      }
    }
  }' \
  --instance-configuration '{"Cpu": "1 vCPU", "Memory": "2 GB"}' \
  --region $AWS_REGION
```

---

## Option B — Use Amazon Comprehend Topic Modeling

```python
import boto3, time

comprehend = boto3.client("comprehend", region_name="eu-west-2")

def start_topic_modeling(s3_input: str, s3_output: str, num_topics: int = 10) -> str:
    response = comprehend.start_topics_detection_job(
        InputDataConfig={"S3Uri": s3_input, "InputFormat": "ONE_DOC_PER_LINE"},
        OutputDataConfig={"S3Uri": s3_output},
        DataAccessRoleArn="arn:aws:iam::<account>:role/ComprehendRole",
        NumberOfTopics=num_topics
    )
    return response["JobId"]

def get_job_status(job_id: str) -> dict:
    result = comprehend.describe_topics_detection_job(JobId=job_id)
    return {"status": result["TopicsDetectionJobProperties"]["JobStatus"]}
```

Add to requirements.txt: `boto3>=1.34.0`

---

## CI/CD — GitHub Actions

```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-west-2
      - uses: aws-actions/amazon-ecr-login@v2
      - run: |
          docker build -f docker/Dockerfile.backend \
            -t ${{ secrets.ECR_REGISTRY }}/docclustering/backend:${{ github.sha }} ./backend
          docker push ${{ secrets.ECR_REGISTRY }}/docclustering/backend:${{ github.sha }}
```

---

## Estimated Monthly Cost

| Service                    | Tier              | Est. Cost          |
|----------------------------|-------------------|--------------------|
| App Runner (backend)       | 1 vCPU / 2 GB     | ~$20–25/month      |
| App Runner (nlp-service)   | 1 vCPU / 2 GB     | ~$20–25/month      |
| ECR + S3 + CloudFront      | Standard          | ~$3–7/month        |
| Amazon Comprehend          | Pay per unit      | ~$1–5/month        |
| **Total (Option A)**       |                   | **~$43–57/month**  |
| **Total (Option B)**       |                   | **~$24–37/month**  |

For exact estimates → https://calculator.aws

---

## Teardown

```bash
aws ecr delete-repository --repository-name docclustering/backend --force
aws ecr delete-repository --repository-name docclustering/nlp-service --force
```
