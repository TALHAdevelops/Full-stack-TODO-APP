from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from better_auth.utils import hashPassword
import os

from ..models import User
from ..schemas import UserCreate, UserResponse
from ..db import get_session

router = APIRouter(prefix="/api", tags=["users"])

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    """Create new user"""
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    hashed_password = hashPassword(user_data.password)

    new_user = User(
        id=f"user-{os.urandom(4).hex()}",
        email=user_data.email,
        name=user_data.name,
        password_hash=hashed_password,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user
