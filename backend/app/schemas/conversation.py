"""Conversation and Message schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    sender_name: str | None = None
    body: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationCreate(BaseModel):
    seller_id: int
    product_id: int | None = None


class ConversationResponse(BaseModel):
    id: int
    buyer_id: int
    seller_id: int
    product_id: int | None
    created_at: datetime
    updated_at: datetime
    buyer_name: str | None = None
    seller_name: str | None = None
    product_title: str | None = None
    last_message: str | None = None
    last_message_at: datetime | None = None
    unread_count: int = 0
    other_party_online: bool = False  # True if the other user (buyer/seller) was seen in chat recently

    model_config = {"from_attributes": True}
