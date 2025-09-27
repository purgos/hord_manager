from fastapi.testclient import TestClient


def test_only_usd_default_present(client: TestClient):
    response = client.get("/currencies/")
    assert response.status_code == 200, response.text
    data = response.json()

    names = {currency["name"] for currency in data}
    assert names == {"USD"}

    legacy_names = {"US Dollar", "Euro", "British Pound", "Japanese Yen"}
    assert names.isdisjoint(legacy_names), names
    assert "Gold" not in names
