from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import random
from datetime import datetime
from ..core.database import get_db
from ..models.material import MaterialPriceHistory
from ..services.scraper import fetch_latest_material_prices, store_material_prices_in_db

router = APIRouter(prefix="/materials", tags=["materials"])

# Define 20 common materials with their base prices and units
MATERIALS_DATA = [
    # Existing metals-like materials
    {"name": "Wood", "unit": "board ft", "base_price": 2.50},
    {"name": "Cotton", "unit": "lb", "base_price": 0.75},
    {"name": "Carbon", "unit": "lb", "base_price": 15.00},
    {"name": "Sulfur", "unit": "lb", "base_price": 0.25},
    {"name": "Silicon", "unit": "lb", "base_price": 1.20},
    {"name": "Phosphorus", "unit": "lb", "base_price": 2.80},
    
    # Additional common materials to reach 20 total
    {"name": "Iron Ore", "unit": "ton", "base_price": 120.00},
    {"name": "Salt", "unit": "lb", "base_price": 0.05},
    {"name": "Sand", "unit": "ton", "base_price": 15.00},
    {"name": "Clay", "unit": "ton", "base_price": 25.00},
    {"name": "Limestone", "unit": "ton", "base_price": 12.00},
    {"name": "Rubber", "unit": "lb", "base_price": 1.45},
    {"name": "Wool", "unit": "lb", "base_price": 3.20},
    {"name": "Hemp", "unit": "lb", "base_price": 2.10},
    {"name": "Flax", "unit": "lb", "base_price": 1.80},
    {"name": "Bamboo", "unit": "board ft", "base_price": 1.90},
    {"name": "Cork", "unit": "lb", "base_price": 4.50},
    
    # New materials replacing removed ones
    {"name": "Leather", "unit": "sq ft", "base_price": 6.25},
    {"name": "Glass", "unit": "lb", "base_price": 0.95},
    {"name": "Wax", "unit": "lb", "base_price": 3.80}
]

def generate_material_prices(session_number: int = 1, use_mock_data: bool = True):
    """Generate material prices with some variability based on session number."""
    prices = []
    
    # Use session number as seed for consistent but varying prices
    random.seed(session_number * 42)
    
    for material in MATERIALS_DATA:
        # Add some variability (±20%) to base prices
        variance = random.uniform(0.8, 1.2)
        session_modifier = 1 + (session_number - 1) * 0.02  # 2% increase per session
        
        current_price = material["base_price"] * variance * session_modifier
        
        # Calculate price per oz gold (assuming gold is ~$2000/oz)
        gold_price_per_oz = 2000.0
        price_per_oz_gold = current_price / gold_price_per_oz
        
        prices.append({
            "material_name": material["name"],
            "unit": material["unit"],
            "price_per_unit_usd": round(current_price, 4),
            "price_per_oz_gold": round(price_per_oz_gold, 6),
        })
    
    return prices

@router.post("/scrape")
def trigger_material_price_update(
    session_number: int = Query(1, description="Session number for price calculation"),
    use_mock_data: bool = Query(True, description="Use generated data"),
    db: Session = Depends(get_db)
):
    """Generate and store material prices for the current session."""
    try:
        prices = generate_material_prices(session_number, use_mock_data)
        stored_count = store_material_prices_in_db(prices, db, session_number)

        latest_prices = fetch_latest_material_prices(db, session_number)

        return {
            "success": True,
            "prices_stored": stored_count,
            "session_number": session_number,
            "prices": [
                {
                    "material_name": record.material_name,
                    "unit": record.unit,
                    "price_per_unit_usd": record.price_per_unit_usd,
                    "price_per_oz_gold": record.price_per_oz_gold,
                    "session_number": record.session_number,
                    "created_at": record.created_at,
                }
                for record in latest_prices
            ],
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update material prices: {str(e)}")

@router.get("/prices/current")
def get_current_material_prices(
    session_number: int | None = Query(None, description="Session number to filter by"),
    use_mock_data: bool = Query(True, description="Generate and persist mock data when no records exist"),
    db: Session = Depends(get_db)
):
    """Return the most recently stored material prices, generating data only when needed."""
    try:
        records = fetch_latest_material_prices(db, session_number)

        generated = False
        target_session = session_number

        if not records and use_mock_data:
            session_to_generate = session_number or 1
            prices = generate_material_prices(session_to_generate, use_mock_data)
            store_material_prices_in_db(prices, db, session_to_generate)
            target_session = session_to_generate
            records = fetch_latest_material_prices(db, target_session)
            generated = True

        if not records:
            raise HTTPException(status_code=404, detail="No material prices available. Run the scrape endpoint to populate data.")

        response_session = target_session or (records[0].session_number if records else None)

        return {
            "prices": [
                {
                    "material_name": record.material_name,
                    "unit": record.unit,
                    "price_per_unit_usd": record.price_per_unit_usd,
                    "price_per_oz_gold": record.price_per_oz_gold,
                    "session_number": record.session_number,
                    "created_at": record.created_at,
                }
                for record in records
            ],
            "count": len(records),
            "session_number": response_session,
            "generated": generated,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get material prices: {str(e)}")

@router.get("/prices/history")
def get_material_price_history(
    material_name: Optional[str] = Query(None, description="Filter by material name"),
    session_number: Optional[int] = Query(None, description="Filter by session number"),
    limit: int = Query(100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Get historical material price data from database."""
    try:
        query = db.query(MaterialPriceHistory)
        
        if material_name:
            query = query.filter(MaterialPriceHistory.material_name == material_name)
        
        if session_number:
            query = query.filter(MaterialPriceHistory.session_number == session_number)
        
        # Order by most recent first
        query = query.order_by(MaterialPriceHistory.created_at.desc())
        
        # Apply limit
        records = query.limit(limit).all()
        
        return {
            "records": [
                {
                    "id": record.id,
                    "material_name": record.material_name,
                    "unit": record.unit,
                    "price_per_unit_usd": record.price_per_unit_usd,
                    "price_per_oz_gold": record.price_per_oz_gold,
                    "session_number": record.session_number,
                    "created_at": record.created_at
                }
                for record in records
            ],
            "count": len(records)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get material price history: {str(e)}")

@router.get("/list")
def get_available_materials():
    """Get list of all available materials and their base information."""
    return {
        "materials": [
            {
                "name": material["name"],
                "unit": material["unit"],
                "base_price": material["base_price"],
                "min_multiplier": 0.8,  # Default values - would be stored in database
                "max_multiplier": 1.2
            }
            for material in MATERIALS_DATA
        ],
        "count": len(MATERIALS_DATA)
    }

@router.put("/price-range/{material_name}")
def update_material_price_range(
    material_name: str,
    min_multiplier: float,
    max_multiplier: float
):
    """Update the price range multipliers for a specific material."""
    # Validate material exists
    material_exists = any(material["name"] == material_name for material in MATERIALS_DATA)
    if not material_exists:
        raise HTTPException(status_code=404, detail=f"Material '{material_name}' not found")
    
    # Validate multipliers
    if min_multiplier <= 0 or max_multiplier <= 0:
        raise HTTPException(status_code=400, detail="Multipliers must be positive")
    
    if min_multiplier >= max_multiplier:
        raise HTTPException(status_code=400, detail="Minimum multiplier must be less than maximum multiplier")
    
    # In a real implementation, this would update the database
    # For now, we'll just return success with the updated values
    return {
        "success": True,
        "material_name": material_name,
        "min_multiplier": min_multiplier,
        "max_multiplier": max_multiplier,
        "message": f"Successfully updated price range for {material_name}"
    }

@router.get("/price-ranges")
def get_all_material_price_ranges():
    """Get price range multipliers for all materials."""
    return {
        "materials": [
            {
                "name": material["name"],
                "unit": material["unit"],
                "base_price": material["base_price"],
                "min_multiplier": 0.8,  # Default values - would come from database
                "max_multiplier": 1.2,
                "current_min_price": material["base_price"] * 0.8,
                "current_max_price": material["base_price"] * 1.2
            }
            for material in MATERIALS_DATA
        ]
    }

@router.post("/create")
def create_new_material(
    name: str,
    unit: str,
    base_price: float,
    db: Session = Depends(get_db)
):
    """Create a new material with initial price data"""
    try:
        # Get current session
        from ..models.session import GlobalState
        session_state = db.query(GlobalState).first()
        current_session = session_state.current_session if session_state else 1
        
        # Check if material already exists
        existing = db.query(MaterialPriceHistory).filter(
            MaterialPriceHistory.material_name == name
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail=f"Material '{name}' already exists")
        
        # Create initial price entry
        price_per_oz_gold = base_price / 2000.0  # Assuming $2000/oz gold
        
        new_material = MaterialPriceHistory(
            material_name=name,
            unit=unit,
            price_per_unit_usd=base_price,
            price_per_oz_gold=price_per_oz_gold,
            session_number=current_session
        )
        
        db.add(new_material)
        db.commit()
        db.refresh(new_material)
        
        return {
            "message": f"Material '{name}' created successfully",
            "material": {
                "material_name": new_material.material_name,
                "unit": new_material.unit,
                "price_per_unit_usd": new_material.price_per_unit_usd,
                "price_per_oz_gold": new_material.price_per_oz_gold,
                "session_number": new_material.session_number
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating material: {str(e)}")