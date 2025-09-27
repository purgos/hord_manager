from fastapi.testclient import TestClient


def test_create_and_list_art(client: TestClient):
    resp = client.post("/art/", json={"name": "Ancient Vase", "description": "Clay", "player_id": None})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["name"] == "Ancient Vase"

    list_resp = client.get("/art/")
    assert list_resp.status_code == 200
    names = [i["name"] for i in list_resp.json()]
    assert "Ancient Vase" in names

def test_patch_art(client: TestClient):
    resp = client.post("/art/", json={"name": "Bronze Statue", "description": "Statue", "player_id": None})
    assert resp.status_code == 200, resp.text
    art = resp.json()
    patch = client.patch(f"/art/{art['id']}", json={"description": "Bronze warrior statue", "appraised_value_oz_gold": 5.5})
    assert patch.status_code == 200, patch.text
    updated = patch.json()
    assert updated["description"].startswith("Bronze")
    assert updated["appraised_value_oz_gold"] == 5.5
