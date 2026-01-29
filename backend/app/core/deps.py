"""FastAPI dependencies: auth, db, pagination."""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.security import decode_access_token
from app.database import get_db, AsyncSessionLocal
from app.models.user import User

security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User | None:
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        return None
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == int(payload["sub"])))
    user = result.scalar_one_or_none()
    if user and not user.is_active:
        return None
    return user


async def get_current_user(
    user: Annotated[User | None, Depends(get_current_user_optional)],
) -> User:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_user_seller(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    from app.models.user import UserRole
    if user.role not in (UserRole.SELLER, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seller access required",
        )
    return user


def pagination_params(
    page: int = 1,
    page_size: int = 20,
) -> tuple[int, int]:
    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    return page, page_size
