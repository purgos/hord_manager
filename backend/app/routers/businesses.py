from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..core.database import get_db
from ..models.business import Business, BusinessInvestor
from ..models.player import Player
from ..models.gm import InboxMessage
from ..schemas.common import (
    BusinessCreate,
    BusinessRead,
    BusinessUpdate,
    BusinessInvestorUpsert,
    BusinessInvestorRead,
    BusinessWithInvestorsRead,
    BusinessPetitionCreate,
)

router = APIRouter(prefix="/businesses", tags=["businesses"]) 

@router.post("/", response_model=BusinessRead)
def create_business(payload: BusinessCreate, db: Session = Depends(get_db)):
    # Simple duplicate name prevention
    existing = db.query(Business).filter(Business.name == payload.name).first()
    if existing:
        # Return existing to make this endpoint idempotent for repeated test/dev calls
        return existing
    b = Business(
        name=payload.name,
        description=payload.description,
        principle_activity=payload.principle_activity,
        net_worth_oz_gold=payload.net_worth_oz_gold,
        income_per_session_oz_gold=payload.income_per_session_oz_gold,
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    return b

@router.get("/", response_model=list[BusinessRead])
def list_businesses(db: Session = Depends(get_db)):
    businesses = db.query(Business).all()
    return businesses

@router.get("/{business_id}", response_model=BusinessWithInvestorsRead)
def get_business(business_id: int, db: Session = Depends(get_db)):
    b = db.query(Business).filter(Business.id == business_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")
    # Pydantic from_attributes should handle nested investors; we manually adapt investors
    return BusinessWithInvestorsRead(
        id=b.id,
        name=b.name,
        description=b.description,
        principle_activity=b.principle_activity,
        net_worth_oz_gold=b.net_worth_oz_gold,
        income_per_session_oz_gold=b.income_per_session_oz_gold,
        created_at=b.created_at,  # type: ignore[arg-type]
        updated_at=b.updated_at,  # type: ignore[arg-type]
        investors=[
            BusinessInvestorRead(
                id=i.id,
                business_id=i.business_id,
                player_id=i.player_id,
                equity_percent=i.equity_percent,
                invested_oz_gold=i.invested_oz_gold,
                created_at=i.created_at,  # type: ignore[arg-type]
                updated_at=i.updated_at,  # type: ignore[arg-type]
            )
            for i in b.investors
        ],
    )

@router.patch("/{business_id}", response_model=BusinessRead)
def patch_business(business_id: int, payload: BusinessUpdate, db: Session = Depends(get_db)):
    b = db.query(Business).filter(Business.id == business_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(b, field, value)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b

@router.post("/{business_id}/investors", response_model=list[BusinessInvestorRead])
def upsert_investors(business_id: int, investors: list[BusinessInvestorUpsert], db: Session = Depends(get_db)):
    b = db.query(Business).filter(Business.id == business_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")
    # Index existing by player_id
    existing = {inv.player_id: inv for inv in b.investors}
    for inv_payload in investors:
        if inv_payload.player_id in existing:
            inv = existing[inv_payload.player_id]
            if inv_payload.equity_percent is not None:
                inv.equity_percent = inv_payload.equity_percent
            if inv_payload.invested_oz_gold is not None:
                inv.invested_oz_gold = inv_payload.invested_oz_gold
        else:
            # ensure player exists
            player = db.query(Player).filter(Player.id == inv_payload.player_id).first()
            if not player:
                raise HTTPException(status_code=404, detail=f"Player {inv_payload.player_id} not found")
            # Append through relationship so in-memory collection reflects new rows
            new_inv = BusinessInvestor(
                business_id=b.id,
                player_id=inv_payload.player_id,
                equity_percent=inv_payload.equity_percent or 0.0,
                invested_oz_gold=inv_payload.invested_oz_gold or 0.0,
            )
            b.investors.append(new_inv)
    db.flush()  # ensure PKs assigned
    # Enforce equity percent <= 100 total
    total_equity = sum(inv.equity_percent for inv in b.investors)
    if total_equity > 100.0001:  # tiny tolerance
        raise HTTPException(status_code=400, detail=f"Total equity percent exceeds 100 (got {total_equity})")
    db.commit()
    return [
        BusinessInvestorRead(
            id=i.id,
            business_id=i.business_id,
            player_id=i.player_id,
            equity_percent=i.equity_percent,
            invested_oz_gold=i.invested_oz_gold,
            created_at=i.created_at,  # type: ignore[arg-type]
            updated_at=i.updated_at,  # type: ignore[arg-type]
        )
        for i in b.investors
    ]

@router.delete("/{business_id}/investors/{player_id}", response_model=list[BusinessInvestorRead])
def remove_investor(
    business_id: int,
    player_id: int,
    rebalance: bool = Query(False, description="If true, redistribute removed equity proportionally among remaining investors"),
    db: Session = Depends(get_db),
):
    b = db.query(Business).filter(Business.id == business_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")
    target = None
    for inv in b.investors:
        if inv.player_id == player_id:
            target = inv
            break
    if not target:
        raise HTTPException(status_code=404, detail="Investor not found for business")
    removed_equity = target.equity_percent
    b.investors.remove(target)
    db.flush()
    if rebalance and removed_equity > 0 and b.investors:
        # redistribute proportionally to current equity holdings
        current_total = sum(i.equity_percent for i in b.investors)
        if current_total <= 0:
            # If all remaining were zero, give all to first investor
            b.investors[0].equity_percent = removed_equity
        else:
            for inv in b.investors:
                share = inv.equity_percent / current_total
                inv.equity_percent += removed_equity * share
    # Final validation
    total_equity = sum(i.equity_percent for i in b.investors)
    if total_equity > 100.0001:
        raise HTTPException(status_code=400, detail=f"Total equity percent exceeds 100 after removal (got {total_equity})")
    db.commit()
    return [
        BusinessInvestorRead(
            id=i.id,
            business_id=i.business_id,
            player_id=i.player_id,
            equity_percent=i.equity_percent,
            invested_oz_gold=i.invested_oz_gold,
            created_at=i.created_at,  # type: ignore[arg-type]
            updated_at=i.updated_at,  # type: ignore[arg-type]
        )
        for i in b.investors
    ]

@router.post("/petitions", status_code=202)
def create_business_petition(payload: BusinessPetitionCreate, db: Session = Depends(get_db)):
    # Player existence check
    player = db.query(Player).filter(Player.id == payload.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    # Create an inbox message for GM review (simplified payload)
    msg = InboxMessage(
        type="business_petition",
        status="pending",
        payload={
            "name": payload.name,
            "description": payload.description,
            "principle_activity": payload.principle_activity,
            "initial_investment_oz_gold": payload.initial_investment_oz_gold,
        },
        player_id=player.id,
    )
    db.add(msg)
    db.commit()
    return {"status": "accepted", "message_id": msg.id}
