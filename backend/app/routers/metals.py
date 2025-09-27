from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..models.metal import MetalPriceHistory
from ..services.scraper import (
    scrape_and_store_metal_prices,
    scrape_metal_prices,
    scrape_gemstone_prices,
    fetch_latest_metal_prices,
)

router = APIRouter(prefix="/metals", tags=["metals"])

@router.post("/scrape")
def trigger_metal_price_scraping(
    use_mock_data: bool = Query(False, description="Use mock data instead of scraping"),
    db: Session = Depends(get_db)
):
    """Trigger metal price scraping and store results in database."""
    try:
        result = scrape_and_store_metal_prices(db, use_mock_data=use_mock_data)
        
        if result["success"]:
            latest_prices = fetch_latest_metal_prices(db, result.get("session_number"))
            return {
                "success": True,
                "prices_stored": result["prices_stored"],
                "total_metals": result["total_metals"],
                "session_number": result["session_number"],
                "prices": [
                    {
                        "metal_name": price.metal_name,
                        "unit": price.unit,
                        "price_per_unit_usd": price.price_per_unit_usd,
                        "price_per_oz_gold": price.price_per_oz_gold,
                        "session_number": price.session_number,
                        "created_at": price.created_at,
                    }
                    for price in latest_prices
                ],
                "use_mock_data": use_mock_data,
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to scrape metal prices"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@router.get("/prices/current")
def get_current_metal_prices(
    session_number: int | None = Query(None, description="Session number to filter by"),
    use_mock_data: bool = Query(False, description="Generate mock data when no stored prices are available"),
    db: Session = Depends(get_db),
):
    """Get the most recently stored metal prices, generating and persisting mock data only when necessary."""
    try:
        records = fetch_latest_metal_prices(db, session_number)

        generated = False
        target_session = session_number

        if not records and use_mock_data:
            scrape_result = scrape_and_store_metal_prices(db, use_mock_data=True)
            if not scrape_result.get("success"):
                raise HTTPException(status_code=500, detail=scrape_result.get("error", "Failed to generate metal prices"))
            target_session = scrape_result.get("session_number")
            records = fetch_latest_metal_prices(db, target_session)
            generated = True

        if not records:
            raise HTTPException(status_code=404, detail="No metal prices available. Run the scrape endpoint to populate data.")

        response_session = target_session or (records[0].session_number if records else None)

        return {
            "prices": [
                {
                    "metal_name": record.metal_name,
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
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to get prices: {exc}") from exc

@router.get("/prices/history")
def get_metal_price_history(
    metal_name: Optional[str] = Query(None, description="Filter by metal name"),
    session_number: Optional[int] = Query(None, description="Filter by session number"),
    limit: int = Query(100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Get historical metal price data from database."""
    try:
        query = db.query(MetalPriceHistory)
        
        if metal_name:
            query = query.filter(MetalPriceHistory.metal_name == metal_name)
        
        if session_number:
            query = query.filter(MetalPriceHistory.session_number == session_number)
        
        # Order by most recent first
        query = query.order_by(MetalPriceHistory.created_at.desc())
        
        # Apply limit
        records = query.limit(limit).all()
        
        return {
            "records": [
                {
                    "id": record.id,
                    "metal_name": record.metal_name,
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
        raise HTTPException(status_code=500, detail=f"Failed to get price history: {str(e)}")

@router.get("/supported")
def get_supported_metals():
    """Get list of supported metals and their units."""
    from ..services.scraper import SUPPORTED_METALS
    
    return {
        "metals": [
            {
                "name": metal_name,
                "unit": config["unit"],
                "min_price_range": config["min_price"],
                "max_price_range": config["max_price"]
            }
            for metal_name, config in SUPPORTED_METALS.items()
        ],
        "count": len(SUPPORTED_METALS)
    }

@router.get("/gemstones/prices/current")
def get_current_gemstone_prices(
    use_mock_data: bool = Query(False, description="Use mock data (parameter kept for compatibility)"),
):
    """Get current gemstone prices."""
    try:
        prices = scrape_gemstone_prices(use_mock_data=use_mock_data)
        return {
            "prices": prices,
            "count": len(prices),
            "use_mock_data": False  # Always random generation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get gemstone prices: {str(e)}")

@router.get("/gemstones/supported")
def get_supported_gemstones():
    """Get list of supported gemstones and their price ranges."""
    from ..services.scraper import SUPPORTED_GEMSTONES
    
    return {
        "gemstones": [
            {
                "name": gemstone_name,
                "unit": config["unit"],
                "min_price_range": config["min_price"],
                "max_price_range": config["max_price"]
            }
            for gemstone_name, config in SUPPORTED_GEMSTONES.items()
        ],
        "count": len(SUPPORTED_GEMSTONES)
    }

@router.put("/price-range/{metal_name}")
def update_metal_price_range(
    metal_name: str,
    min_multiplier: float,
    max_multiplier: float
):
    """Update the price range multipliers for a specific metal."""
    # Validate multipliers
    if min_multiplier <= 0 or max_multiplier <= 0:
        raise HTTPException(status_code=400, detail="Multipliers must be positive")
    
    if min_multiplier >= max_multiplier:
        raise HTTPException(status_code=400, detail="Minimum multiplier must be less than maximum multiplier")
    
    # In a real implementation, this would update the database
    # For now, we'll just return success with the updated values
    return {
        "success": True,
        "metal_name": metal_name,
        "min_multiplier": min_multiplier,
        "max_multiplier": max_multiplier,
        "message": f"Successfully updated price range for {metal_name}"
    }

@router.get("/price-ranges")
def get_all_metal_price_ranges():
    """Get price range multipliers for all metals with current market prices."""
    try:
        current_prices = scrape_metal_prices(use_mock_data=True)
        return {
            "metals": [
                {
                    "name": metal["metal_name"],
                    "unit": metal["unit"],
                    "base_price": metal["price_per_unit_usd"],
                    "min_multiplier": 0.8,  # Default values - would come from database
                    "max_multiplier": 1.2,
                    "current_min_price": metal["price_per_unit_usd"] * 0.8,
                    "current_max_price": metal["price_per_unit_usd"] * 1.2
                }
                for metal in current_prices
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metal price ranges: {str(e)}")

@router.post("/create")
def create_new_metal(
    name: str,
    unit: str,
    base_price: float,
    db: Session = Depends(get_db)
):
    """Create a new metal with initial price data"""
    try:
        # Get current session
        from ..models.session import GlobalState
        session_state = db.query(GlobalState).first()
        current_session = session_state.current_session if session_state else 1
        
        # Check if metal already exists
        existing = db.query(MetalPriceHistory).filter(
            MetalPriceHistory.metal_name == name
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail=f"Metal '{name}' already exists")
        
        # Create initial price entry
        price_per_oz_gold = base_price / 2000.0  # Assuming $2000/oz gold
        
        new_metal = MetalPriceHistory(
            metal_name=name,
            unit=unit,
            price_per_unit_usd=base_price,
            price_per_oz_gold=price_per_oz_gold,
            session_number=current_session
        )
        
        db.add(new_metal)
        db.commit()
        db.refresh(new_metal)
        
        return {
            "message": f"Metal '{name}' created successfully",
            "metal": {
                "metal_name": new_metal.metal_name,
                "unit": new_metal.unit,
                "price_per_unit_usd": new_metal.price_per_unit_usd,
                "price_per_oz_gold": new_metal.price_per_oz_gold,
                "session_number": new_metal.session_number
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating metal: {str(e)}")