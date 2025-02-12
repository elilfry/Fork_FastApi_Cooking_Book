from typing import List, Optional
from pydantic import BaseModel


class Ingredient(BaseModel):
    name: str
    quantity: Optional[str] = 'По вкусу'

    class Config:
        orm_mode = True


class Step(BaseModel):
    step_description: str
    step_time: int
    # recipe_id: int

    class Config:
        orm_mode = True


class RecipeGet(BaseModel):
    id: int
    name: str
    description: Optional[str]
    ingredients: List[Ingredient]
    steps: List[Step]

    class Config:
        orm_mode = True


class RecipePost(BaseModel):
    name: str
    description: Optional[str] = None
    ingredients: Optional[List[Ingredient]]
    steps: Optional[List[Step]]

    class Config:
        orm_mode = True
