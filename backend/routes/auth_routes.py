from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
import bcrypt
import jwt
import os
from datetime import datetime, timedelta, timezone

try:  # Support both package and standalone execution
    from backend.models import User  # type: ignore
    from backend.db import get_session  # type: ignore
    from backend.config import settings  # type: ignore
    from backend.schemas import UserCreate, UserResponse  # type: ignore
    from backend.auth import verify_token  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    from ..models import User
    from ..db import get_session
    from ..config import settings
    from ..schemas import UserCreate, UserResponse
    from ..auth import verify_token


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed match."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    session: Session = Depends(get_session),
    user_id: str = Depends(verify_token)
):
    """Get current authenticated user"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

@router.post("/register")
async def register_user(user_data: UserCreate, session: Session = Depends(get_session)):
    """Register a new user"""
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    new_user = User(
        id=f"user-{os.urandom(4).hex()}",
        email=user_data.email,
        name=user_data.name or "",
        password_hash=hashed_password,
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    # Generate token
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode = {"sub": new_user.id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.BETTER_AUTH_SECRET, algorithm="HS256")
    
    user_response = {
        "id": new_user.id,
        "email": new_user.email,
        "name": new_user.name,
        "created_at": new_user.created_at.isoformat()
    }
    
    return {"access_token": encoded_jwt, "token_type": "bearer", "user": user_response}

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    """Login and get access token"""
    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode = {"sub": user.id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.BETTER_AUTH_SECRET, algorithm="HS256")

    # Return a structure that includes the user object for the frontend
    user_data = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "created_at": user.created_at.isoformat()
    }

    return {"access_token": encoded_jwt, "token_type": "bearer", "user": user_data}
