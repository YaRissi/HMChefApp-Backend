from fastapi import APIRouter, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.models.models import Recipe, RecipeResponse
from app.services.redis_hander import RedisHandler
import app.services.auth as auth_service

redis_handler = RedisHandler()

async def lifespan(_: FastAPI):
    yield
    await redis_handler.close()

router = APIRouter(lifespan=lifespan)

async def validate_header(request: Request, user: str = None) -> str:
    """Validate the header for the user."""
    auth_token = request.headers.get("Authorization")
    if not auth_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Authorization header is missing")
    success, user_info = await auth_service.validate_token(auth_token)
    if not success:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if user_info.get("username") != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized user")
    return user

@router.get("/", response_model=RecipeResponse)
async def get_recipes(request: Request, user: str):
    """Get all Recipes for a user."""
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User Param is missing")
    await validate_header(request, user)
    try:
        recipes = await redis_handler.get_recipes(user)
        return JSONResponse({"recipes": recipes})
    except Exception as redis_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to get Recipes for user: {user}: {redis_error}",
        )

@router.post("/{user}")
async def create_recipe(request: Request, user: str, recipe: Recipe):
    """Create a Recipe for a user."""
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User Param is missing")
    await validate_header(request, user)
    try:
        await redis_handler.add_recipes(user, recipe.model_dump())
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Recipe added successfully"},
        )
    except Exception as redis_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to add Recipe to user: {user}: {redis_error}",
        )

@router.delete("/{user}")
async def delete_recipe(request: Request, user: str, id: str):
    """Delete a Recipe for a user."""
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User Param is missing")
    await validate_header(request, user)
    try:
        await redis_handler.delete_recipe(user, id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Recipe deleted successfully"},
        )
    except Exception as redis_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to delete Recipe for user: {user}: {redis_error}",
        )