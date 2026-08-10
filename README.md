---
title: AI Sentiment API
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
---

# 🚀 AI Sentiment Analysis App

![CI](https://github.com/yigitliman/ai-sentiment-api/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A containerized full-stack application that performs real-time sentiment analysis using NLP. Built with a **FastAPI** backend, **Streamlit** frontend, and a live **monitoring dashboard**.

**🔴 Live Demo:** [yliman-ai-sentiment-api.hf.space](https://yliman-ai-sentiment-api.hf.space)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Backend API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| ML Model | Hugging Face Transformers (DistilBERT) |
| Database | SQLite |
| Containerization | Docker |
| Testing | Pytest + HTTPX |

---

## Model Performance

The API serves `distilbert-base-uncased-finetuned-sst-2-english`, pinned by name so an upstream change to the pipeline default cannot silently swap the model out. Measured on the **SST-2 validation split (872 held-out sentences)**:

| Metric | Value |
|---|---|
| Accuracy | 0.911 |
| F1 | 0.914 |
| Mean confidence | 0.983 |
| Accuracy, positive / negative | 0.930 / 0.890 |

Single-request latency on CPU, with no GPU and no batching: **p50 37 ms, p95 64 ms, p99 80 ms**. The model is loaded once at import and reused across requests, so these are steady-state numbers rather than cold starts.

---

## Features

- **Real-time sentiment analysis** — classifies text as POSITIVE or NEGATIVE with a confidence score
- **REST API** with auto-generated Swagger docs (`/docs`)
- **MLOps dashboard** — live pie chart and recent prediction history via analytics endpoints
- **Persistent logging** — every prediction is stored in SQLite
- **Fully containerized** — single Docker image runs both backend and frontend
- **Test suite** — endpoint, model, and database tests with Pytest

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/analyze` | Run sentiment analysis on text |
| GET | `/logs` | Retrieve recent predictions |
| GET | `/stats` | Get sentiment distribution counts |
| GET | `/docs` | Interactive Swagger UI |

---

## How to Run

### With Docker (recommended)

```bash
docker build -t ai-sentiment-app .
docker run -p 7860:7860 ai-sentiment-app
```

Open [http://localhost:7860](http://localhost:7860) for the frontend.

### Locally

```bash
pip install -r requirements.txt
python run.py
```

---

## Example

**Request:**
```json
POST /analyze
{ "text": "I finally deployed my first AI model and it works perfectly!" }
```

**Response:**
```json
{ "label": "POSITIVE", "score": 0.9997 }
```

---

## Running Tests

```bash
pytest -v
```

The same suite runs on every push and pull request via GitHub Actions, followed by a Docker
image build.
