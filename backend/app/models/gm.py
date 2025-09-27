from enum import Enum
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from ..core.database import Base

if TYPE_CHECKING:
    from .player import Player


class InboxMessageType(str, Enum):
    APPRAISAL = "appraisal"
    BUSINESS = "business"
    INVESTMENT = "investment"
    LOAN = "loan"
    ACCOUNT_REGISTRATION = "account_registration"


class InboxMessageStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    RESOLVED = "resolved"


class GMSettings(Base):
    __tablename__ = "gm_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Economic controls
    exchange_fee_percent: Mapped[float] = mapped_column(default=0.0)
    interest_rate_percent: Mapped[float] = mapped_column(default=0.0)
    growth_factor_percent: Mapped[float] = mapped_column(default=0.0)
    # Feature flags / visibility
    hide_dollar_from_players: Mapped[bool] = mapped_column(Boolean, default=False)
    # Audit
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class InboxMessage(Base):
    __tablename__ = "inbox_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String, default=InboxMessageStatus.PENDING.value, index=True)
    payload: Mapped[dict] = mapped_column(JSON)  # Structured JSON payload
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    player_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("players.id", ondelete="SET NULL"), nullable=True)

    # Relationship to Player
    player: Mapped["Player"] = relationship("Player")
