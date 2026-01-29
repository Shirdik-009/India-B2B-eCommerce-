"""Order schemas."""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)
    unit_price: Decimal | None = Field(None, ge=0)  # If omitted/0, use product price


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(..., min_length=1)
    shipping_address: str = Field(..., min_length=1, max_length=1000)
    notes: str | None = None


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_title: str | None = None
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    buyer_id: int
    status: str
    total_amount: Decimal
    shipping_address: str
    notes: str | None
    created_at: datetime
    items: list[OrderItemResponse] = []
    display_number: int | None = None  # Per-buyer order number (e.g. "Order #1")

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    orders: list[OrderResponse]


class SellerOrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_title: str | None
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class SellerOrderResponse(BaseModel):
    id: int
    buyer_id: int
    buyer_name: str | None
    status: str
    created_at: datetime
    shipping_address: str
    items: list[SellerOrderItemResponse]
    seller_subtotal: Decimal
