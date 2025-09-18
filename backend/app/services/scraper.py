from typing import Dict, List
import requests
from bs4 import BeautifulSoup

TARGET_URL = "https://www.dailymetalprice.com/metalpricescurr.php"
SUPPORTED_METALS = {
    "Aluminum": "lb",
    "Cobalt": "lb",
    "Copper": "lb",
    "Gold": "oz",
    "Lead": "lb",
    "Molybdenum": "lb",
    "Neodymium": "oz",
    "Nickel": "lb",
    "Palladium": "oz",
    "Platinum": "oz",
    "Silver": "oz",
    "Tin": "lb",
    "Uranium": "lb",
    "Zinc": "lb",
}

def scrape_metal_prices() -> List[dict]:
    """Scrape current metal prices from target site.

    Returns list of dicts: { metal_name, unit, price_per_unit_usd }
    (Note: Real parsing logic TBD — placeholder implementation.)
    """
    try:
        resp = requests.get(TARGET_URL, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        return []

    # Use built-in html.parser to avoid external lxml dependency; can switch later if needed.
    soup = BeautifulSoup(resp.text, "html.parser")
    # Placeholder: real implementation will parse actual table.
    results = []
    for metal, unit in SUPPORTED_METALS.items():
        # Placeholder price
        results.append({
            "metal_name": metal,
            "unit": unit,
            "price_per_unit_usd": 0.0,
        })
    return results
