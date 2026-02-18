from fastapi.testclient import TestClient
from backend.src.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_translate_success():
    r = client.post("/api/translate", json={"text": "Hello, world!"})
    assert r.status_code == 200
    data = r.json()
    assert "translated_text" in data


def test_translate_empty():
    r = client.post("/api/translate", json={"text": ""})
    assert r.status_code == 400
