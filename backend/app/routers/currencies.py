from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..core.database import get_db
from ..models.currency import Currency, CurrencyDenomination, PegType
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


def _coerce_peg_type(raw: str | PegType | None) -> PegType:
    """Normalize incoming peg type values, accepting enum members, names, or values."""
    if isinstance(raw, PegType):
        return raw
    if raw is None:
        raise HTTPException(status_code=400, detail="peg_type is required")

    if not isinstance(raw, str):
        raise HTTPException(status_code=400, detail="peg_type must be a string")

    value = raw.strip()
    if not value:
        raise HTTPException(status_code=400, detail="peg_type cannot be empty")

    # Try enum name lookup (uppercase)
    try:
        return PegType[value.upper()]
    except KeyError:
        pass

    # Fall back to enum value lookup (lowercase in models)
    try:
        return PegType(value.lower())
    except ValueError as exc:  # pragma: no cover - defensive branch
        raise HTTPException(status_code=400, detail=f"Invalid peg_type '{raw}'") from exc


def _ensure_base_currencies(db: Session) -> None:
    """Ensure only USD is automatically managed as the base currency."""
    changed = False

    usd = db.query(Currency).filter(Currency.name == "USD").first()
    if usd is None:
        usd = Currency(name="USD", peg_type=PegType.CURRENCY, peg_target="USD", base_unit_value=1.0)
        db.add(usd)
        db.flush()
        db.add_all(
            [
                CurrencyDenomination(currency_id=usd.id, name="Dollar", value_in_base_units=1.0),
                CurrencyDenomination(currency_id=usd.id, name="Cent", value_in_base_units=0.01),
            ]
        )
        changed = True
    else:
        if usd.peg_type != PegType.CURRENCY or usd.peg_target != "USD" or usd.base_unit_value != 1.0:
            usd.peg_type = PegType.CURRENCY
            usd.peg_target = "USD"
            usd.base_unit_value = 1.0
            changed = True
        if not usd.denominations:
            db.add_all(
                [
                    CurrencyDenomination(currency_id=usd.id, name="Dollar", value_in_base_units=1.0),
                    CurrencyDenomination(currency_id=usd.id, name="Cent", value_in_base_units=0.01),
                ]
            )
            changed = True

    gold = db.query(Currency).filter(Currency.name == "Gold").first()
    if gold is not None:
        db.delete(gold)
        changed = True

    if changed:
        db.commit()

@router.post("/", response_model=CurrencyRead)
def create_currency(
    payload: CurrencyCreate,
    upsert: bool = Query(False, description="If true, update existing currency (and replace denominations)."),
    db: Session = Depends(get_db),
):
    """Create a currency.

    Upsert semantics when `upsert=true`:
    - Updates peg_type, peg_target, and base_unit_value.
    - Replaces existing denominations with those provided (full replacement, not merge).
    """
    existing = db.query(Currency).filter(Currency.name == payload.name).first()
    if existing:
        if not upsert:
            raise HTTPException(status_code=400, detail="Currency already exists")
        # Update values
        existing.peg_type = _coerce_peg_type(payload.peg_type)
        existing.peg_target = payload.peg_target
        existing.base_unit_value = payload.base_unit_value
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
        currency = Currency(
            name=payload.name,
            peg_type=_coerce_peg_type(payload.peg_type),
            peg_target=payload.peg_target,
            base_unit_value=payload.base_unit_value,
        )
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
        peg_type=target.peg_type.value,
        peg_target=target.peg_target,
        base_unit_value=target.base_unit_value,
        denominations=[
            CurrencyDenominationRead(id=den.id, name=den.name, value_in_base_units=den.value_in_base_units)
            for den in target.denominations
        ],
    )

@router.get("/", response_model=list[CurrencyRead])
def list_currencies(db: Session = Depends(get_db)):
    _ensure_base_currencies(db)
    currencies = db.query(Currency).all()
    return [
        CurrencyRead(
            id=c.id,
            name=c.name,
            peg_type=c.peg_type.value,
            peg_target=c.peg_target,
            base_unit_value=c.base_unit_value,
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

    - peg_type: if provided, update the pegging type (CURRENCY, METAL, MATERIAL)
    - peg_target: if provided, update the target (currency/metal/material name)
    - base_unit_value: if provided, update the value in terms of peg_target
    - denominations_add_or_update: list of denomination objects:
        * if id provided -> update existing fields (name/value) if not None
        * if id missing -> create new denomination
    - denomination_ids_remove: list of denomination IDs to delete
    """
    currency = db.query(Currency).filter(Currency.id == currency_id).first()
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")

    data = payload.model_dump(exclude_unset=True)
    if "peg_type" in data and data["peg_type"] is not None:
        currency.peg_type = _coerce_peg_type(data["peg_type"])
    if "peg_target" in data and data["peg_target"] is not None:
        currency.peg_target = data["peg_target"]
    base_unit = data.get("base_unit_value")
    if base_unit is None and data.get("base_unit_value_oz_gold") is not None:
        base_unit = data["base_unit_value_oz_gold"]
    if base_unit is not None:
        currency.base_unit_value = base_unit

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
        peg_type=currency.peg_type.value,
        peg_target=currency.peg_target,
        base_unit_value=currency.base_unit_value,
        denominations=[
            CurrencyDenominationRead(id=den.id, name=den.name, value_in_base_units=den.value_in_base_units)
            for den in currency.denominations
        ],
    )


@router.delete("/{currency_id}", status_code=204)
def delete_currency(currency_id: int, db: Session = Depends(get_db)):
    currency = db.query(Currency).filter(Currency.id == currency_id).first()
    if currency is None:
        raise HTTPException(status_code=404, detail="Currency not found")
    if currency.name == "USD":
        raise HTTPException(status_code=400, detail="Cannot delete the USD base currency")

    db.delete(currency)
    db.commit()
    return Response(status_code=204)


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
