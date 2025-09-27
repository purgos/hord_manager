from sqlalchemy import Integer, String, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from ..core.database import Base

class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)  # For new accounts
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)  # GM approval status
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    approved_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)

