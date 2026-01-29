"""Buyer–seller chat: conversations and messages."""
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.conversation import Conversation, Message
from app.models.presence import UserPresence
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)

router = APIRouter(prefix="/chat", tags=["chat"])

ONLINE_WINDOW = timedelta(minutes=5)


async def _get_online_user_ids(db: AsyncSession, user_ids: list[int]) -> set[int]:
    """Return set of user_ids that have been seen in chat within ONLINE_WINDOW."""
    if not user_ids:
        return set()
    cutoff = datetime.now(timezone.utc) - ONLINE_WINDOW
    r = await db.execute(
        select(UserPresence.user_id).where(
            UserPresence.user_id.in_(user_ids),
            UserPresence.last_seen_at >= cutoff,
        )
    )
    return set(r.scalars().all())


def _conversation_response(
    c,
    last_body=None,
    last_at=None,
    unread=0,
    other_party_online=False,
) -> ConversationResponse:
    """Build ConversationResponse from conversation and optional last message / unread / online."""
    return ConversationResponse(
        id=c.id,
        buyer_id=c.buyer_id,
        seller_id=c.seller_id,
        product_id=c.product_id,
        created_at=c.created_at,
        updated_at=c.updated_at,
        buyer_name=c.buyer.full_name if c.buyer else None,
        seller_name=c.seller.full_name if c.seller else None,
        product_title=c.product.title if c.product else None,
        last_message=last_body[:100] if last_body else None,
        last_message_at=last_at,
        unread_count=unread,
        other_party_online=other_party_online,
    )


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ConversationResponse]:
    """List my conversations (where I'm buyer or seller). Fetches last message and unread per conversation without loading all messages."""
    result = await db.execute(
        select(Conversation)
        .where((Conversation.buyer_id == user.id) | (Conversation.seller_id == user.id))
        .options(
            selectinload(Conversation.buyer),
            selectinload(Conversation.seller),
            selectinload(Conversation.product),
        )
        .order_by(Conversation.updated_at.desc())
    )
    convos = result.scalars().all()
    if not convos:
        return []
    ids = [c.id for c in convos]
    # Latest message per conversation (one row per conversation via max id)
    subq = (
        select(Message.conversation_id, func.max(Message.id).label("max_id"))
        .where(Message.conversation_id.in_(ids))
        .group_by(Message.conversation_id)
    ).alias("last_per_conv")
    last_q = (
        select(Message.conversation_id, Message.body, Message.created_at)
        .where(Message.conversation_id.in_(ids))
        .join(subq, Message.id == subq.c.max_id)
    )
    last_result = await db.execute(last_q)
    last_rows = {row[0]: (row[1], row[2]) for row in last_result.all()}
    # Unread count per conversation (single query)
    unread_result = await db.execute(
        select(Message.conversation_id, func.count(Message.id))
        .where(
            Message.conversation_id.in_(ids),
            Message.is_read.is_(False),
            Message.sender_id != user.id,
        )
        .group_by(Message.conversation_id)
    )
    unread_map = {row[0]: row[1] for row in unread_result.all()}
    other_user_ids = list({c.seller_id if user.id == c.buyer_id else c.buyer_id for c in convos})
    online_ids = await _get_online_user_ids(db, other_user_ids)
    return [
        _conversation_response(
            c,
            last_body=last_rows.get(c.id, (None, None))[0],
            last_at=last_rows.get(c.id, (None, None))[1],
            unread=unread_map.get(c.id, 0),
            other_party_online=(c.seller_id if user.id == c.buyer_id else c.buyer_id) in online_ids,
        )
        for c in convos
    ]


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_or_get_conversation(
    data: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ConversationResponse:
    """Create a conversation with a seller (or return existing). Buyer initiates."""
    if data.seller_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot start a conversation with yourself",
        )
    result = await db.execute(select(User).where(User.id == data.seller_id))
    seller = result.scalar_one_or_none()
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")
    if seller.role not in (UserRole.SELLER, UserRole.ADMIN):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not a seller")
    if data.product_id:
        prod = await db.execute(select(Product).where(Product.id == data.product_id, Product.seller_id == data.seller_id))
        if not prod.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product not found or not owned by seller")

    buyer_id = user.id
    seller_id = data.seller_id
    result = await db.execute(
        select(Conversation)
        .where(Conversation.buyer_id == buyer_id, Conversation.seller_id == seller_id)
        .options(
            selectinload(Conversation.buyer),
            selectinload(Conversation.seller),
            selectinload(Conversation.product),
            selectinload(Conversation.messages),
        )
    )
    conv = result.scalar_one_or_none()
    if conv:
        if data.product_id and not conv.product_id:
            conv.product_id = data.product_id
            await db.flush()
        last_msg = conv.messages[-1] if conv.messages else None
        unread = sum(1 for m in conv.messages if not m.is_read and m.sender_id != user.id)
        other_id = conv.seller_id if user.id == conv.buyer_id else conv.buyer_id
        online_ids = await _get_online_user_ids(db, [other_id])
        return _conversation_response(
            conv,
            last_body=last_msg.body if last_msg else None,
            last_at=last_msg.created_at if last_msg else None,
            unread=unread,
            other_party_online=other_id in online_ids,
        )
    conv = Conversation(buyer_id=buyer_id, seller_id=seller_id, product_id=data.product_id)
    db.add(conv)
    await db.flush()
    await db.refresh(conv)
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conv.id)
        .options(
            selectinload(Conversation.buyer),
            selectinload(Conversation.seller),
            selectinload(Conversation.product),
        )
    )
    conv = result.scalar_one()
    online_ids = await _get_online_user_ids(db, [seller_id])
    return _conversation_response(
        conv, last_body=None, last_at=None, unread=0, other_party_online=seller_id in online_ids
    )


@router.put("/presence")
async def update_presence(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Update current user's last_seen_at (call periodically from chat UI to show as online)."""
    now = datetime.now(timezone.utc)
    r = await db.execute(select(UserPresence).where(UserPresence.user_id == user.id))
    row = r.scalar_one_or_none()
    if row:
        row.last_seen_at = now
    else:
        db.add(UserPresence(user_id=user.id, last_seen_at=now))
    await db.flush()
    return {"ok": True}


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ConversationResponse:
    """Get one conversation (e.g. for thread header with online status)."""
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            ((Conversation.buyer_id == user.id) | (Conversation.seller_id == user.id)),
        )
        .options(
            selectinload(Conversation.buyer),
            selectinload(Conversation.seller),
            selectinload(Conversation.product),
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    other_id = conv.seller_id if user.id == conv.buyer_id else conv.buyer_id
    online_ids = await _get_online_user_ids(db, [other_id])
    return _conversation_response(
        conv,
        last_body=None,
        last_at=None,
        unread=0,
        other_party_online=other_id in online_ids,
    )


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = Query(100, ge=1, le=200),
    before_id: int | None = Query(None, description="Get messages before this id (pagination)"),
) -> list[MessageResponse]:
    """List messages in a conversation. Mark messages from the other user as read."""
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            ((Conversation.buyer_id == user.id) | (Conversation.seller_id == user.id)),
        )
        .options(selectinload(Conversation.messages).selectinload(Message.sender))
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    q = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .options(selectinload(Message.sender))
    )
    if before_id:
        q = q.where(Message.id < before_id)
    q = q.order_by(Message.created_at.desc()).limit(limit)
    result = await db.execute(q)
    messages = list(reversed(result.scalars().all()))
    for m in conv.messages:
        if m.sender_id != user.id and not m.is_read:
            m.is_read = True
    await db.flush()
    return [
        MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            sender_id=m.sender_id,
            sender_name=m.sender.full_name if m.sender else None,
            body=m.body,
            is_read=m.is_read,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: int,
    data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    """Send a message in a conversation."""
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            ((Conversation.buyer_id == user.id) | (Conversation.seller_id == user.id)),
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    msg = Message(conversation_id=conversation_id, sender_id=user.id, body=data.body.strip())
    db.add(msg)
    await db.flush()
    conv.updated_at = msg.created_at
    await db.refresh(msg)
    result = await db.execute(select(Message).where(Message.id == msg.id).options(selectinload(Message.sender)))
    msg = result.scalar_one()
    return MessageResponse(
        id=msg.id,
        conversation_id=msg.conversation_id,
        sender_id=msg.sender_id,
        sender_name=msg.sender.full_name if msg.sender else None,
        body=msg.body,
        is_read=msg.is_read,
        created_at=msg.created_at,
    )
