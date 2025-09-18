from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.currency import Currency, CurrencyDenomination
from ..schemas.common import (
    CurrencyCreate,
    CurrencyRead,
    CurrencyDenominationCreate,
    CurrencyDenominationRead,
)

router = APIRouter(prefix="/currencies", tags=["currencies"]) 

@router.post("/", response_model=CurrencyRead)
def create_currency(payload: CurrencyCreate, db: Session = Depends(get_db)):
    existing = db.query(Currency).filter(Currency.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Currency already exists")
    currency = Currency(name=payload.name, base_unit_value_oz_gold=payload.base_unit_value_oz_gold)
    db.add(currency)
    db.flush()
    for d in payload.denominations:
        db.add(CurrencyDenomination(currency_id=currency.id, name=d.name, value_in_base_units=d.value_in_base_units))
    db.commit()
    db.refresh(currency)
    return CurrencyRead(
        id=currency.id,
        name=currency.name,
        base_unit_value_oz_gold=currency.base_unit_value_oz_gold,
        denominations=[
            CurrencyDenominationRead(id=den.id, name=den.name, value_in_base_units=den.value_in_base_units)
            for den in currency.denominations
        ],
    )

@router.get("/", response_model=list[CurrencyRead])
def list_currencies(db: Session = Depends(get_db)):
    currencies = db.query(Currency).all()
    return [
        CurrencyRead(
            id=c.id,
            name=c.name,
            base_unit_value_oz_gold=c.base_unit_value_oz_gold,
            denominations=[
                CurrencyDenominationRead(id=den.id, name=den.name, value_in_base_units=den.value_in_base_units)
                for den in c.denominations
            ],
        )
        for c in currencies
    ]
