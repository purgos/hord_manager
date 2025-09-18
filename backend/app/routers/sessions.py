from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.session import GlobalState
from ..schemas.common import SessionStateRead

router = APIRouter(prefix="/sessions", tags=["sessions"]) 

@router.get("/state", response_model=SessionStateRead)
def get_state(db: Session = Depends(get_db)):
    state = db.query(GlobalState).first()
    if not state:
        state = GlobalState(current_session=0)
        db.add(state)
        db.commit()
        db.refresh(state)
    return SessionStateRead(current_session=state.current_session)

@router.post("/increment", response_model=SessionStateRead)
def increment_session(db: Session = Depends(get_db)):
    state = db.query(GlobalState).first()
    if not state:
        state = GlobalState(current_session=0)
        db.add(state)
    state.current_session += 1
    db.commit()
    db.refresh(state)
    return SessionStateRead(current_session=state.current_session)
