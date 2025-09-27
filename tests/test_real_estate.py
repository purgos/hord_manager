from fastapi.testclient import TestClient


def test_create_and_list_property(client: TestClient):
    resp = client.post("/real-estate/", json={"name": "Tower Keep", "location": "Hill", "description": "Stone keep", "player_id": None})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["name"] == "Tower Keep"

    list_resp = client.get("/real-estate/")
    assert list_resp.status_code == 200
    names = [p["name"] for p in list_resp.json()]
    assert "Tower Keep" in names
def test_patch_property(client: TestClient):
    resp = client.post("/real-estate/", json={"name": "Farmstead", "location": "Valley", "description": "Crop land", "player_id": None})
    assert resp.status_code == 200, resp.text
    prop = resp.json()
    patch = client.patch(f"/real-estate/{prop['id']}", json={"description": "Large crop land", "income_per_session_oz_gold": 2.25})
    assert patch.status_code == 200, patch.text
    updated = patch.json()
    assert updated["description"].startswith("Large")
    assert updated["income_per_session_oz_gold"] == 2.25
