"""Cart schemas."""
from decimal import Decimal
from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product_title: str | None = None
    product_price: Decimal | None = None
    subtotal: Decimal | None = None

    model_config = {"from_attributes": True}
