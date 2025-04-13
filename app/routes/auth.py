from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return access token.
    """
    # Dummy authentication logic for demonstration purposes
    if form_data.username == "user" and form_data.password == "password":
        return {"access_token": "dummy_token", "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
@router.post("/register")
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Register a new user.
    """
    # Dummy registration logic for demonstration purposes
    if form_data.username and form_data.password:
        return {"message": "User registered successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid registration data",
        )
