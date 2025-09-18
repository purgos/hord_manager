from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_ping():
    r = client.get("/health/ping")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
