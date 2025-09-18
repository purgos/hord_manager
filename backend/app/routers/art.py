from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.art import ArtItem
from ..schemas.common import ArtItemCreate, ArtItemRead, ArtItemUpdate

router = APIRouter(prefix="/art", tags=["art"]) 

@router.post("/", response_model=ArtItemRead)
def create_art(payload: ArtItemCreate, db: Session = Depends(get_db)):
    art = ArtItem(
        name=payload.name,
        description=payload.description,
        player_id=payload.player_id,
    )
    db.add(art)
    db.commit()
    db.refresh(art)
    return art

@router.get("/", response_model=list[ArtItemRead])
def list_art(db: Session = Depends(get_db)):
    items = db.query(ArtItem).all()
    return items

@router.patch("/{art_id}", response_model=ArtItemRead)
def patch_art(art_id: int, payload: ArtItemUpdate, db: Session = Depends(get_db)):
    art = db.query(ArtItem).filter(ArtItem.id == art_id).first()
    if not art:
        raise HTTPException(status_code=404, detail="Art item not found")
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(art, field, value)
    db.add(art)
    db.commit()
    db.refresh(art)
    return art
