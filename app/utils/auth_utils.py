from datetime import datetime, timedelta, timezone
import jwt
from app.schemas.token_payload_schema import TokenPayload
from app.core.settings import settings

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    Args:
        data (dict): Data to encode in the token.
        expires_delta (timedelta | None): Custom expiration duration.

    Returns:
        str: Encoded JWT access token.
    """
    to_encode = data.copy()
    expire = (datetime.now(timezone.utc) +
              (expires_delta
               if expires_delta
               else timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
               )
              )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

def decode_access_token(token: str) -> TokenPayload:
    """
    Decode a JWT access token.

    Args:
        token (str): JWT token to decode.

    Returns:
        TokenPayload: Decoded token payload containing
        authentication information.

    Raises:
        jwt.InvalidTokenError: If the token is invalid.
        jwt.ExpiredSignatureError: If the token has expired.
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )
    return TokenPayload(**payload)