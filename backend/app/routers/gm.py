from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.gm import GMSettings, InboxMessage
from ..schemas.common import GMSettingsRead, GMSettingsUpdate, InboxMessageRead

router = APIRouter(prefix="/gm", tags=["gm"])


def _get_or_create_settings(db: Session) -> GMSettings:
    settings = db.query(GMSettings).first()
    if not settings:
        settings = GMSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("/settings", response_model=GMSettingsRead)
def get_settings(db: Session = Depends(get_db)):
    settings = _get_or_create_settings(db)
    return settings


@router.patch("/settings", response_model=GMSettingsRead)
def update_settings(payload: GMSettingsUpdate, db: Session = Depends(get_db)):
    settings = _get_or_create_settings(db)
    data = payload.model_dump(exclude_unset=True)
    if not data:
        return settings
    for k, v in data.items():
        setattr(settings, k, v)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


@router.get("/inbox", response_model=list[InboxMessageRead])
def list_inbox(db: Session = Depends(get_db)):
    return db.query(InboxMessage).order_by(InboxMessage.created_at.desc()).all()
