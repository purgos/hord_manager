from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..models.metal import MetalPriceHistory
from ..services.scraper import scrape_and_store_metal_prices, scrape_metal_prices

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
            return {
                "message": result["message"],
                "prices_stored": result["prices_stored"],
                "scraped_prices": result["scraped_prices"],
                "use_mock_data": result["use_mock_data"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@router.get("/prices/current")
def get_current_metal_prices(
    use_mock_data: bool = Query(False, description="Use mock data instead of scraping"),
):
    """Get current metal prices without storing them in database."""
    try:
        prices = scrape_metal_prices(use_mock_data=use_mock_data)
        return {
            "prices": prices,
            "count": len(prices),
            "use_mock_data": use_mock_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get prices: {str(e)}")

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