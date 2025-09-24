from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.session import GlobalState
from ..schemas.common import SessionStateRead
from ..services.scraper import scrape_and_store_metal_prices
import logging

logger = logging.getLogger(__name__)

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
    
    # Automatically scrape metal prices when session increments
    try:
        logger.info(f"Session incremented to {state.current_session}, triggering metal price scraping")
        scrape_result = scrape_and_store_metal_prices(db, use_mock_data=False)
        if scrape_result["success"]:
            logger.info(f"Successfully scraped {scrape_result['prices_stored']} metal prices for session {state.current_session}")
        else:
            logger.warning(f"Metal price scraping failed: {scrape_result['message']}")
    except Exception as e:
        logger.error(f"Error during automatic metal price scraping: {e}")
        # Don't fail the session increment if scraping fails
    
    return SessionStateRead(current_session=state.current_session)
