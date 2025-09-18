from pydantic import BaseModel
from typing import Optional, List

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
