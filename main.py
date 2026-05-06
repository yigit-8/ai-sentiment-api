from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
import sqlite3
import os

app = FastAPI()

sentiment_model = pipeline("sentiment-analysis")

class TextRequest(BaseModel):
    text: str

# Absolute path to the database file, relative to this script's location
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_logs.db")

def init_db():
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

def log_to_db(text: str, label: str, score: float):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO predictions (text, label, score) VALUES (?, ?, ?)",
            (text, label, score)
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

@app.get("/")
def read_root():
    return {"message": "AI API is running! Go to /docs to test it."}

@app.post("/analyze")
def analyze_sentiment(request: TextRequest):
    result = sentiment_model(request.text)[0]
    label = result["label"]
    score = result["score"]
    log_to_db(request.text, label, score)
    return {"label": label, "score": score}

@app.get("/logs")
def get_logs(limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT text, label, score, timestamp FROM predictions ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"text": r[0], "label": r[1], "score": r[2], "timestamp": r[3]} for r in rows]

@app.get("/stats")
def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT label, COUNT(*) FROM predictions GROUP BY label")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}