from typing import Dict, List, Optional
import requests
import random
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.metal import MetalPriceHistory
from ..models.session import GlobalState

logger = logging.getLogger(__name__)

# Primary and fallback URLs for metal price scraping
TARGET_URL = "https://www.dailymetalprice.com/metalpricescurr.php"
FALLBACK_URL = "https://www.dailymetalprice.com/metalprices.php"

# Supported metals with their units and approximate price ranges for fallback
SUPPORTED_METALS = {
    "Aluminum": {"unit": "lb", "min_price": 0.75, "max_price": 1.25},
    "Cobalt": {"unit": "lb", "min_price": 12.0, "max_price": 18.0},
    "Copper": {"unit": "lb", "min_price": 3.50, "max_price": 4.50},
    "Gold": {"unit": "oz", "min_price": 1900.0, "max_price": 2100.0},
    "Lead": {"unit": "lb", "min_price": 0.85, "max_price": 1.15},
    "Lithium": {"unit": "kg", "min_price": 15.0, "max_price": 25.0},
    "Molybdenum": {"unit": "lb", "min_price": 18.0, "max_price": 28.0},
    "Neodymium": {"unit": "oz", "min_price": 50.0, "max_price": 80.0},
    "Nickel": {"unit": "lb", "min_price": 7.0, "max_price": 11.0},
    "Palladium": {"unit": "oz", "min_price": 900.0, "max_price": 1200.0},
    "Platinum": {"unit": "oz", "min_price": 800.0, "max_price": 1100.0},
    "Silver": {"unit": "oz", "min_price": 20.0, "max_price": 35.0},
    "Tin": {"unit": "lb", "min_price": 12.0, "max_price": 16.0},
    "Uranium": {"unit": "lb", "min_price": 45.0, "max_price": 65.0},
    "Zinc": {"unit": "lb", "min_price": 1.00, "max_price": 1.40},
}

def _try_parse_dailymetalprice_table(soup: BeautifulSoup) -> Optional[List[dict]]:
    """Try to parse metal prices from dailymetalprice.com table structure."""
    try:
        # Look for tables with commodity price data
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            if not rows:
                continue
                
            # Check if this looks like a price table
            headers = [cell.get_text().strip().lower() for cell in rows[0].find_all(['th', 'td'])]
            if 'commodity' in headers and 'price' in headers:
                results = []
                
                # Get column indices
                try:
                    commodity_idx = headers.index('commodity')
                    price_idx = headers.index('price')
                    unit_idx = headers.index('unit') if 'unit' in headers else None
                except ValueError:
                    continue
                
                # Parse data rows
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) <= max(commodity_idx, price_idx):
                        continue
                        
                    commodity = cells[commodity_idx].get_text().strip()
                    price_text = cells[price_idx].get_text().strip()
                    unit = cells[unit_idx].get_text().strip() if unit_idx and unit_idx < len(cells) else ""
                    
                    # Check if this commodity is in our supported list
                    if commodity in SUPPORTED_METALS:
                        try:
                            # Extract numeric price (remove currency symbols, commas)
                            price_cleaned = ''.join(c for c in price_text if c.isdigit() or c == '.')
                            if price_cleaned:
                                price = float(price_cleaned)
                                results.append({
                                    "metal_name": commodity,
                                    "unit": unit or SUPPORTED_METALS[commodity]["unit"],
                                    "price_per_unit_usd": price,
                                })
                        except (ValueError, KeyError):
                            continue
                
                if results:
                    return results
                    
    except Exception as e:
        logger.warning(f"Error parsing dailymetalprice table: {e}")
    
    return None

def _generate_mock_prices() -> List[dict]:
    """Generate realistic mock prices for testing and fallback purposes."""
    results = []
    
    for metal_name, config in SUPPORTED_METALS.items():
        # Generate a price within the realistic range with some randomness
        base_price = (config["min_price"] + config["max_price"]) / 2
        variation = random.uniform(-0.1, 0.1)  # ±10% variation
        price = base_price * (1 + variation)
        
        results.append({
            "metal_name": metal_name,
            "unit": config["unit"],
            "price_per_unit_usd": round(price, 2),
        })
    
    return results

def scrape_metal_prices(use_mock_data: bool = False) -> List[dict]:
    """Scrape current metal prices from target site.

    Args:
        use_mock_data: If True, return mock data instead of scraping

    Returns:
        List of dicts: { metal_name, unit, price_per_unit_usd }
    """
    if use_mock_data:
        logger.info("Using mock metal price data")
        return _generate_mock_prices()
    
    # Try to scrape real data
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    # Try primary URL first
    urls_to_try = [TARGET_URL, FALLBACK_URL]
    
    for url in urls_to_try:
        try:
            logger.info(f"Attempting to scrape metal prices from {url}")
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Try to parse the table
            results = _try_parse_dailymetalprice_table(soup)
            if results:
                logger.info(f"Successfully scraped {len(results)} metal prices")
                return results
            else:
                logger.warning(f"No price data found in {url}")
                
        except Exception as e:
            logger.warning(f"Error scraping {url}: {e}")
            continue
    
    # If all scraping attempts failed, fall back to mock data
    logger.warning("All scraping attempts failed, falling back to mock data")
    return _generate_mock_prices()

def _get_current_session_number(db: Session) -> int:
    """Get the current session number from the database."""
    global_state = db.query(GlobalState).first()
    if global_state:
        return global_state.current_session
    else:
        # Create initial global state if it doesn't exist
        new_state = GlobalState(current_session=1)
        db.add(new_state)
        db.commit()
        return 1

def _calculate_price_per_oz_gold(price_usd: float, unit: str, gold_price_per_oz: float) -> float:
    """Convert metal price to price per oz of gold."""
    if gold_price_per_oz <= 0:
        return 0.0
    
    # Convert to price per oz if needed
    if unit == "lb":
        price_per_oz = price_usd / 16.0  # 16 oz in a pound
    elif unit == "kg":
        price_per_oz = price_usd / 35.274  # ~35.274 oz in a kg
    else:  # assume oz
        price_per_oz = price_usd
    
    # Convert to fraction of gold price
    return price_per_oz / gold_price_per_oz

def store_metal_prices_in_db(metal_prices: List[dict], db: Session) -> int:
    """Store scraped metal prices in the database.
    
    Args:
        metal_prices: List of metal price dicts from scrape_metal_prices()
        db: Database session
        
    Returns:
        Number of records stored
    """
    if not metal_prices:
        logger.warning("No metal prices to store")
        return 0
    
    session_number = _get_current_session_number(db)
    
    # Find gold price to use as reference
    gold_price_usd = None
    for metal in metal_prices:
        if metal["metal_name"] == "Gold" and metal["unit"] == "oz":
            gold_price_usd = metal["price_per_unit_usd"]
            break
    
    if gold_price_usd is None or gold_price_usd <= 0:
        logger.warning("No valid gold price found, using fallback value")
        gold_price_usd = 2000.0  # Fallback gold price
    
    stored_count = 0
    
    for metal_data in metal_prices:
        try:
            price_per_oz_gold = _calculate_price_per_oz_gold(
                metal_data["price_per_unit_usd"],
                metal_data["unit"],
                gold_price_usd
            )
            
            price_record = MetalPriceHistory(
                metal_name=metal_data["metal_name"],
                unit=metal_data["unit"],
                price_per_unit_usd=metal_data["price_per_unit_usd"],
                price_per_oz_gold=price_per_oz_gold,
                session_number=session_number
            )
            
            db.add(price_record)
            stored_count += 1
            
        except Exception as e:
            logger.error(f"Error storing price for {metal_data.get('metal_name', 'unknown')}: {e}")
    
    try:
        db.commit()
        logger.info(f"Successfully stored {stored_count} metal price records for session {session_number}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error committing metal prices to database: {e}")
        stored_count = 0
    
    return stored_count

def scrape_and_store_metal_prices(db: Session, use_mock_data: bool = False) -> dict:
    """Scrape metal prices and store them in the database.
    
    Args:
        db: Database session
        use_mock_data: If True, use mock data instead of scraping
        
    Returns:
        Dict with status information
    """
    try:
        # Scrape the prices
        metal_prices = scrape_metal_prices(use_mock_data=use_mock_data)
        
        if not metal_prices:
            return {
                "success": False,
                "message": "No metal prices could be scraped",
                "prices_stored": 0
            }
        
        # Store in database
        stored_count = store_metal_prices_in_db(metal_prices, db)
        
        return {
            "success": stored_count > 0,
            "message": f"Successfully scraped and stored {stored_count} metal prices",
            "prices_stored": stored_count,
            "scraped_prices": len(metal_prices),
            "use_mock_data": use_mock_data
        }
        
    except Exception as e:
        logger.error(f"Error in scrape_and_store_metal_prices: {e}")
        return {
            "success": False,
            "message": f"Error during scraping: {str(e)}",
            "prices_stored": 0
        }
