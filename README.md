---
title: AI Sentiment API
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
---

# Sentiment Analysis Demo (FastAPI + Streamlit)

![CI](https://github.com/yigitliman/ai-sentiment-api/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A DistilBERT sentiment classifier served over a FastAPI REST API, with a Streamlit front end and a SQLite prediction log, packaged as one Docker image and deployed on Hugging Face Spaces.

This repo is the deployed demo. The MLflow tracking, Evidently drift detection and fuller CI for the same model live in [mlops-sentiment-pipeline](https://github.com/yigitliman/mlops-sentiment-pipeline).

**🔴 Live Demo:** [yliman-ai-sentiment-api.hf.space](https://yliman-ai-sentiment-api.hf.space)

> **Note:** text submitted to the live demo is stored in the app's SQLite database and returned by the public, unauthenticated `/logs` endpoint. Do not enter personal, confidential, or sensitive information.

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

## Architecture

One container runs both processes, supervised by `run.py`:

```
run.py            starts and supervises both processes below

  ├─ main.py      FastAPI on :8000
  │               loads distilbert-base-uncased-finetuned-sst-2-english once at
  │               import, serves /analyze /logs /stats, writes every prediction
  │               to api_logs.db (SQLite, on the container filesystem)
  │
  └─ frontend.py  Streamlit on :7860  (the port the Space exposes)
                  calls the API over HTTP at API_URL, renders the result plus a
                  pie chart of /stats and a table of /logs

Dockerfile           single image, both processes, non-root user
.github/workflows/   ci.yml    tests + lint + Docker build and run
                     sync.yml  mirrors main to the Hugging Face Space
```

`main.py`, `frontend.py`, `run.py` and `test_main.py` sit at the repository root rather than in `src/` and `tests/`, because the Space builds from this repo as-is.

---

## Model

The API serves `distilbert-base-uncased-finetuned-sst-2-english`, pinned by name so an upstream change to the pipeline default cannot silently swap the model out. Neither this repo nor its sibling fine-tunes it, so for published metrics see the [model card](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english).

---

## Features

- **Real-time sentiment analysis**: classifies text as POSITIVE or NEGATIVE with a confidence score
- **REST API** with auto-generated Swagger docs (`/docs`)
- **Analytics view**: a pie chart of the POSITIVE/NEGATIVE split and a table of recent predictions, both read from the API's own log
- **Persistent logging**: every prediction is stored in SQLite
- **Fully containerized**: single Docker image runs both backend and frontend
- **Test suite**: endpoint, model, and database-schema tests with Pytest

---

## Limitations

- The model was fine-tuned on product and movie reviews (SST-2). It is not suitable for personal, demographic or identity-related statements and may be biased or wrong on them.
- Binary only. There is no neutral class, so neutral or mixed text still gets a confident-looking label.
- `/logs` is unauthenticated by design and returns a truncated preview of recent submissions. Nothing entered here is private.
- The SQLite file lives inside the container, so history resets when the Space restarts.
- Single-process CPU inference: no batching, no GPU, no queue.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/analyze` | Run sentiment analysis on text (1–5000 characters) |
| GET | `/logs` | Retrieve recent predictions (`limit` 1–200, text truncated) |
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

The same suite runs on every push and pull request via GitHub Actions, alongside a `ruff`
lint pass, followed by a Docker image build that is started and polled until it answers.
