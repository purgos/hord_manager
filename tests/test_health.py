from fastapi.testclient import TestClient


def test_health_ping(client: TestClient):
    r = client.get("/health/ping")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
