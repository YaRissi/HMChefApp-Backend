"""Service for authentication and token management."""

from typing import Any, Dict, Optional, Tuple

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.internal.settings import settings
from app.services.redis_hander import RedisHandler

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
REDIS_HANDLER = RedisHandler()


async def validate_token(token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Validates a JWT token and returns the payload if valid.

    Args:
        token (str): the JWT token to validate.

    Returns:
        Tuple[bool, Optional[Dict[str, Any]]]: A tuple containing a boolean indicating whether the token is valid and the payload if valid.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        return True, payload
    except jwt.PyJWTError:
        return False, None


async def create_token(data: dict) -> str:
    """Creates a JWT token with the given data.

    Args:
        data (dict): The data to include in the token.
    Returns:
        str: The generated JWT token.
    """
    to_encode = data.copy()

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


async def register_user(username: str, password: str) -> str:
    """Registers a new user and returns a token.

    Args:
        username (str): The username.
        password (str): The password.

    Returns:
        str: The generated JWT token.
    """
    if await REDIS_HANDLER.check_user(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    hashed_password = PWD_CONTEXT.hash(password)
    await REDIS_HANDLER.set_user_password(username, hashed_password)

    token = await create_token({"username": username})

    return token


async def authenticate_user(username: str, password: str) -> Optional[str]:
    """Authenticates a user and returns a token.

    Args:
        username (str): The username.
        password (str): The password.

    Returns:
        Optional[str]: The generated JWT token or None if authentication fails.
    """
    user_hashed_password = await REDIS_HANDLER.get_user_password(username)

    if user_hashed_password and PWD_CONTEXT.verify(password, user_hashed_password):
        token = await create_token({"username": username})
        return token

    return None
