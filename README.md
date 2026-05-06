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

A containerized, production-ready full-stack AI application that performs real-time sentiment analysis using NLP. Built with a **FastAPI** backend, **Streamlit** frontend, and a live **MLOps monitoring dashboard**.

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
pytest test_main.py -v
```
