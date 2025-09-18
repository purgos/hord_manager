from fastapi.testclient import TestClient
from backend.app.main import app
import uuid

client = TestClient(app)


def make_currency(name_prefix="PatchCurr", base_unit=0.01, denominations=None):
    if denominations is None:
        denominations = [
            {"name": "Small", "value_in_base_units": 1},
            {"name": "Large", "value_in_base_units": 10},
        ]
    name = f"{name_prefix}_{uuid.uuid4().hex[:8]}"
    resp = client.post(
        "/currencies/",
        json={
            "name": name,
            "base_unit_value_oz_gold": base_unit,
            "denominations": denominations,
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_patch_add_denomination():
    curr = make_currency()
    cid = curr["id"]
    patch_payload = {
        "denominations_add_or_update": [
            {"name": "NewDenom", "value_in_base_units": 25}
        ]
    }
    resp = client.patch(f"/currencies/{cid}", json=patch_payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    names = {d["name"] for d in data["denominations"]}
    assert "NewDenom" in names


def test_patch_update_denomination():
    curr = make_currency()
    cid = curr["id"]
    # Pick one denom to update
    target = curr["denominations"][0]
    patch_payload = {
        "denominations_add_or_update": [
            {"id": target["id"], "name": "Renamed", "value_in_base_units": 2}
        ]
    }
    resp = client.patch(f"/currencies/{cid}", json=patch_payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    updated = next(d for d in data["denominations"] if d["id"] == target["id"])
    assert updated["name"] == "Renamed"
    assert updated["value_in_base_units"] == 2


def test_patch_remove_denomination():
    curr = make_currency()
    cid = curr["id"]
    remove_id = curr["denominations"][0]["id"]
    patch_payload = {"denomination_ids_remove": [remove_id]}
    resp = client.patch(f"/currencies/{cid}", json=patch_payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    ids = {d["id"] for d in data["denominations"]}
    assert remove_id not in ids


def test_patch_combined_operations():
    curr = make_currency()
    cid = curr["id"]
    # We will: update base unit, update one denom, remove another, add new
    to_update = curr["denominations"][0]
    to_remove = curr["denominations"][1]
    patch_payload = {
        "base_unit_value_oz_gold": 0.02,
        "denomination_ids_remove": [to_remove["id"]],
        "denominations_add_or_update": [
            {"id": to_update["id"], "value_in_base_units": 3},
            {"name": "Added", "value_in_base_units": 50},
        ],
    }
    resp = client.patch(f"/currencies/{cid}", json=patch_payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["base_unit_value_oz_gold"] == 0.02
    ids = {d["id"] for d in data["denominations"]}
    assert to_remove["id"] not in ids
    updated = next(d for d in data["denominations"] if d["id"] == to_update["id"])  # still present
    assert updated["value_in_base_units"] == 3
    names = {d["name"] for d in data["denominations"]}
    assert "Added" in names


def test_patch_update_nonexistent_denomination_error():
    curr = make_currency()
    cid = curr["id"]
    nonexistent_id = 999999  # unlikely to exist
    patch_payload = {
        "denominations_add_or_update": [
            {"id": nonexistent_id, "name": "Ghost"}
        ]
    }
    resp = client.patch(f"/currencies/{cid}", json=patch_payload)
    assert resp.status_code == 404
    assert "not found" in resp.text.lower()
