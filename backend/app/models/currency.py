from sqlalchemy import Integer, String, Float, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base
import enum

class PegType(enum.Enum):
    CURRENCY = "currency"
    METAL = "metal"
    MATERIAL = "material"

class Currency(Base):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    
    # Flexible pegging system
    peg_type: Mapped[PegType] = mapped_column(Enum(PegType), default=PegType.CURRENCY)
    peg_target: Mapped[str] = mapped_column(String, default="USD")  # name of currency/metal/material
    base_unit_value: Mapped[float] = mapped_column(Float, default=1.0)  # value in terms of peg_target
    
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    denominations: Mapped[list["CurrencyDenomination"]] = relationship("CurrencyDenomination", back_populates="currency", cascade="all, delete-orphan")

class CurrencyDenomination(Base):
    __tablename__ = "currency_denominations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    currency_id: Mapped[int] = mapped_column(ForeignKey("currencies.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String, index=True)
    value_in_base_units: Mapped[float] = mapped_column(Float)  # relative to 1 base currency unit

    currency: Mapped[Currency] = relationship("Currency", back_populates="denominations")
