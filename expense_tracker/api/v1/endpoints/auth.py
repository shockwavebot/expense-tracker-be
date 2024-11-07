# expense_tracker/api/v1/auth.py
from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from expense_tracker.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
)
from expense_tracker.db.session import get_session
from expense_tracker.schemas.token import LoginRequest, Token
from expense_tracker.schemas.user import User, UserCreate
from expense_tracker.services.user import user_service

router = APIRouter()


@router.post("/register", response_model=User)
async def register(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_session)]
) -> Any:
    """
    Register a new user.
    """
    user = await user_service.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists."
        )

    user = await user_service.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this username already exists."
        )

    user = await user_service.create(db, obj_in=user_in)
    return user


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_session)]
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await user_service.authenticate(
        db, email=login_data.email, password=login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user_service.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_session)]
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await user_service.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user_service.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
