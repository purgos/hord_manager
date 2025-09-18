from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.currency import Currency, CurrencyDenomination
from ..schemas.common import (
    CurrencyCreate,
    CurrencyRead,
    CurrencyDenominationCreate,
    CurrencyDenominationRead,
    CurrencyUpdate,
    CurrencyDenominationUpdate,
)

router = APIRouter(prefix="/currencies", tags=["currencies"]) 

@router.post("/", response_model=CurrencyRead)
def create_currency(
    payload: CurrencyCreate,
    upsert: bool = Query(False, description="If true, update existing currency (and replace denominations)."),
    db: Session = Depends(get_db),
):
    """Create a currency.

    Upsert semantics when `upsert=true`:
    - Updates base_unit_value_oz_gold.
    - Replaces existing denominations with those provided (full replacement, not merge).
    """
    existing = db.query(Currency).filter(Currency.name == payload.name).first()
    if existing:
        if not upsert:
            raise HTTPException(status_code=400, detail="Currency already exists")
        # Update value
        existing.base_unit_value_oz_gold = payload.base_unit_value_oz_gold
        # Replace denominations
        for den in list(existing.denominations):
            db.delete(den)
        db.flush()
        for d in payload.denominations:
            db.add(
                CurrencyDenomination(
                    currency_id=existing.id,
                    name=d.name,
                    value_in_base_units=d.value_in_base_units,
                )
            )
        db.commit()
        db.refresh(existing)
        target = existing
    else:
        currency = Currency(name=payload.name, base_unit_value_oz_gold=payload.base_unit_value_oz_gold)
        db.add(currency)
        db.flush()
        for d in payload.denominations:
            db.add(CurrencyDenomination(currency_id=currency.id, name=d.name, value_in_base_units=d.value_in_base_units))
        db.commit()
        db.refresh(currency)
        target = currency

    return CurrencyRead(
        id=target.id,
        name=target.name,
        base_unit_value_oz_gold=target.base_unit_value_oz_gold,
        denominations=[
            CurrencyDenominationRead(id=den.id, name=den.name, value_in_base_units=den.value_in_base_units)
            for den in target.denominations
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


@router.patch("/{currency_id}", response_model=CurrencyRead)
def patch_currency(currency_id: int, payload: CurrencyUpdate, db: Session = Depends(get_db)):
    """Partially update a currency.

    - base_unit_value_oz_gold: if provided, update.
    - denominations_add_or_update: list of denomination objects:
        * if id provided -> update existing fields (name/value) if not None
        * if id missing -> create new denomination
    - denomination_ids_remove: list of denomination IDs to delete
    """
    currency = db.query(Currency).filter(Currency.id == currency_id).first()
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")

    data = payload.model_dump(exclude_unset=True)
    if "base_unit_value_oz_gold" in data and data["base_unit_value_oz_gold"] is not None:
        currency.base_unit_value_oz_gold = data["base_unit_value_oz_gold"]

    # Remove denominations
    for den_id in data.get("denomination_ids_remove", []):
        den = next((d for d in currency.denominations if d.id == den_id), None)
        if den:
            db.delete(den)

    # Add / update denominations
    for den_payload in data.get("denominations_add_or_update", []):
        den_id = den_payload.get("id")
        if den_id:
            den = next((d for d in currency.denominations if d.id == den_id), None)
            if not den:
                raise HTTPException(status_code=404, detail=f"Denomination id {den_id} not found")
            if den_payload.get("name") is not None:
                den.name = den_payload["name"]
            if den_payload.get("value_in_base_units") is not None:
                den.value_in_base_units = den_payload["value_in_base_units"]
        else:
            # create new
            new_den = CurrencyDenomination(
                currency_id=currency.id,
                name=den_payload.get("name") or "Unnamed",
                value_in_base_units=den_payload.get("value_in_base_units") or 0.0,
            )
            db.add(new_den)

    db.add(currency)
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
