# expense_tracker/api/v1/endpoints/users.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from expense_tracker.core.exceptions import DuplicateEmailError, UserNotFoundError
from expense_tracker.db.session import get_session
from expense_tracker.schemas.user import UserCreate, UserResponse, UserUpdate
from expense_tracker.services.user import UserService

router = APIRouter()


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new user"
)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_session)
) -> UserResponse:
    """
    Create a new user with the following information:
    - email: unique email address
    - name: user's full name
    """
    user_service = UserService(db)
    try:
        user = await user_service.create_user(user_data)
        return user
    except DuplicateEmailError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    description="Get user by ID"
)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_session)
) -> UserResponse:
    """
    Retrieve a user by their ID
    """
    user_service = UserService(db)
    try:
        user = await user_service.get_user_by_id(user_id)
        return user
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    description="Update user information"
)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_session)
) -> UserResponse:
    """
    Update user information. The following fields can be updated:
    - email: new email address (must be unique)
    - username: new full name
    """
    user_service = UserService(db)
    try:
        user = await user_service.update_user(user_id, user_data)
        return user
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DuplicateEmailError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete a user"
)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_session)
) -> None:
    """
    Delete a user and all their associated data
    """
    user_service = UserService(db)
    try:
        await user_service.delete_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "",
    response_model=List[UserResponse],
    description="List all users"
)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
) -> List[UserResponse]:
    """
    Retrieve a list of users with pagination
    """
    user_service = UserService(db)
    users = await user_service.list_users(skip=skip, limit=limit)
    return users
