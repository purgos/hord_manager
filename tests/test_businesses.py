from fastapi.testclient import TestClient
from backend.app.models.player import Player


def ensure_player(db_session, name="BizTester"):
    player = db_session.query(Player).filter(Player.name == name).first()
    if not player:
        player = Player(name=name)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
    return player


def test_create_business_and_get(client: TestClient):
    resp = client.post(
        "/businesses/",
        json={
            "name": "Arcane Forge",
            "description": "Magical item crafting",
            "principle_activity": "Enchanting",
            "net_worth_oz_gold": 100.0,
            "income_per_session_oz_gold": 5.0,
        },
    )
    assert resp.status_code == 200, resp.text
    biz = resp.json()
    get_resp = client.get(f"/businesses/{biz['id']}")
    assert get_resp.status_code == 200
    detailed = get_resp.json()
    assert detailed["name"] == "Arcane Forge"
    assert detailed["investors"] == []


def test_upsert_investors_and_equity_check(client: TestClient, db_session):
    player1 = ensure_player(db_session, "Owner1")
    player2 = ensure_player(db_session, "Owner2")
    # Create business
    resp = client.post(
        "/businesses/",
        json={"name": "Skyport", "description": "Airship docks", "principle_activity": "Logistics"},
    )
    assert resp.status_code == 200, resp.text
    biz = resp.json()
    # Add investors
    inv_resp = client.post(
        f"/businesses/{biz['id']}/investors",
        json=[
            {"player_id": player1.id, "equity_percent": 60, "invested_oz_gold": 300},
            {"player_id": player2.id, "equity_percent": 40, "invested_oz_gold": 200},
        ],
    )
    assert inv_resp.status_code == 200, inv_resp.text
    inv_list = inv_resp.json()
    assert len(inv_list) == 2
    total_equity = sum(i["equity_percent"] for i in inv_list)
    assert round(total_equity, 2) == 100.0
    # Try exceeding
    bad = client.post(
        f"/businesses/{biz['id']}/investors",
        json=[{"player_id": player2.id, "equity_percent": 70}],
    )
    assert bad.status_code == 400


def test_business_petition_creates_inbox_message(client: TestClient, db_session):
    player = ensure_player(db_session, "Petitioner")
    petition = client.post(
        "/businesses/petitions",
        json={
            "player_id": player.id,
            "name": "Herbal Shop",
            "description": "Potion ingredients",
            "principle_activity": "Herbalism",
            "initial_investment_oz_gold": 25.0,
        },
    )
    assert petition.status_code == 202, petition.text
    data = petition.json()
    assert data["status"] == "accepted"
    # Check inbox listing
    inbox = client.get("/gm/inbox/")
    assert inbox.status_code == 200
    msgs = inbox.json()
    assert any(m["type"] == "business_petition" for m in msgs)


def test_remove_investor_no_rebalance(client: TestClient, db_session):
    # setup business with two investors
    player_a = ensure_player(db_session, "RemOwnerA")
    player_b = ensure_player(db_session, "RemOwnerB")
    resp = client.post(
        "/businesses/",
        json={"name": "RemovalBiz", "description": "Test", "principle_activity": "Testing"},
    )
    assert resp.status_code == 200
    biz = resp.json()
    inv_resp = client.post(
        f"/businesses/{biz['id']}/investors",
        json=[
            {"player_id": player_a.id, "equity_percent": 70, "invested_oz_gold": 100},
            {"player_id": player_b.id, "equity_percent": 30, "invested_oz_gold": 50},
        ],
    )
    assert inv_resp.status_code == 200
    # remove second investor without rebalance
    del_resp = client.delete(f"/businesses/{biz['id']}/investors/{player_b.id}")
    assert del_resp.status_code == 200, del_resp.text
    remaining = del_resp.json()
    assert len(remaining) == 1
    assert remaining[0]["player_id"] == player_a.id
    # equity sum can now be 70 (not rebalanced)
    assert round(sum(i["equity_percent"] for i in remaining), 2) == 70.0


def test_remove_investor_with_rebalance(client: TestClient, db_session):
    player_a = ensure_player(db_session, "RebalOwnerA")
    player_b = ensure_player(db_session, "RebalOwnerB")
    player_c = ensure_player(db_session, "RebalOwnerC")
    resp = client.post(
        "/businesses/",
        json={"name": "RebalanceBiz", "description": "Test", "principle_activity": "Testing"},
    )
    assert resp.status_code == 200
    biz = resp.json()
    inv_resp = client.post(
        f"/businesses/{biz['id']}/investors",
        json=[
            {"player_id": player_a.id, "equity_percent": 50, "invested_oz_gold": 100},
            {"player_id": player_b.id, "equity_percent": 30, "invested_oz_gold": 60},
            {"player_id": player_c.id, "equity_percent": 20, "invested_oz_gold": 40},
        ],
    )
    assert inv_resp.status_code == 200
    # remove player_c with rebalance: its 20% should be distributed proportionally to 50:30 (total 80 -> ratios 62.5% and 37.5%)
    del_resp = client.delete(f"/businesses/{biz['id']}/investors/{player_c.id}?rebalance=true")
    assert del_resp.status_code == 200, del_resp.text
    remaining = del_resp.json()
    assert len(remaining) == 2
    eq_map = {i["player_id"]: i["equity_percent"] for i in remaining}
    # Expected new equities: A gets 50 + 20*(50/80)=62.5, B gets 30 + 20*(30/80)=37.5
    assert round(eq_map[player_a.id], 2) == 62.5
    assert round(eq_map[player_b.id], 2) == 37.5
    assert round(sum(eq_map.values()), 2) == 100.0
