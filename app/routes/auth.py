"""Authentication routes for user login and registration."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

import app.services.auth as auth_service

router = APIRouter()


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate a user and return an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The OAuth2 form data containing username and password.

    Raises:
        HTTPException: If authentication fails.

    Returns:
        JSONResponse: A response containing the access token.
    """
    token = await auth_service.authenticate_user(form_data.username, form_data.password)
    if token:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"access_token": token},
        ) 
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/register")
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    """Register a new user.
    
    Args:
        form_data (OAuth2PasswordRequestForm): The OAuth2 form data containing username and password.

    Raises:
        HTTPException: If registration fails.

    Returns:
        JSONResponse: A response containing the access token.
    """
    print(form_data.username, form_data.password)
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required",
        )

    token = await auth_service.register_user(form_data.username, form_data.password)
    if token:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"access_token": token},
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid registration data",
    )
