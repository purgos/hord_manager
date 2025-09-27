from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.gemstone import Gemstone, PlayerGemstone
from ..schemas.common import (
    GemstoneCreate,
    GemstoneRead,
    PlayerGemstoneCreate,
    PlayerGemstoneRead,
)

router = APIRouter(prefix="/gemstones", tags=["gemstones"])


@router.post("/", response_model=GemstoneRead)
def create_gemstone(
    payload: GemstoneCreate,
    upsert: bool = Query(False, description="If true, update existing gemstone instead of erroring."),
    db: Session = Depends(get_db),
):
    """Create a gemstone.

    If `upsert=true` and the name exists, its value_per_carat_oz_gold is updated and the updated row returned.
    """
    existing = db.query(Gemstone).filter(Gemstone.name == payload.name).first()
    if existing:
        if not upsert:
            raise HTTPException(status_code=400, detail="Gemstone name already exists")
        existing.value_per_carat_oz_gold = payload.value_per_carat_oz_gold
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    gm = Gemstone(name=payload.name, value_per_carat_oz_gold=payload.value_per_carat_oz_gold)
    db.add(gm)
    db.commit()
    db.refresh(gm)
    return gm


@router.get("/", response_model=list[GemstoneRead])
def list_gemstones(db: Session = Depends(get_db)):
    return db.query(Gemstone).order_by(Gemstone.name.asc()).all()


@router.put("/{gemstone_id}", response_model=GemstoneRead)
def update_gemstone(gemstone_id: int, payload: GemstoneCreate, db: Session = Depends(get_db)):
    """Update an existing gemstone."""
    gemstone = db.query(Gemstone).filter(Gemstone.id == gemstone_id).first()
    if not gemstone:
        raise HTTPException(status_code=404, detail="Gemstone not found")
    
    gemstone.name = payload.name
    gemstone.value_per_carat_oz_gold = payload.value_per_carat_oz_gold
    db.add(gemstone)
    db.commit()
    db.refresh(gemstone)
    return gemstone


@router.delete("/{gemstone_id}")
def delete_gemstone(gemstone_id: int, db: Session = Depends(get_db)):
    """Delete a gemstone."""
    gemstone = db.query(Gemstone).filter(Gemstone.id == gemstone_id).first()
    if not gemstone:
        raise HTTPException(status_code=404, detail="Gemstone not found")
    
    db.delete(gemstone)
    db.commit()
    return {"message": f"Gemstone '{gemstone.name}' deleted successfully"}


@router.post("/players/{player_id}", response_model=PlayerGemstoneRead)
def add_player_gemstone(player_id: int, payload: PlayerGemstoneCreate, db: Session = Depends(get_db)):
    # Ensure gemstone exists
    gemstone = db.query(Gemstone).filter(Gemstone.id == payload.gemstone_id).first()
    if not gemstone:
        raise HTTPException(status_code=404, detail="Gemstone not found")
    holding = PlayerGemstone(
        player_id=player_id,
        gemstone_id=payload.gemstone_id,
        carats=payload.carats,
        appraised_value_oz_gold=payload.carats * gemstone.value_per_carat_oz_gold,
    )
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return holding


@router.get("/players/{player_id}", response_model=list[PlayerGemstoneRead])
def list_player_gemstones(player_id: int, db: Session = Depends(get_db)):
    return (
        db.query(PlayerGemstone)
        .filter(PlayerGemstone.player_id == player_id)
        .order_by(PlayerGemstone.created_at.asc())
        .all()
    )
