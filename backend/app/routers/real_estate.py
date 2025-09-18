from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.art import RealEstateProperty
from ..schemas.common import RealEstateCreate, RealEstateRead, RealEstateUpdate

router = APIRouter(prefix="/real-estate", tags=["real-estate"]) 

@router.post("/", response_model=RealEstateRead)
def create_property(payload: RealEstateCreate, db: Session = Depends(get_db)):
    prop = RealEstateProperty(
        name=payload.name,
        location=payload.location,
        description=payload.description,
        player_id=payload.player_id,
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop

@router.get("/", response_model=list[RealEstateRead])
def list_properties(db: Session = Depends(get_db)):
    props = db.query(RealEstateProperty).all()
    return props

@router.patch("/{property_id}", response_model=RealEstateRead)
def patch_property(property_id: int, payload: RealEstateUpdate, db: Session = Depends(get_db)):
    prop = db.query(RealEstateProperty).filter(RealEstateProperty.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(prop, field, value)
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop
