from typing import List
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.models.models import Recipe, RecipeResponse
from app.services.redis_hander import RedisHandler

redis_handler = RedisHandler()

async def lifespan(_: FastAPI):
    yield
    await redis_handler.close()

router = APIRouter(lifespan=lifespan)

@router.get("/", response_model=RecipeResponse)
async def get_recipes(user: str):
    """Get a all Recipes for a user."""
    try:
        recipes = await redis_handler.get_recipes(user)
        return JSONResponse({"recipes": recipes})
    except Exception as redis_error:
        raise HTTPException(
            status_code=404,
            detail=f"Failed to get Recipes for user: {user}: {redis_error}",
        )

@router.post("/")
async def create_recipe(user: str, recipe: Recipe):
    """Create a Recipe for a user."""
    try:
        await redis_handler.add_recipes(user, recipe.model_dump())
        return JSONResponse(
            status_code=201,
            content={"message": "Recipe added successfully"},
        )
    except Exception as redis_error:
        raise HTTPException(
            status_code=404,
            detail=f"Failed to add Recipe to user: {user}: {redis_error}",
        )

@router.delete("/{id}")
async def delete_recipe(user: str, id: str):
    """Delete a Recipe for a user."""
    try:
        await redis_handler.delete_recipe(user, id)
        return JSONResponse(
            status_code=200,
            content={"message": "Recipe deleted successfully"},
        )
    except Exception as redis_error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete Recipe for user: {user}: {redis_error}",
        )