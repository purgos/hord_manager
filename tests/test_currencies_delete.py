from fastapi.testclient import TestClient


def _create_currency(client: TestClient, name: str = "DeleteCurr", base_unit: float = 0.05):
    payload = {
        "name": name,
        "base_unit_value_oz_gold": base_unit,
        "denominations": [
            {"name": "Unit", "value_in_base_units": 1.0},
        ],
    }
    response = client.post("/currencies/", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_delete_currency_success(client: TestClient):
    currency = _create_currency(client, name="TempDelete")

    delete_response = client.delete(f"/currencies/{currency['id']}")
    assert delete_response.status_code == 204, delete_response.text
    assert delete_response.text == ""

    list_response = client.get("/currencies/")
    assert list_response.status_code == 200
    names = {item["name"] for item in list_response.json()}
    assert "TempDelete" not in names


def test_delete_usd_forbidden(client: TestClient):
    response = client.get("/currencies/")
    assert response.status_code == 200

    usd = next(item for item in response.json() if item["name"] == "USD")

    delete_response = client.delete(f"/currencies/{usd['id']}")
    assert delete_response.status_code == 400
    assert "USD" in delete_response.text
