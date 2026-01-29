"""Current user profile."""
from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        company_name=user.company_name,
        is_verified=user.is_verified,
        role=user.role.value,
    )
