from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_currency_duplicate_then_upsert():
    payload = {
        "name": "Dollar",
        "base_unit_value_oz_gold": 0.02,
        "denominations": [
            {"name": "Cent", "value_in_base_units": 0.01},
            {"name": "Dollar", "value_in_base_units": 1},
        ],
    }
    r1 = client.post("/currencies/", json=payload)
    if r1.status_code == 400:
        assert "already exists" in r1.text
    else:
        assert r1.status_code == 200, r1.text

    # Duplicate without upsert
    dup = client.post("/currencies/", json=payload)
    assert dup.status_code == 400

    # Upsert with changed value and new denominations list
    up_payload = {
        "name": "Dollar",
        "base_unit_value_oz_gold": 0.025,
        "denominations": [
            {"name": "Nickel", "value_in_base_units": 0.05},
            {"name": "Dollar", "value_in_base_units": 1},
        ],
    }
    up = client.post("/currencies/?upsert=true", json=up_payload)
    assert up.status_code == 200, up.text
    data = up.json()
    assert data["base_unit_value_oz_gold"] == 0.025
    denom_names = {d["name"] for d in data["denominations"]}
    assert denom_names == {"Nickel", "Dollar"}
