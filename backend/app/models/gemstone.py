from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from .player import Player  # noqa: F401


class Gemstone(Base):
    __tablename__ = "gemstones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    value_per_carat_oz_gold: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    holdings: Mapped[list["PlayerGemstone"]] = relationship("PlayerGemstone", back_populates="gemstone", cascade="all, delete-orphan")


class PlayerGemstone(Base):
    __tablename__ = "player_gemstones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id", ondelete="CASCADE"))
    gemstone_id: Mapped[int] = mapped_column(Integer, ForeignKey("gemstones.id", ondelete="CASCADE"))
    carats: Mapped[float] = mapped_column(Float, default=0.0)
    appraised_value_oz_gold: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    gemstone: Mapped[Gemstone] = relationship("Gemstone", back_populates="holdings")
    # player: Mapped[Player] = relationship("Player")  # optional backref later
