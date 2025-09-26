from typing import List
import random
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from ..models.metal import MetalPriceHistory
from ..models.session import GlobalState

logger = logging.getLogger(__name__)

# Supported metals with their units and price ranges
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
    "Steel": {"unit": "kg", "min_price": 0.45, "max_price": 0.75},
    "Tin": {"unit": "lb", "min_price": 12.0, "max_price": 16.0},
    "Uranium": {"unit": "lb", "min_price": 45.0, "max_price": 65.0},
    "Zinc": {"unit": "lb", "min_price": 1.00, "max_price": 1.40},
}

# Supported gemstones with their approximate price ranges per carat
SUPPORTED_GEMSTONES = {
    "Diamond": {"unit": "carat", "min_price": 2000.0, "max_price": 15000.0},
    "Ruby": {"unit": "carat", "min_price": 1000.0, "max_price": 8000.0},
    "Sapphire": {"unit": "carat", "min_price": 800.0, "max_price": 6000.0},
    "Emerald": {"unit": "carat", "min_price": 1200.0, "max_price": 10000.0},
    "Tanzanite": {"unit": "carat", "min_price": 600.0, "max_price": 3000.0},
    "Opal": {"unit": "carat", "min_price": 50.0, "max_price": 2000.0},
    "Jade": {"unit": "carat", "min_price": 100.0, "max_price": 3000.0},
    "Topaz": {"unit": "carat", "min_price": 25.0, "max_price": 400.0},
    "Aquamarine": {"unit": "carat", "min_price": 200.0, "max_price": 1500.0},
    "Amethyst": {"unit": "carat", "min_price": 20.0, "max_price": 300.0},
    "Citrine": {"unit": "carat", "min_price": 10.0, "max_price": 200.0},
    "Garnet": {"unit": "carat", "min_price": 15.0, "max_price": 500.0},
    "Peridot": {"unit": "carat", "min_price": 50.0, "max_price": 400.0},
    "Turquoise": {"unit": "carat", "min_price": 5.0, "max_price": 50.0},
    "Moonstone": {"unit": "carat", "min_price": 10.0, "max_price": 300.0},
    "Lapis Lazuli": {"unit": "carat", "min_price": 5.0, "max_price": 50.0},
    "Malachite": {"unit": "carat", "min_price": 3.0, "max_price": 30.0},
    "Onyx": {"unit": "carat", "min_price": 2.0, "max_price": 20.0},
    "Rose Quartz": {"unit": "carat", "min_price": 1.0, "max_price": 15.0},
    "Tiger's Eye": {"unit": "carat", "min_price": 2.0, "max_price": 25.0},
}

def scrape_metal_prices(use_mock_data: bool = False) -> List[dict]:
    """Generate random metal prices within specified ranges."""
    logger.info("Generating random metal price data")
    results = []
    
    for metal_name, config in SUPPORTED_METALS.items():
        price = random.uniform(config["min_price"], config["max_price"])
        results.append({
            "metal_name": metal_name,
            "unit": config["unit"],
            "price_per_unit_usd": round(price, 4),
        })
    
    return results

def scrape_gemstone_prices(use_mock_data: bool = False) -> List[dict]:
    """Generate fixed gemstone prices using average of min/max ranges."""
    logger.info("Generating fixed gemstone price data using averages")
    results = []
    
    for gemstone_name, config in SUPPORTED_GEMSTONES.items():
        # Use the average of min and max prices for consistent pricing
        price = (config["min_price"] + config["max_price"]) / 2.0
        
        results.append({
            "gemstone_name": gemstone_name,
            "unit": config["unit"],
            "price_per_unit_usd": round(price, 2),  # Round to 2 decimal places for currency
        })
    
    return results

def _get_current_session_number(db: Session) -> int:
    """Get the current session number from the database."""
    global_state = db.query(GlobalState).first()
    if global_state:
        return global_state.current_session
    else:
        new_state = GlobalState(current_session=1)
        db.add(new_state)
        db.commit()
        return 1

def _calculate_price_per_oz_gold(price_usd: float, unit: str, gold_price_per_oz: float) -> float:
    """Convert metal price to price per oz of gold."""
    if gold_price_per_oz <= 0:
        return 0.0
    
    if unit == "lb":
        price_per_oz = price_usd / 16.0
    elif unit == "kg":
        price_per_oz = price_usd / 35.274
    else:
        price_per_oz = price_usd
    
    return price_per_oz / gold_price_per_oz

def store_metal_prices_in_db(metal_prices: List[dict], db: Session) -> int:
    """Store metal prices in the database."""
    session_number = _get_current_session_number(db)
    
    gold_price_per_oz = None
    for price_data in metal_prices:
        if price_data["metal_name"] == "Gold" and price_data["unit"] == "oz":
            gold_price_per_oz = price_data["price_per_unit_usd"]
            break
    
    if gold_price_per_oz is None:
        gold_price_per_oz = 2000.0
    
    stored_count = 0
    for price_data in metal_prices:
        try:
            price_per_oz_gold = _calculate_price_per_oz_gold(
                price_data["price_per_unit_usd"],
                price_data["unit"],
                gold_price_per_oz
            )
            
            metal_price = MetalPriceHistory(
                metal_name=price_data["metal_name"],
                unit=price_data["unit"],
                price_per_unit_usd=price_data["price_per_unit_usd"],
                price_per_oz_gold=price_per_oz_gold,
                session_number=session_number,
                created_at=datetime.utcnow(),
            )
            
            db.add(metal_price)
            stored_count += 1
            
        except Exception as e:
            logger.error(f"Error storing price for {price_data['metal_name']}: {e}")
            continue
    
    try:
        db.commit()
        logger.info(f"Stored {stored_count} metal prices for session {session_number}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error committing metal prices to database: {e}")
        raise
    
    return stored_count

def scrape_and_store_metal_prices(db: Session, use_mock_data: bool = False) -> dict:
    """Generate random metal prices and store them in the database."""
    try:
        metal_prices = scrape_metal_prices(use_mock_data=use_mock_data)
        
        if not metal_prices:
            return {
                "success": False,
                "error": "No price data generated",
                "prices_stored": 0
            }
        
        stored_count = store_metal_prices_in_db(metal_prices, db)
        
        return {
            "success": True,
            "prices_stored": stored_count,
            "total_metals": len(metal_prices),
            "session_number": _get_current_session_number(db)
        }
        
    except Exception as e:
        logger.error(f"Error in scrape_and_store_metal_prices: {e}")
        return {
            "success": False,
            "error": str(e),
            "prices_stored": 0
        }
