"""Models for the recipe API."""
from typing import List

from pydantic import BaseModel


class Recipe(BaseModel):
    """Model for a Recipe."""
    id: str
    name: str
    description: str
    category: str
    imageUri: str


class RecipeResponse(BaseModel):
    """Model for a Recipe response."""
    recipes: List[Recipe]
