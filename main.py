import logging
import os
import sqlite3
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from transformers import pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Pinned explicitly: without a model name the pipeline falls back to whatever
# Hugging Face currently ships as the default, which can change under us.
MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"

# Longest input accepted by /analyze. DistilBERT truncates at 512 tokens anyway;
# this bound simply stops a pathological payload from reaching the model at all.
MAX_TEXT_LENGTH = 5000

# /logs is public and unauthenticated, so stored text is echoed back only as a
# short preview rather than in full.
LOG_TEXT_PREVIEW_CHARS = 200

sentiment_model = pipeline("sentiment-analysis", model=MODEL_NAME)


class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT_LENGTH)


# Absolute path to the database file, relative to this script's location
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_logs.db")


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            label TEXT,
            score REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


init_db()


def log_to_db(text: str, label: str, score: float) -> None:
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO predictions (text, label, score) VALUES (?, ?, ?)",
            (text, label, score)
        )
        conn.commit()
    except sqlite3.Error:
        logger.exception("Failed to write prediction to %s", DB_PATH)
    finally:
        if conn is not None:
            conn.close()


def _truncate(text: str, limit: int = LOG_TEXT_PREVIEW_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Sentiment API is running! Go to /docs to test it."}


@app.post("/analyze")
def analyze_sentiment(request: TextRequest) -> dict[str, Any]:
    try:
        result = sentiment_model(request.text)[0]
    except Exception:
        logger.exception("Sentiment inference failed for a %d-character input", len(request.text))
        raise HTTPException(
            status_code=400,
            detail="Could not analyze the submitted text. Please try a shorter or simpler input.",
        )
    label = result["label"]
    score = result["score"]
    log_to_db(request.text, label, score)
    return {"label": label, "score": score}


@app.get("/logs")
def get_logs(limit: int = Query(default=20, ge=1, le=200)) -> list[dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Tie-break on id: CURRENT_TIMESTAMP only has second granularity, so several
    # rows routinely share a timestamp and "most recent" would otherwise be
    # non-deterministic.
    cursor.execute(
        "SELECT text, label, score, timestamp FROM predictions ORDER BY timestamp DESC, id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"text": _truncate(r[0]), "label": r[1], "score": r[2], "timestamp": r[3]}
        for r in rows
    ]


@app.get("/stats")
def get_stats() -> dict[str, int]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT label, COUNT(*) FROM predictions GROUP BY label")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}
