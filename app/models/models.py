from typing import List, Optional
from pydantic import BaseModel

class Recipe(BaseModel):
    id: str
    name: str
    description: str
    category: str
    imageUri: str


class RecipeResponse(BaseModel):
    recipes: List[Recipe]

