"""Categories CRUD and listing."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user_seller
from app.models.user import User
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)) -> list[CategoryResponse]:
    result = await db.execute(
        select(Category).order_by(Category.sort_order, Category.name)
    )
    categories = result.scalars().all()
    return [CategoryResponse.model_validate(c) for c in categories]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return CategoryResponse.model_validate(category)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_seller),
) -> CategoryResponse:
    result = await db.execute(select(Category).where(Category.slug == data.slug))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug already exists",
        )
    category = Category(
        name=data.name,
        slug=data.slug,
        description=data.description,
        parent_id=data.parent_id,
        sort_order=data.sort_order,
    )
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return CategoryResponse.model_validate(category)
