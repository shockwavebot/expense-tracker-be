# expense_tracker/core/security.py
from datetime import datetime, timedelta
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from expense_tracker.core.settings import settings
from expense_tracker.db.session import get_session
from expense_tracker.models.user import User
from expense_tracker.schemas.token import TokenPayload

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "your-secret-key-here"  # Change this!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configure password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # You can adjust this for security vs. speed
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Error verifying password: {str(e)}")
        return False


def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Error hashing password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing password"
        )


def create_access_token(
    subject: str | Any, expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        print(f"Error creating access token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating access token"
        )


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    """Get the current user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            raise credentials_exception
    except JWTError as e:
        print(f"JWT Error: {str(e)}")
        raise credentials_exception
    except Exception as e:
        print(f"Unexpected error in token validation: {str(e)}")
        raise credentials_exception

    try:
        result = await db.execute(
            select(User).where(User.id == int(token_data.sub))
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise credentials_exception
        return user
    except Exception as e:
        print(f"Database error in get_current_user: {str(e)}")
        raise credentials_exception
