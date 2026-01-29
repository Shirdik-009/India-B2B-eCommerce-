"""Product schemas."""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class ProductImageSchema(BaseModel):
    id: int
    url: str
    alt: str | None
    sort_order: int

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    price: Decimal = Field(..., ge=0)
    min_order_quantity: int = Field(default=1, ge=1)
    unit: str = Field(default="piece", max_length=50)
    category_id: int | None = None
    image_urls: list[str] = Field(default_factory=list, max_length=10)


class ProductUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    price: Decimal | None = Field(None, ge=0)
    min_order_quantity: int | None = Field(None, ge=1)
    unit: str | None = Field(None, max_length=50)
    category_id: int | None = None
    is_active: bool | None = None
    image_urls: list[str] | None = Field(None, max_length=10)


class ProductResponse(BaseModel):
    id: int
    title: str
    slug: str
    description: str | None
    price: Decimal
    min_order_quantity: int
    unit: str
    category_id: int | None
    seller_id: int
    is_active: bool
    created_at: datetime
    images: list[ProductImageSchema] = []
    seller_name: str | None = None

    model_config = {"from_attributes": True}


class ProductList(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ProductResponse]
