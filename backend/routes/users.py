from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
import bcrypt
import os

try:  # Support both package and standalone execution
    from models import User  # type: ignore
    from schemas import UserCreate, UserResponse  # type: ignore
    from db import get_session  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    from ..models import User
    from ..schemas import UserCreate, UserResponse
    from ..db import get_session

router = APIRouter(prefix="/api", tags=["users"])


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    """Create new user"""
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = hash_password(user_data.password)

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
