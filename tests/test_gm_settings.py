from fastapi.testclient import TestClient
from backend.app.main import app


def get_client():
    return TestClient(app)


def test_get_or_create_settings():
    client = get_client()
    # Force a known state by patching first
    resp = client.patch("/gm/settings", json={"hide_dollar_from_players": False})
    assert resp.status_code == 200
    data = resp.json()
    assert data["hide_dollar_from_players"] is False

    # Fetch again and ensure id stable
    resp2 = client.get("/gm/settings")
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["id"] == data["id"]
    assert data2["hide_dollar_from_players"] is False


def test_patch_toggle_hide_dollar():
    client = get_client()
    resp = client.patch("/gm/settings", json={"hide_dollar_from_players": True})
    assert resp.status_code == 200
    data = resp.json()
    assert data["hide_dollar_from_players"] is True
    # Toggle back
    resp2 = client.patch("/gm/settings", json={"hide_dollar_from_players": False})
    assert resp2.status_code == 200
    assert resp2.json()["hide_dollar_from_players"] is False
