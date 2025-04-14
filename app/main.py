"""Main entry point for the FastAPI application."""

from fastapi import FastAPI

from app.routes import auth, recipes

app = FastAPI(title="Recipes Api")


@app.get("/")
async def root():
    """Endpoint for the root URL."""
    return "Welcome to the Recipes API!"


app.include_router(auth.router, tags=["Authentication"], prefix="/api/auth")
app.include_router(recipes.router, tags=["Recipes"], prefix="/api/recipes")
