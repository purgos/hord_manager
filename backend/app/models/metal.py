from sqlalchemy import Integer, String, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from ..core.database import Base

class MetalPriceHistory(Base):
    __tablename__ = "metal_price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    metal_name: Mapped[str] = mapped_column(String, index=True)
    unit: Mapped[str] = mapped_column(String)  # lb or oz
    price_per_unit_usd: Mapped[float] = mapped_column(Float)
    price_per_oz_gold: Mapped[float] = mapped_column(Float)
    session_number: Mapped[int] = mapped_column(Integer, index=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
