"""Authentication: register, login."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> Token:
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    role = UserRole.BUYER if data.role == "buyer" else UserRole.SELLER
    user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        phone=data.phone,
        company_name=data.company_name,
        role=role,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    token = create_access_token(str(user.id), extra={"email": user.email, "role": user.role.value})
    return Token(
        access_token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            company_name=user.company_name,
            is_verified=user.is_verified,
            role=user.role.value,
        ),
    )


@router.post("/login", response_model=Token)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )
    token = create_access_token(str(user.id), extra={"email": user.email, "role": user.role.value})
    return Token(
        access_token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            company_name=user.company_name,
            is_verified=user.is_verified,
            role=user.role.value,
        ),
    )
