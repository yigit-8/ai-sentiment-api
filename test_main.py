from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

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

def test_database_initialization():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_logs.db")
    assert os.path.exists(db_path)