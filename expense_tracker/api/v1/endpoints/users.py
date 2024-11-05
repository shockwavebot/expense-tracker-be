# expense_tracker/api/v1/endpoints/users.py
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from expense_tracker.core.security import get_current_user, get_password_hash
from expense_tracker.db.base import get_session
from expense_tracker.models.user import User
from expense_tracker.schemas.user import User as UserSchema
from expense_tracker.schemas.user import UserCreate, UserUpdate

router = APIRouter()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_session)]
):
    """
    Create new user.
    """
    # Check if user with this email exists
    if await get_user_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists."
        )

    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/me", response_model=UserSchema)
async def read_user_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_user_me(
    user_in: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_session)]
):
    """
    Update current user.
    """
    if user_in.email and user_in.email != current_user.email:
        if await get_user_by_email(db, email=user_in.email):
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

    for field, value in user_in.model_dump(exclude_unset=True).items():
        if field == "password":
            setattr(current_user, "hashed_password", get_password_hash(value))
        else:
            setattr(current_user, field, value)

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user
