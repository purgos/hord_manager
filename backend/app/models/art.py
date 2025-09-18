from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class ArtItem(Base):
    __tablename__ = "art_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("players.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String, default="")
    appraised_value_oz_gold: Mapped[float] = mapped_column(Float, default=0.0)
    pending_appraisal: Mapped[bool] = mapped_column(Integer, default=0)  # 0/1 bool
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RealEstateProperty(Base):
    __tablename__ = "real_estate_properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("players.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String, index=True)
    location: Mapped[str] = mapped_column(String, default="")
    description: Mapped[str] = mapped_column(String, default="")
    appraised_value_oz_gold: Mapped[float] = mapped_column(Float, default=0.0)
    income_per_session_oz_gold: Mapped[float] = mapped_column(Float, default=0.0)
    pending_appraisal: Mapped[bool] = mapped_column(Integer, default=0)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
