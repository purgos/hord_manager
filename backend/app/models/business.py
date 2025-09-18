from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from .player import Player  # noqa: F401

class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String, default="")
    principle_activity: Mapped[str] = mapped_column(String, default="")
    net_worth_oz_gold: Mapped[float] = mapped_column(Float, default=0.0)
    income_per_session_oz_gold: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    investors: Mapped[list["BusinessInvestor"]] = relationship(
        "BusinessInvestor", back_populates="business", cascade="all, delete-orphan"
    )

class BusinessInvestor(Base):
    __tablename__ = "business_investors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"))
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id", ondelete="CASCADE"))
    equity_percent: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100 sum constraint enforced in logic
    invested_oz_gold: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    business: Mapped[Business] = relationship("Business", back_populates="investors")
