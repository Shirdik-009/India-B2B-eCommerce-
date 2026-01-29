"""Category schemas."""
from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    parent_id: int | None = None
    sort_order: int = 0


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    parent_id: int | None
    sort_order: int

    model_config = {"from_attributes": True}
