from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.player import Player

client = TestClient(app)


def ensure_player(name="Tester"):
    db = SessionLocal()
    try:
        p = db.query(Player).filter(Player.name == name).first()
        if not p:
            p = Player(name=name)
            db.add(p)
            db.commit()
            db.refresh(p)
        return p
    finally:
        db.close()


def test_create_and_list_gemstones():
    payload = {"name": "Ruby", "value_per_carat_oz_gold": 0.5}
    resp = client.post("/gemstones/", json=payload)
    if resp.status_code == 400:  # Already exists from previous test run
        assert "already exists" in resp.text
    else:
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["name"] == payload["name"]
        assert data["value_per_carat_oz_gold"] == payload["value_per_carat_oz_gold"]

    resp2 = client.get("/gemstones/")
    assert resp2.status_code == 200
    names = [g["name"] for g in resp2.json()]
    assert payload["name"] in names


def test_add_player_gemstone():
    player = ensure_player()
    # Ensure gemstone exists
    client.post("/gemstones/", json={"name": "Emerald", "value_per_carat_oz_gold": 0.75})
    gems = client.get("/gemstones/").json()
    emerald = next(g for g in gems if g["name"] == "Emerald")

    resp = client.post(
        f"/gemstones/players/{player.id}",
        json={"gemstone_id": emerald["id"], "carats": 10},
    )
    assert resp.status_code == 200, resp.text
    holding = resp.json()
    assert holding["carats"] == 10
    assert holding["appraised_value_oz_gold"] == 10 * emerald["value_per_carat_oz_gold"]

    list_resp = client.get(f"/gemstones/players/{player.id}")
    assert list_resp.status_code == 200
    holdings = list_resp.json()
    assert any(h["gemstone_id"] == emerald["id"] for h in holdings)


def test_duplicate_without_upsert_then_with_upsert():
    # Create once
    first = client.post("/gemstones/", json={"name": "Sapphire", "value_per_carat_oz_gold": 1.0})
    if first.status_code not in (200, 400):
        assert first.status_code == 200, first.text
    # Duplicate without upsert should 400
    dup = client.post("/gemstones/", json={"name": "Sapphire", "value_per_carat_oz_gold": 1.2})
    assert dup.status_code == 400
    # Upsert should succeed and update value
    up = client.post("/gemstones/?upsert=true", json={"name": "Sapphire", "value_per_carat_oz_gold": 1.5})
    assert up.status_code == 200, up.text
    data = up.json()
    assert data["value_per_carat_oz_gold"] == 1.5
