"""Shopping cart."""
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.cart import CartItem
from app.schemas.cart import CartItemCreate, CartItemResponse

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=list[CartItemResponse])
async def get_cart(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[CartItemResponse]:
    result = await db.execute(
        select(CartItem)
        .where(CartItem.user_id == user.id)
        .options(selectinload(CartItem.product))
    )
    items = result.scalars().all()
    return [
        CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            quantity=item.quantity,
            product_title=item.product.title if item.product else None,
            product_price=item.product.price if item.product else None,
            subtotal=(item.product.price * item.quantity) if item.product else None,
        )
        for item in items
    ]


@router.post("", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    data: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CartItemResponse:
    result = await db.execute(select(Product).where(Product.id == data.product_id, Product.is_active))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if product.seller_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot add your own products to cart",
        )
    if data.quantity < product.min_order_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum order quantity is {product.min_order_quantity}",
        )
    result = await db.execute(
        select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == data.product_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.quantity += data.quantity
        await db.flush()
        await db.refresh(existing)
        item = existing
    else:
        item = CartItem(user_id=user.id, product_id=data.product_id, quantity=data.quantity)
        db.add(item)
        await db.flush()
        await db.refresh(item)
    result = await db.execute(select(CartItem).where(CartItem.id == item.id).options(selectinload(CartItem.product)))
    item = result.scalar_one()
    return CartItemResponse(
        id=item.id,
        product_id=item.product_id,
        quantity=item.quantity,
        product_title=item.product.title if item.product else None,
        product_price=item.product.price if item.product else None,
        subtotal=(item.product.price * item.quantity) if item.product else None,
    )


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)


@router.patch("/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: int,
    data: CartItemUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CartItemResponse:
    quantity = data.quantity
    if quantity < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be at least 1")
    result = await db.execute(
        select(CartItem).where(CartItem.id == item_id, CartItem.user_id == user.id).options(selectinload(CartItem.product))
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    if quantity < item.product.min_order_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum order quantity is {item.product.min_order_quantity}",
        )
    item.quantity = quantity
    await db.flush()
    await db.refresh(item)
    return CartItemResponse(
        id=item.id,
        product_id=item.product_id,
        quantity=item.quantity,
        product_title=item.product.title if item.product else None,
        product_price=item.product.price if item.product else None,
        subtotal=(item.product.price * item.quantity) if item.product else None,
    )


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    result = await db.execute(select(CartItem).where(CartItem.id == item_id, CartItem.user_id == user.id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    await db.delete(item)
    await db.flush()
