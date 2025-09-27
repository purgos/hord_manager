from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..core.database import get_db
from ..models.player import Player
from ..models.currency import Currency, CurrencyDenomination, PegType
from ..models.gemstone import Gemstone
from ..models.metal import MetalPriceHistory
from ..models.material import MaterialPriceHistory
from ..models.session import GlobalState
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/data-management", tags=["data-management"])

@router.post("/reset/users")
async def reset_users_to_default(db: Session = Depends(get_db)):
    """Reset all users to default GM and Player accounts"""
    try:
        # Delete all existing users
        db.execute(text("DELETE FROM players"))
        

        
        # Add default users (simple player accounts)
        default_users = [
            {
                "name": "gm",
                "password_hash": "gm123",  # In production this should be hashed
                "is_approved": True
            },
            {
                "name": "player1", 
                "password_hash": "player123",  # In production this should be hashed
                "is_approved": True
            }
        ]
        
        for user_data in default_users:
            new_user = Player(**user_data)
            db.add(new_user)
        
        db.commit()
        logger.info("Users reset to default successfully")
        return {"message": "Users reset to default successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting users: {e}")
        raise HTTPException(status_code=500, detail=f"Error resetting users: {str(e)}")

@router.post("/reset/currencies")
async def reset_currencies_to_default(db: Session = Depends(get_db)):
    """Reset all currencies to default values"""
    try:
        # Delete all existing currencies
        db.execute(text("DELETE FROM currencies"))
        

        
        # Add default currency (only USD)
        default_currencies = [
            {"name": "USD", "rate": 1.0},
        ]
        
        for currency_data in default_currencies:
            # Create currency with proper peg structure
            new_currency = Currency(
                name=currency_data["name"],
                peg_type=PegType.CURRENCY,
                peg_target="USD",
                base_unit_value=currency_data["rate"]
            )
            db.add(new_currency)
        
        db.commit()
        logger.info("Currencies reset to default successfully")
        return {"message": "Currencies reset to default successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting currencies: {e}")
        raise HTTPException(status_code=500, detail=f"Error resetting currencies: {str(e)}")

@router.post("/reset/metals")
async def reset_metals_to_default(db: Session = Depends(get_db)):
    """Reset all metal price history to default values"""
    try:
        # Delete all existing metal price history
        db.execute(text("DELETE FROM metal_price_history"))
        

        
        # Add 20 default metal prices for session 1
        default_metals = [
            {"metal_name": "Gold", "unit": "oz", "price_per_unit_usd": 2000.0, "price_per_oz_gold": 1.0, "session_number": 1},
            {"metal_name": "Silver", "unit": "oz", "price_per_unit_usd": 25.0, "price_per_oz_gold": 0.0125, "session_number": 1},
            {"metal_name": "Platinum", "unit": "oz", "price_per_unit_usd": 1000.0, "price_per_oz_gold": 0.5, "session_number": 1},
            {"metal_name": "Steel", "unit": "lb", "price_per_unit_usd": 0.75, "price_per_oz_gold": 0.000375, "session_number": 1},
            {"metal_name": "Lithium", "unit": "kg", "price_per_unit_usd": 185.0, "price_per_oz_gold": 0.0925, "session_number": 1},
            {"metal_name": "Iron", "unit": "lb", "price_per_unit_usd": 0.8, "price_per_oz_gold": 0.0004, "session_number": 1},
            {"metal_name": "Lead", "unit": "lb", "price_per_unit_usd": 1.20, "price_per_oz_gold": 0.0006, "session_number": 1},
            {"metal_name": "Copper", "unit": "lb", "price_per_unit_usd": 4.0, "price_per_oz_gold": 0.002, "session_number": 1},
            {"metal_name": "Aluminum", "unit": "lb", "price_per_unit_usd": 0.95, "price_per_oz_gold": 0.000475, "session_number": 1},
            {"metal_name": "Tin", "unit": "lb", "price_per_unit_usd": 12.5, "price_per_oz_gold": 0.00625, "session_number": 1},
            {"metal_name": "Zinc", "unit": "lb", "price_per_unit_usd": 1.35, "price_per_oz_gold": 0.000675, "session_number": 1},
            {"metal_name": "Nickel", "unit": "lb", "price_per_unit_usd": 8.75, "price_per_oz_gold": 0.004375, "session_number": 1},
            {"metal_name": "Cobalt", "unit": "lb", "price_per_unit_usd": 35.0, "price_per_oz_gold": 0.0175, "session_number": 1},
            {"metal_name": "Titanium", "unit": "lb", "price_per_unit_usd": 15.0, "price_per_oz_gold": 0.0075, "session_number": 1},
            {"metal_name": "Palladium", "unit": "oz", "price_per_unit_usd": 2300.0, "price_per_oz_gold": 1.15, "session_number": 1},
            {"metal_name": "Rhodium", "unit": "oz", "price_per_unit_usd": 4500.0, "price_per_oz_gold": 2.25, "session_number": 1},
            {"metal_name": "Brass", "unit": "lb", "price_per_unit_usd": 2.85, "price_per_oz_gold": 0.001425, "session_number": 1},
            {"metal_name": "Bronze", "unit": "lb", "price_per_unit_usd": 3.20, "price_per_oz_gold": 0.0016, "session_number": 1},
            {"metal_name": "Chromium", "unit": "lb", "price_per_unit_usd": 6.50, "price_per_oz_gold": 0.00325, "session_number": 1},
            {"metal_name": "Magnesium", "unit": "lb", "price_per_unit_usd": 2.10, "price_per_oz_gold": 0.00105, "session_number": 1},
        ]
        
        for metal_data in default_metals:
            new_metal = MetalPriceHistory(**metal_data)
            db.add(new_metal)
        
        db.commit()
        logger.info("Metal prices reset to default successfully")
        return {"message": "Metal prices reset to default successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting metals: {e}")
        raise HTTPException(status_code=500, detail=f"Error resetting metals: {str(e)}")

@router.post("/reset/materials")
async def reset_materials_to_default(db: Session = Depends(get_db)):
    """Reset all material price history to default values"""
    try:
        # Delete all existing material price history
        db.execute(text("DELETE FROM material_price_history"))
        

        
        # Add 20 default material prices for session 1
        default_materials = [
            {"material_name": "Wood", "unit": "board ft", "price_per_unit_usd": 2.50, "price_per_oz_gold": 0.00125, "session_number": 1},
            {"material_name": "Carbon", "unit": "lb", "price_per_unit_usd": 15.0, "price_per_oz_gold": 0.0075, "session_number": 1},
            {"material_name": "Cotton", "unit": "lb", "price_per_unit_usd": 0.75, "price_per_oz_gold": 0.000375, "session_number": 1},
            {"material_name": "Flax", "unit": "lb", "price_per_unit_usd": 1.80, "price_per_oz_gold": 0.0009, "session_number": 1},
            {"material_name": "Sulfur", "unit": "lb", "price_per_unit_usd": 0.25, "price_per_oz_gold": 0.000125, "session_number": 1},
            {"material_name": "Stone", "unit": "ton", "price_per_unit_usd": 18.0, "price_per_oz_gold": 0.009, "session_number": 1},
            {"material_name": "Silicon", "unit": "lb", "price_per_unit_usd": 1.20, "price_per_oz_gold": 0.0006, "session_number": 1},
            {"material_name": "Gallium", "unit": "oz", "price_per_unit_usd": 450.0, "price_per_oz_gold": 0.225, "session_number": 1},
            {"material_name": "Leather", "unit": "sq ft", "price_per_unit_usd": 6.25, "price_per_oz_gold": 0.003125, "session_number": 1},
            {"material_name": "Wool", "unit": "lb", "price_per_unit_usd": 3.20, "price_per_oz_gold": 0.0016, "session_number": 1},
            {"material_name": "Clay", "unit": "ton", "price_per_unit_usd": 25.0, "price_per_oz_gold": 0.0125, "session_number": 1},
            {"material_name": "Sand", "unit": "ton", "price_per_unit_usd": 15.0, "price_per_oz_gold": 0.0075, "session_number": 1},
            {"material_name": "Hemp", "unit": "lb", "price_per_unit_usd": 2.10, "price_per_oz_gold": 0.00105, "session_number": 1},
            {"material_name": "Bamboo", "unit": "board ft", "price_per_unit_usd": 1.90, "price_per_oz_gold": 0.00095, "session_number": 1},
            {"material_name": "Cork", "unit": "lb", "price_per_unit_usd": 4.50, "price_per_oz_gold": 0.00225, "session_number": 1},
            {"material_name": "Rubber", "unit": "lb", "price_per_unit_usd": 1.45, "price_per_oz_gold": 0.000725, "session_number": 1},
            {"material_name": "Glass", "unit": "lb", "price_per_unit_usd": 0.95, "price_per_oz_gold": 0.000475, "session_number": 1},
            {"material_name": "Coal", "unit": "ton", "price_per_unit_usd": 65.0, "price_per_oz_gold": 0.0325, "session_number": 1},
            {"material_name": "Oil", "unit": "barrel", "price_per_unit_usd": 75.0, "price_per_oz_gold": 0.0375, "session_number": 1},
            {"material_name": "Phosphorus", "unit": "lb", "price_per_unit_usd": 2.80, "price_per_oz_gold": 0.0014, "session_number": 1},
        ]
        
        for material_data in default_materials:
            new_material = MaterialPriceHistory(**material_data)
            db.add(new_material)
        
        db.commit()
        logger.info("Material prices reset to default successfully")
        return {"message": "Material prices reset to default successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting materials: {e}")
        raise HTTPException(status_code=500, detail=f"Error resetting materials: {str(e)}")

@router.post("/reset/gemstones")
async def reset_gemstones_to_default(db: Session = Depends(get_db)):
    """Reset all gemstones to default values"""
    try:
        # Delete all existing gemstones
        db.execute(text("DELETE FROM gemstones"))
        

        
        # Add 20 default gemstones with realistic prices (in oz gold per carat)
        default_gemstones = [
            {"name": "Diamond", "value_per_carat_oz_gold": 2.62},
            {"name": "Ruby", "value_per_carat_oz_gold": 1.58},
            {"name": "Emerald", "value_per_carat_oz_gold": 1.42},
            {"name": "Sapphire", "value_per_carat_oz_gold": 0.96},
            {"name": "Amethyst", "value_per_carat_oz_gold": 0.19},
            {"name": "Topaz", "value_per_carat_oz_gold": 0.27},
            {"name": "Garnet", "value_per_carat_oz_gold": 0.15},
            {"name": "Peridot", "value_per_carat_oz_gold": 0.12},
            {"name": "Aquamarine", "value_per_carat_oz_gold": 0.44},
            {"name": "Citrine", "value_per_carat_oz_gold": 0.08},
            {"name": "Tourmaline", "value_per_carat_oz_gold": 0.22},
            {"name": "Opal", "value_per_carat_oz_gold": 0.33},
            {"name": "Turquoise", "value_per_carat_oz_gold": 0.06},
            {"name": "Jade", "value_per_carat_oz_gold": 0.39},
            {"name": "Onyx", "value_per_carat_oz_gold": 0.04},
            {"name": "Moonstone", "value_per_carat_oz_gold": 0.10},
            {"name": "Labradorite", "value_per_carat_oz_gold": 0.04},
            {"name": "Tanzanite", "value_per_carat_oz_gold": 0.62},
            {"name": "Alexandrite", "value_per_carat_oz_gold": 2.28},
            {"name": "Spinel", "value_per_carat_oz_gold": 0.49}
        ]
        
        for gemstone_data in default_gemstones:
            new_gemstone = Gemstone(**gemstone_data)
            db.add(new_gemstone)
        
        db.commit()
        logger.info("Gemstones reset to default successfully")
        return {"message": "Gemstones reset to default successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting gemstones: {e}")
        raise HTTPException(status_code=500, detail=f"Error resetting gemstones: {str(e)}")

@router.post("/reset/sessions")
async def reset_sessions_to_default(db: Session = Depends(get_db)):
    """Reset all sessions to default values"""
    try:
        # Delete all existing session state
        db.execute(text("DELETE FROM global_state"))
        

        
        # Add default session state
        default_session = GlobalState(current_session=1)
        db.add(default_session)
        
        db.commit()
        logger.info("Sessions reset to default successfully")
        return {"message": "Sessions reset to default successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Error resetting sessions: {str(e)}")

@router.post("/reset/all")
async def reset_all_data_to_default(db: Session = Depends(get_db)):
    """Reset ALL data to default values"""
    try:
        # Call all reset functions
        await reset_sessions_to_default(db)
        await reset_gemstones_to_default(db)
        await reset_materials_to_default(db)
        await reset_metals_to_default(db)
        await reset_currencies_to_default(db)
        await reset_users_to_default(db)
        
        logger.info("All data reset to default successfully")
        return {"message": "All data reset to default successfully"}
    except Exception as e:
        logger.error(f"Error resetting all data: {e}")
        raise HTTPException(status_code=500, detail=f"Error resetting all data: {str(e)}")