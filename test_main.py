import os
import sqlite3

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_logs.db")


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Sentiment API is running! Go to /docs to test it."


def test_analyze_sentiment():
    payload = {"text": "Artificial Intelligence is fascinating!"}
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    assert "label" in response.json()
    assert "score" in response.json()
    assert response.json()["label"] in ["POSITIVE", "NEGATIVE"]


def test_analyze_rejects_empty_text():
    response = client.post("/analyze", json={"text": ""})
    assert response.status_code == 422


def test_analyze_rejects_oversized_text():
    response = client.post("/analyze", json={"text": "a" * 5001})
    assert response.status_code == 422


def test_logs_returns_recent_predictions():
    client.post("/analyze", json={"text": "This library is wonderful to work with."})

    response = client.get("/logs")
    assert response.status_code == 200
    logs = response.json()
    assert isinstance(logs, list)
    assert len(logs) >= 1
    entry = logs[0]
    assert set(entry) == {"text", "label", "score", "timestamp"}
    assert entry["label"] in ["POSITIVE", "NEGATIVE"]
    assert 0.0 < entry["score"] <= 1.0


def test_logs_respects_limit():
    response = client.get("/logs", params={"limit": 1})
    assert response.status_code == 200
    assert len(response.json()) <= 1


def test_logs_rejects_out_of_range_limit():
    assert client.get("/logs", params={"limit": 0}).status_code == 422
    assert client.get("/logs", params={"limit": 201}).status_code == 422


def test_logs_truncates_stored_text():
    long_text = "This product is great. " * 40  # comfortably over the preview length
    assert len(long_text) > 200
    client.post("/analyze", json={"text": long_text})

    logs = client.get("/logs", params={"limit": 1}).json()
    assert len(logs[0]["text"]) <= 203  # 200 characters plus the "..." marker
    assert logs[0]["text"].endswith("...")


def test_stats_returns_label_counts():
    client.post("/analyze", json={"text": "An absolutely delightful experience."})

    response = client.get("/stats")
    assert response.status_code == 200
    stats = response.json()
    assert isinstance(stats, dict)
    assert stats, "stats should not be empty after a prediction was logged"
    assert set(stats).issubset({"POSITIVE", "NEGATIVE"})
    assert all(isinstance(count, int) and count > 0 for count in stats.values())


def test_database_schema():
    assert os.path.exists(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    try:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert "predictions" in tables

        columns = {row[1]: row[2] for row in conn.execute("PRAGMA table_info(predictions)")}
    finally:
        conn.close()

    assert columns == {
        "id": "INTEGER",
        "text": "TEXT",
        "label": "TEXT",
        "score": "REAL",
        "timestamp": "DATETIME",
    }
