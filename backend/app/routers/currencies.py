from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
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
from ..services.conversion import get_conversion_service


# Additional Pydantic models for conversion endpoints
class ConversionRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str


class ConversionResponse(BaseModel):
    amount: float
    from_currency: str
    to_currency: str
    converted_amount: float
    oz_gold_equivalent: float


class ValueDisplayRequest(BaseModel):
    oz_gold_value: float
    target_currencies: Optional[List[str]] = None

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


# === CONVERSION ENDPOINTS ===

@router.post("/convert", response_model=ConversionResponse)
async def convert_currency(
    request: ConversionRequest, 
    db: Session = Depends(get_db)
):
    """Convert between two currencies."""
    conversion_service = get_conversion_service(db)
    
    try:
        converted_amount = conversion_service.convert_between_currencies(
            request.amount, request.from_currency, request.to_currency
        )
        
        # Also get gold equivalent
        oz_gold_equivalent = conversion_service.currency_to_oz_gold(
            request.amount, request.from_currency
        )
        
        return ConversionResponse(
            amount=request.amount,
            from_currency=request.from_currency,
            to_currency=request.to_currency,
            converted_amount=converted_amount,
            oz_gold_equivalent=oz_gold_equivalent
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/convert/from-gold")
async def convert_from_gold(
    oz_gold: float,
    currency: str,
    db: Session = Depends(get_db)
):
    """Convert ounces of gold to specified currency."""
    conversion_service = get_conversion_service(db)
    
    try:
        amount = conversion_service.oz_gold_to_currency(oz_gold, currency)
        breakdown = conversion_service.format_currency_with_denominations(amount, currency)
        
        return {
            "oz_gold": oz_gold,
            "currency": currency,
            "amount": amount,
            "breakdown": breakdown
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/convert/to-gold")
async def convert_to_gold(
    amount: float,
    currency: str,
    db: Session = Depends(get_db)
):
    """Convert currency amount to ounces of gold."""
    conversion_service = get_conversion_service(db)
    
    try:
        oz_gold = conversion_service.currency_to_oz_gold(amount, currency)
        
        return {
            "amount": amount,
            "currency": currency,
            "oz_gold": oz_gold
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/convert/usd")
async def convert_usd(
    amount: float,
    to_currency: Optional[str] = None,
    from_currency: Optional[str] = None,
    session_number: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Convert to/from USD using current gold prices."""
    conversion_service = get_conversion_service(db)
    
    try:
        if to_currency:
            # Convert USD to target currency
            oz_gold = conversion_service.usd_to_oz_gold(amount, session_number)
            converted_amount = conversion_service.oz_gold_to_currency(oz_gold, to_currency)
            
            return {
                "amount": amount,
                "from_currency": "USD",
                "to_currency": to_currency,
                "converted_amount": converted_amount,
                "oz_gold_equivalent": oz_gold
            }
        elif from_currency:
            # Convert from currency to USD
            oz_gold = conversion_service.currency_to_oz_gold(amount, from_currency)
            usd_amount = conversion_service.oz_gold_to_usd(oz_gold, session_number)
            
            return {
                "amount": amount,
                "from_currency": from_currency,
                "to_currency": "USD",
                "converted_amount": usd_amount,
                "oz_gold_equivalent": oz_gold
            }
        else:
            raise HTTPException(status_code=400, detail="Must specify either to_currency or from_currency")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rates/{base_currency}")
async def get_conversion_rates(
    base_currency: str = "USD",
    db: Session = Depends(get_db)
):
    """Get conversion rates for all currencies relative to base currency."""
    conversion_service = get_conversion_service(db)
    
    try:
        rates = conversion_service.get_conversion_rates(base_currency)
        return rates
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/display")
async def display_value_in_currencies(
    request: ValueDisplayRequest,
    db: Session = Depends(get_db)
):
    """Display a gold value in multiple currencies with denominations."""
    conversion_service = get_conversion_service(db)
    
    try:
        display = conversion_service.convert_value_display(
            request.oz_gold_value, 
            request.target_currencies
        )
        return display
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/breakdown/{currency_name}")
async def get_currency_breakdown(
    currency_name: str,
    amount: float,
    db: Session = Depends(get_db)
):
    """Get denomination breakdown for a currency amount."""
    conversion_service = get_conversion_service(db)
    
    try:
        breakdown = conversion_service.format_currency_with_denominations(amount, currency_name)
        return breakdown
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/metals/value")
async def get_metal_value(
    metal_name: str,
    amount: float,
    unit: str,
    session_number: Optional[int] = None,
    target_currencies: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    """Get value of metal amount in various currencies."""
    conversion_service = get_conversion_service(db)
    
    try:
        oz_gold_value = conversion_service.metal_value_to_oz_gold(
            metal_name, amount, unit, session_number
        )
        
        display = conversion_service.convert_value_display(
            oz_gold_value, 
            target_currencies
        )
        
        return {
            "metal_name": metal_name,
            "amount": amount,
            "unit": unit,
            "session_number": session_number,
            "oz_gold_value": oz_gold_value,
            "conversions": display["conversions"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/gemstones/value")
async def get_gemstone_value(
    gemstone_name: str,
    carats: float,
    target_currencies: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    """Get value of gemstone carats in various currencies."""
    conversion_service = get_conversion_service(db)
    
    try:
        oz_gold_value = conversion_service.gemstone_value_to_oz_gold(gemstone_name, carats)
        
        display = conversion_service.convert_value_display(
            oz_gold_value, 
            target_currencies
        )
        
        return {
            "gemstone_name": gemstone_name,
            "carats": carats,
            "oz_gold_value": oz_gold_value,
            "conversions": display["conversions"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
