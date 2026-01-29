"""Conversation and Message models for buyer-seller chat."""
from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    buyer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    seller_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    buyer = relationship("User", foreign_keys=[buyer_id], lazy="selectin")
    seller = relationship("User", foreign_keys=[seller_id], lazy="selectin")
    product = relationship("Product", lazy="selectin")
    messages = relationship("Message", back_populates="conversation", lazy="selectin", order_by="Message.created_at", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("buyer_id", "seller_id", name="uq_conversation_buyer_seller"),)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages", lazy="selectin")
    sender = relationship("User", lazy="selectin")
