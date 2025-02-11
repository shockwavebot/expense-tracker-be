# expense_tracker/services/auth.py
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from expense_tracker.core.exceptions import InvalidCredentialsError, UserNotFoundError
from expense_tracker.core.settings import Settings as settings
from expense_tracker.models.user import User
from expense_tracker.schemas.auth import TokenData

from .user import UserService

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_service = UserService(session)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    async def authenticate_user(self, email: str, password: str) -> Tuple[User, str]:
        """Authenticate user and return user object with access token"""
        user = await self.user_service.get_user_by_email(email)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        if not self.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")

        if not user.is_active:
            raise InvalidCredentialsError("User account is not active")

        # Create access token
        access_token = self.create_access_token(
            data={"sub": str(user.id)}
        )

        return user, access_token

    async def get_current_user(self, token: str) -> User:
        """Get current user from JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise InvalidCredentialsError("Invalid token")
            token_data = TokenData(user_id=user_id)
        except JWTError:
            raise InvalidCredentialsError("Invalid token")

        user = await self.user_service.get_user_by_id(token_data.user_id)
        if user is None:
            raise UserNotFoundError("User not found")

        if not user.is_active:
            raise InvalidCredentialsError("User account is not active")

        return user

    async def create_verification_token(self, user: User) -> str:
        """Create email verification token"""
        token = str(uuid4())
        user.verification_token = token
        await self.session.commit()
        return token

    async def verify_email(self, token: str) -> User:
        """Verify user's email"""
        query = await self.session.execute(
            select(User).where(User.verification_token == token)
        )
        user = query.scalar_one_or_none()

        if not user:
            raise InvalidCredentialsError("Invalid verification token")

        user.is_verified = True
        user.verification_token = None
        await self.session.commit()
        return user

    async def create_password_reset_token(self, email: str) -> Optional[str]:
        """Create password reset token"""
        user = await self.user_service.get_user_by_email(email)
        if not user:
            return None

        token = str(uuid4())
        user.password_reset_token = token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        await self.session.commit()
        return token

    async def reset_password(self, token: str, new_password: str) -> User:
        """Reset user's password"""
        query = await self.session.execute(
            select(User).where(
                User.password_reset_token == token,
                User.password_reset_expires > datetime.utcnow()
            )
        )
        user = query.scalar_one_or_none()

        if not user:
            raise InvalidCredentialsError("Invalid or expired reset token")

        user.hashed_password = self.get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        await self.session.commit()
        return user

    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> User:
        """Change user's password"""
        if not self.verify_password(current_password, user.hashed_password):
            raise InvalidCredentialsError("Current password is incorrect")

        user.hashed_password = self.get_password_hash(new_password)
        await self.session.commit()
        return user
