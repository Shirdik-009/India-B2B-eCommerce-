"""Products CRUD, listing, and search."""
import re
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_db, get_current_user, get_current_user_seller, get_current_user_optional
from app.models.user import User, UserRole
from app.models.product import Product, ProductImage
from app.models.category import Category
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductList,
    ProductImageSchema,
)

router = APIRouter(prefix="/products", tags=["products"])


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-") or "product"


@router.get("", response_model=ProductList)
async def list_products(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: int | None = None,
    q: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    my: bool = Query(False, description="If true and authenticated as seller, return only current user's products"),
    user: User | None = Depends(get_current_user_optional),
) -> ProductList:
    offset = (page - 1) * page_size
    query = select(Product).where(Product.is_active)
    count_query = select(func.count(Product.id)).where(Product.is_active)

    if my and user and user.role in (UserRole.SELLER, UserRole.ADMIN):
        query = query.where(Product.seller_id == user.id)
        count_query = count_query.where(Product.seller_id == user.id)
    if category_id is not None:
        query = query.where(Product.category_id == category_id)
        count_query = count_query.where(Product.category_id == category_id)
    if q:
        term = f"%{q.strip()}%"
        query = query.where(or_(Product.title.ilike(term), Product.description.ilike(term)))
        count_query = count_query.where(or_(Product.title.ilike(term), Product.description.ilike(term)))
    if min_price is not None:
        query = query.where(Product.price >= min_price)
        count_query = count_query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
        count_query = count_query.where(Product.price <= max_price)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.options(selectinload(Product.images), selectinload(Product.seller), selectinload(Product.category))
    query = query.order_by(Product.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    products = result.scalars().all()

    items = []
    for p in products:
        items.append(
            ProductResponse(
                id=p.id,
                title=p.title,
                slug=p.slug,
                description=p.description,
                price=p.price,
                min_order_quantity=p.min_order_quantity,
                unit=p.unit,
                category_id=p.category_id,
                seller_id=p.seller_id,
                is_active=p.is_active,
                created_at=p.created_at,
                images=[ProductImageSchema.model_validate(i) for i in p.images],
                seller_name=p.seller.full_name if p.seller else None,
            )
        )
    return ProductList(total=total, page=page, page_size=page_size, items=items)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    result = await db.execute(
        select(Product)
        .where(Product.id == product_id, Product.is_active)
        .options(selectinload(Product.images), selectinload(Product.seller), selectinload(Product.category))
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return ProductResponse(
        id=product.id,
        title=product.title,
        slug=product.slug,
        description=product.description,
        price=product.price,
        min_order_quantity=product.min_order_quantity,
        unit=product.unit,
        category_id=product.category_id,
        seller_id=product.seller_id,
        is_active=product.is_active,
        created_at=product.created_at,
        images=[ProductImageSchema.model_validate(i) for i in product.images],
        seller_name=product.seller.full_name if product.seller else None,
    )


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_seller),
) -> ProductResponse:
    base_slug = slugify(data.title)
    slug = base_slug
    n = 0
    while True:
        result = await db.execute(select(Product).where(Product.slug == slug))
        if result.scalar_one_or_none() is None:
            break
        n += 1
        slug = f"{base_slug}-{n}"

    product = Product(
        title=data.title,
        slug=slug,
        description=data.description,
        price=data.price,
        min_order_quantity=data.min_order_quantity,
        unit=data.unit,
        category_id=data.category_id,
        seller_id=user.id,
    )
    db.add(product)
    await db.flush()
    for i, url in enumerate(data.image_urls or []):
        img = ProductImage(product_id=product.id, url=url, sort_order=i)
        db.add(img)
    await db.refresh(product)
    result = await db.execute(select(Product).where(Product.id == product.id).options(selectinload(Product.images), selectinload(Product.seller)))
    product = result.scalar_one()
    return ProductResponse(
        id=product.id,
        title=product.title,
        slug=product.slug,
        description=product.description,
        price=product.price,
        min_order_quantity=product.min_order_quantity,
        unit=product.unit,
        category_id=product.category_id,
        seller_id=product.seller_id,
        is_active=product.is_active,
        created_at=product.created_at,
        images=[ProductImageSchema.model_validate(i) for i in product.images],
        seller_name=product.seller.full_name if product.seller else None,
    )


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_seller),
) -> ProductResponse:
    result = await db.execute(
        select(Product).where(Product.id == product_id).options(selectinload(Product.images), selectinload(Product.seller))
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if product.seller_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your product")

    update_data = data.model_dump(exclude_unset=True)
    image_urls = update_data.pop("image_urls", None)
    for key, value in update_data.items():
        setattr(product, key, value)
    if image_urls is not None:
        await db.execute(ProductImage.__table__.delete().where(ProductImage.product_id == product.id))
        for i, url in enumerate(image_urls):
            db.add(ProductImage(product_id=product.id, url=url, sort_order=i))
    await db.flush()
    await db.refresh(product)
    result = await db.execute(select(Product).where(Product.id == product.id).options(selectinload(Product.images), selectinload(Product.seller)))
    product = result.scalar_one()
    return ProductResponse(
        id=product.id,
        title=product.title,
        slug=product.slug,
        description=product.description,
        price=product.price,
        min_order_quantity=product.min_order_quantity,
        unit=product.unit,
        category_id=product.category_id,
        seller_id=product.seller_id,
        is_active=product.is_active,
        created_at=product.created_at,
        images=[ProductImageSchema.model_validate(i) for i in product.images],
        seller_name=product.seller.full_name if product.seller else None,
    )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_seller),
) -> None:
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if product.seller_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your product")
    await db.delete(product)
    await db.flush()
