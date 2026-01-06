from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

try:
    from config import settings  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    from config import settings

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token and return user_id.

    Args:
        credentials: HTTP Bearer credentials from request header

    Returns:
        str: user_id extracted from token

    Raises:
        HTTPException: 401 if token invalid or expired
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"],
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired. Please sign in again.",
        )
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )
