from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class CurrencyDenominationBase(BaseModel):
    name: str
    value_in_base_units: float

class CurrencyDenominationCreate(CurrencyDenominationBase):
    pass

class CurrencyDenominationRead(CurrencyDenominationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CurrencyDenominationUpdate(BaseModel):
    id: int | None = None  # If provided, update existing; if missing, create new
    name: str | None = None
    value_in_base_units: float | None = None


class CurrencyBase(BaseModel):
    name: str
    base_unit_value_oz_gold: float = 0.0

class CurrencyCreate(CurrencyBase):
    denominations: list[CurrencyDenominationCreate] = []

class CurrencyRead(CurrencyBase):
    id: int
    denominations: list[CurrencyDenominationRead] = []
    model_config = ConfigDict(from_attributes=True)


class CurrencyUpdate(BaseModel):
    base_unit_value_oz_gold: float | None = None
    denominations_add_or_update: list[CurrencyDenominationUpdate] = []
    denomination_ids_remove: list[int] = []

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
    model_config = ConfigDict(from_attributes=True)


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
    model_config = ConfigDict(from_attributes=True)


class GemstoneCreate(BaseModel):
    name: str
    value_per_carat_oz_gold: float = 0.0


class GemstoneRead(BaseModel):
    id: int
    name: str
    value_per_carat_oz_gold: float
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PlayerGemstoneCreate(BaseModel):
    gemstone_id: int
    carats: float


class PlayerGemstoneRead(BaseModel):
    id: int
    player_id: int
    gemstone_id: int
    carats: float
    appraised_value_oz_gold: float
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ArtItemCreate(BaseModel):
    name: str
    description: str = ""
    player_id: int | None = None


class ArtItemRead(BaseModel):
    id: int
    name: str
    description: str
    player_id: int | None
    appraised_value_oz_gold: float
    pending_appraisal: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ArtItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    player_id: int | None = None
    appraised_value_oz_gold: float | None = None
    pending_appraisal: bool | None = None


class RealEstateCreate(BaseModel):
    name: str
    location: str = ""
    description: str = ""
    player_id: int | None = None


class RealEstateRead(BaseModel):
    id: int
    name: str
    location: str
    description: str
    player_id: int | None
    appraised_value_oz_gold: float
    income_per_session_oz_gold: float
    pending_appraisal: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RealEstateUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    description: str | None = None
    player_id: int | None = None
    appraised_value_oz_gold: float | None = None
    income_per_session_oz_gold: float | None = None
    pending_appraisal: bool | None = None


class BusinessCreate(BaseModel):
    name: str
    description: str = ""
    principle_activity: str = ""
    net_worth_oz_gold: float = 0.0
    income_per_session_oz_gold: float = 0.0


class BusinessRead(BaseModel):
    id: int
    name: str
    description: str
    principle_activity: str
    net_worth_oz_gold: float
    income_per_session_oz_gold: float
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BusinessUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    principle_activity: str | None = None
    net_worth_oz_gold: float | None = None
    income_per_session_oz_gold: float | None = None


class BusinessInvestorUpsert(BaseModel):
    player_id: int
    equity_percent: float | None = None
    invested_oz_gold: float | None = None


class BusinessInvestorRead(BaseModel):
    id: int
    business_id: int
    player_id: int
    equity_percent: float
    invested_oz_gold: float
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BusinessWithInvestorsRead(BusinessRead):
    investors: list[BusinessInvestorRead] = []


class BusinessPetitionCreate(BaseModel):
    player_id: int
    name: str
    description: str = ""
    principle_activity: str = ""
    initial_investment_oz_gold: float = 0.0
