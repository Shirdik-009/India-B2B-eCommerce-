"""User presence for chat online status."""
from datetime import datetime
from sqlalchemy import DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserPresence(Base):
    """One row per user: last time they were active in chat (heartbeat)."""
    __tablename__ = "user_presence"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    