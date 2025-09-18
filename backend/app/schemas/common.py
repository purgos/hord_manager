from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CurrencyDenominationBase(BaseModel):
    name: str
    value_in_base_units: float

class CurrencyDenominationCreate(CurrencyDenominationBase):
    pass

class CurrencyDenominationRead(CurrencyDenominationBase):
    id: int
    class Config:
        from_attributes = True

class CurrencyBase(BaseModel):
    name: str
    base_unit_value_oz_gold: float = 0.0

class CurrencyCreate(CurrencyBase):
    denominations: list[CurrencyDenominationCreate] = []

class CurrencyRead(CurrencyBase):
    id: int
    denominations: list[CurrencyDenominationRead] = []
    class Config:
        from_attributes = True

class SessionStateRead(BaseModel):
    current_session: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GMSettingsRead(BaseModel):
    id: int
    exchange_fee_percent: float
    interest_rate_percent: float
    growth_factor_percent: float
    hide_dollar_from_players: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GMSettingsUpdate(BaseModel):
    exchange_fee_percent: float | None = None
    interest_rate_percent: float | None = None
    growth_factor_percent: float | None = None
    hide_dollar_from_players: bool | None = None


class InboxMessageRead(BaseModel):
    id: int
    type: str
    status: str
    payload: dict
    created_at: datetime
    updated_at: datetime
    player_id: int | None

    class Config:
        from_attributes = True
