# expense_tracker/api/v1/endpoints/auth.py
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from expense_tracker.core.settings import settings
from expense_tracker.db.session import get_session
from expense_tracker.models.user import User
from expense_tracker.schemas.auth import (
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
    Token,
)
from expense_tracker.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> User:
    """Dependency to get current user from token"""
    auth_service = AuthService(session)
    return await auth_service.get_current_user(token)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    """Login endpoint"""
    auth_service = AuthService(session)
    user = await auth_service.authenticate_user(
        form_data.username,  # OAuth2 form uses username field for email
        form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Change password endpoint"""
    auth_service = AuthService(session)
    success = await auth_service.change_password(
        current_user,
        password_data.current_password,
        password_data.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password"
        )
    return {"message": "Password changed successfully"}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    password_data: PasswordReset,
    session: AsyncSession = Depends(get_session)
):
    """Initiate password reset process"""
    auth_service = AuthService(session)
    await auth_service.initiate_password_reset(password_data.email)
    # Always return success to prevent email enumeration
    return {
        "message": "If the email exists, you will receive a password reset link"
    }


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    reset_data: PasswordResetConfirm,
    session: AsyncSession = Depends(get_session)
):
    """Reset password using reset token"""
    auth_service = AuthService(session)
    success = await auth_service.reset_password(
        reset_data.token,
        reset_data.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    return {"message": "Password reset successfully"}


@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get a new access token"""
    auth_service = AuthService(session)
    access_token = auth_service.create_access_token(
        data={"sub": str(current_user.id)}
    )
    return {"access_token": access_token, "token_type": "bearer"}
