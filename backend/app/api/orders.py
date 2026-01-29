"""Orders: create and list."""
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_db, get_current_user, get_current_user_seller
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderItemResponse,
    OrderListResponse,
    SellerOrderResponse,
    SellerOrderItemResponse,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=OrderListResponse)
async def list_orders(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> OrderListResponse:
    offset = (page - 1) * page_size
    count_result = await db.execute(select(func.count(Order.id)).where(Order.buyer_id == user.id))
    total = count_result.scalar() or 0
    result = await db.execute(
        select(Order)
        .where(Order.buyer_id == user.id)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    orders = result.scalars().all()
    out = []
    for idx, o in enumerate(orders):
        display_number = total - offset - idx
        items = [
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_title=item.product.title if item.product else None,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            for item in o.items
        ]
        out.append(
            OrderResponse(
                id=o.id,
                buyer_id=o.buyer_id,
                status=o.status.value,
                total_amount=o.total_amount,
                shipping_address=o.shipping_address,
                notes=o.notes,
                created_at=o.created_at,
                items=items,
                display_number=display_number,
            )
        )
    return OrderListResponse(total=total, page=page, page_size=page_size, orders=out)


@router.get("/seller", response_model=list[SellerOrderResponse])
async def list_seller_orders(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_seller),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> list[SellerOrderResponse]:
    """Orders received by this seller (orders that contain this seller's products)."""
    subq = (
        select(OrderItem.order_id)
        .join(Product, OrderItem.product_id == Product.id)
        .where(Product.seller_id == user.id)
        .distinct()
    )
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Order)
        .where(Order.id.in_(subq))
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.buyer),
        )
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    orders = result.scalars().all()
    out = []
    for o in orders:
        seller_items = [item for item in o.items if item.product and item.product.seller_id == user.id]
        if not seller_items:
            continue
        seller_subtotal = sum(item.subtotal for item in seller_items)
        out.append(
            SellerOrderResponse(
                id=o.id,
                buyer_id=o.buyer_id,
                buyer_name=o.buyer.full_name if o.buyer else None,
                status=o.status.value,
                created_at=o.created_at,
                shipping_address=o.shipping_address,
                items=[
                    SellerOrderItemResponse(
                        id=item.id,
                        product_id=item.product_id,
                        product_title=item.product.title if item.product else None,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        subtotal=item.subtotal,
                    )
                    for item in seller_items
                ],
                seller_subtotal=seller_subtotal,
            )
        )
    return out


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> OrderResponse:
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id, Order.buyer_id == user.id)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    total_count = await db.execute(select(func.count(Order.id)).where(Order.buyer_id == user.id))
    total = total_count.scalar() or 0
    count_after = await db.execute(
        select(func.count(Order.id)).where(
            Order.buyer_id == user.id,
            or_(
                Order.created_at > order.created_at,
                and_(Order.created_at == order.created_at, Order.id > order.id),
            ),
        )
    )
    position = count_after.scalar() or 0
    display_number = total - position
    items = [
        OrderItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_title=item.product.title if item.product else None,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.subtotal,
        )
        for item in order.items
    ]
    return OrderResponse(
        id=order.id,
        buyer_id=order.buyer_id,
        status=order.status.value,
        total_amount=order.total_amount,
        shipping_address=order.shipping_address,
        notes=order.notes,
        created_at=order.created_at,
        items=items,
        display_number=display_number,
    )


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> OrderResponse:
    total = Decimal("0")
    order_items_data = []
    for it in data.items:
        result = await db.execute(select(Product).where(Product.id == it.product_id, Product.is_active))
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {it.product_id} not found or inactive",
            )
        if product.seller_id == user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot order your own products",
            )
        if it.quantity < product.min_order_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Minimum order quantity for {product.title} is {product.min_order_quantity}",
            )
        unit_price = (it.unit_price if it.unit_price and it.unit_price > 0 else product.price)
        subtotal = unit_price * it.quantity
        total += subtotal
        order_items_data.append((product, it.quantity, unit_price, subtotal))

    order = Order(
        buyer_id=user.id,
        total_amount=total,
        shipping_address=data.shipping_address,
        notes=data.notes,
    )
    db.add(order)
    await db.flush()
    for product, qty, unit_price, subtotal in order_items_data:
        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=qty,
            unit_price=unit_price,
            subtotal=subtotal,
        )
        db.add(item)
    await db.refresh(order)
    result = await db.execute(
        select(Order)
        .where(Order.id == order.id)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
    )
    order = result.scalar_one()
    items = [
        OrderItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_title=item.product.title if item.product else None,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.subtotal,
        )
        for item in order.items
    ]
    total_count = await db.execute(select(func.count(Order.id)).where(Order.buyer_id == user.id))
    total = total_count.scalar() or 0
    count_after = await db.execute(
        select(func.count(Order.id)).where(
            Order.buyer_id == user.id,
            or_(
                Order.created_at > order.created_at,
                and_(Order.created_at == order.created_at, Order.id > order.id),
            ),
        )
    )
    position = count_after.scalar() or 0
    display_number = total - position
    return OrderResponse(
        id=order.id,
        buyer_id=order.buyer_id,
        status=order.status.value,
        total_amount=order.total_amount,
        shipping_address=order.shipping_address,
        notes=order.notes,
        created_at=order.created_at,
        items=items,
        display_number=display_number,
    )
