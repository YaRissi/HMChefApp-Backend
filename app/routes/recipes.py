"""Recipes API routes."""

from fastapi import APIRouter, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

import app.services.auth as auth_service
from app.models.models import Recipe, RecipeResponse
from app.services.redis_hander import RedisHandler

redis_handler = RedisHandler()


async def lifespan(_: FastAPI):
    """Lifespan event for the FastAPI application, to close the Redis handler."""
    yield
    await redis_handler.close()


router = APIRouter(lifespan=lifespan)


async def validate_header(request: Request, user: str = None) -> str:
    """Validate the Authorization header and user

    Args:
        request (Request): current request object
        user (str, optional): username of the user. Defaults to None.

    Raises:
        HTTPException: the Authorization header is missing || the token is invalid || the user is unauthorized

    Returns:
        str: username of the validated user
    """
    auth_token = request.headers.get("Authorization")
    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization header is missing",
        )
    success, user_info = await auth_service.validate_token(auth_token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    if user_info.get("username") != user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized user"
        )
    return user


@router.get("/", response_model=RecipeResponse)
async def get_recipes(request: Request, user: str):
    """Get all Recipes for a user.

    Args:
        request (Request): current request object
        user (str): username of the user

    Raises:
        HTTPException: the user parameter is missing || the validation fails

    Returns:
        RecipeResponse: list of recipes for the user
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User Param is missing"
        )
    await validate_header(request, user)
    try:
        recipes = await redis_handler.get_recipes(user)
        return JSONResponse({"recipes": recipes})
    except Exception as redis_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to get Recipes for user: {user}: {redis_error}",
        ) from redis_error


@router.post("/")
async def create_recipe(request: Request, user: str, recipe: Recipe):
    """Create a Recipe for a user.

    Args:
        request (Request): current request object
        user (str): username of the user
        recipe (Recipe): recipe data to be added

    Raises:
        HTTPException: user parameter is missing || the validation fails

    Returns:
        JSONResponse: response indicating success or failure
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User Param is missing"
        )
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
        ) from redis_error


@router.delete("/")
async def delete_recipe(
    request: Request, user: str, recipe_id: str = Query(alias="id")
):
    """Delete a Recipe for a user.

    Args:
        request (Request): current request object
        user (str): username of the user
        recipe_id (str): ID of the recipe to be deleted (alias: "id")

    Raises:
        HTTPException: user parameter is missing || the validation fails || the recipe ID is invalid or not found

    Returns:
        JSONResponse: response indicating success or failure
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User Param is missing"
        )
    await validate_header(request, user)
    try:
        await redis_handler.delete_recipe(user, recipe_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Recipe deleted successfully"},
        )
    except Exception as redis_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to delete Recipe for user: {user}: {redis_error}",
        ) from redis_error
