"""
Authentication Router
Handles user signup, login, and profile updates
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
import bcrypt

from app.database import get_db
from app.models import User
from app.schemas import SignupRequest, LoginRequest, UserResponse, UserUpdate
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    payload = {
        "sub": str(user_id),
        "exp": expire
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> int | None:
    """Decode JWT token and return user_id, or None if invalid"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return int(payload.get("sub"))
    except jwt.PyJWTError:
        return None


@router.post("/signup", response_model=UserResponse)
async def signup(request: SignupRequest, db: AsyncSession = Depends(get_db)):
    """Create a new user account"""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create new user
    user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        name=request.name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Generate token
    token = create_access_token(user.id)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        token=token,
        created_at=user.created_at
    )


@router.post("/login", response_model=UserResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return token"""
    # Find user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate token
    token = create_access_token(user.id)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        token=token,
        created_at=user.created_at
    )


@router.put("/user/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, 
    request: UserUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update user profile"""
    # Find user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if request.email is not None:
        # Check if new email is already taken by another user
        existing = await db.execute(
            select(User).where(User.email == request.email, User.id != user_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        user.email = request.email
    
    if request.name is not None:
        user.name = request.name
    
    if request.password is not None:
        user.hashed_password = hash_password(request.password)
    
    await db.commit()
    await db.refresh(user)
    
    # Generate new token
    token = create_access_token(user.id)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        token=token,
        created_at=user.created_at
    )
