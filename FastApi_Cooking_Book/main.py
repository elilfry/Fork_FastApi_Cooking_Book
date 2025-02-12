from fastapi_users import FastAPIUsers

from auth.ayth import auth_backend
from auth.auth_manager import get_user_manager
from auth.auth_schemas import UserRead, UserCreate

from db.models import *
from db import schemas
import spec_functions
from db.connector import get_db

import uvicorn
from typing import List, Optional
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

app = FastAPI()

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()


#регистрация
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

#авторизация
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)


# Получение списка всех рецептов
@app.get("/recipes/", response_model=List[schemas.RecipeGet])
def get_all_recipes(session: Session = Depends(get_db)):
    '''Получить список всех рецепты из бд'''
    recipe_db = session.query(Recipe).all()
    return recipe_db


# Получение рецепта по id
@app.get("/recipes/{recipe_id}/", response_model=schemas.RecipeGet)
def get_recipe_by_id(recipe_id: int, session: Session = Depends(get_db)):
    '''Получить рецепт по его id в бд'''
    recipe_db = spec_functions.get_recipe_by_id(recipe_id, session)
    spec_functions.check_recipe_not_none(recipe_db, session)
    return recipe_db


# Добавление рецепта в бд
@app.post("/recipes/add_recipe/")
def add_new_recipe(recipe: schemas.RecipePost, session: Session = Depends(get_db), _: User = Depends(current_user)):
    '''Добавить рецепт в бд'''
    steps = [Step(**step.dict()) for step in recipe.steps]
    ingredients = [Ingredient(name=ingredient.name.lower(), quantity=ingredient.quantity) for ingredient in
                   recipe.ingredients]
    recipe_db = Recipe(name=recipe.name, description=recipe.description, ingredients=ingredients, steps=steps)
    session.add(recipe_db)
    session.commit()
    session.refresh(recipe_db)
    spec_functions.check_unique_ingredients(session, ingredients)
    return recipe


# Обновление информации о рецепте по id
@app.put("/recipes/update/{recipe_id}/")
def update_recipe_by_id(recipe: schemas.RecipePost, recipe_id: int, session: Session = Depends(get_db),
                        _: User = Depends(current_user)):
    '''Обновить информацию о рецепте, по его id в бд'''
    recipe_db = spec_functions.get_recipe_by_id(recipe_id, session)
    spec_functions.check_recipe_not_none(recipe_db, session)
    # Удаление старых ингредиентов
    session.query(Ingredient).filter_by(recipe_id=recipe_id).delete()
    # Добавление новых ингредиентов, если есть
    if recipe.ingredients:
        new_ingredients = [Ingredient(name=ingredient.name.lower(), quantity=ingredient.quantity, recipe_id=recipe_id)
                           for ingredient in recipe.ingredients]
        session.add_all(new_ingredients)
        # Проверка на новые уникальные ингредиенты
        spec_functions.check_unique_ingredients(session, new_ingredients)

    # Удаление старых шагов
    session.query(Step).filter_by(recipe_id=recipe_id).delete()
    # Добавление новых шагов, если есть
    if recipe.steps:
        new_steps = [Step(step_description=step.step_description, step_time=step.step_time, recipe_id=recipe_id)
                     for step in recipe.steps]
        session.add_all(new_steps)
    # Обновление информации о рецепте
    recipe_db.name = recipe.name
    recipe_db.description = recipe.description
    session.commit()
    session.refresh(recipe_db)
    return {"new_recipe": recipe}


# Удаление рецепта из бд
@app.delete("/recipes/delete/{recipe_id}/")
def delete_recipe_by_id(recipe_id: int, session: Session = Depends(get_db), _: User = Depends(current_user)):
    '''Удалить рецепт по его id в бд'''
    recipe_db = spec_functions.get_recipe_by_id(recipe_id, session)
    spec_functions.check_recipe_not_none(recipe_db, session)
    session.delete(recipe_db)
    session.commit()
    return {"message": f"Recipe with id {recipe_id} has been deleted."}


# Сортировка рецептов по общему времени приготовления
@app.get("/recipes/sort_by_cooking_time", response_model=List[schemas.RecipeGet])
def sort_recipes_by_time(desc: Optional[bool] = False, session: Session = Depends(get_db)):
    '''
    Функция сортирует рецепты по общему времени приготовления.
    -desc - сортировка в порядке убывания
    '''
    recipes = session.query(Recipe).join(Step).group_by(Recipe).order_by(func.sum(Step.step_time)).all()
    if desc:
        recipes.reverse()
    return recipes


# Фильтрация по максимальному времени приготовления + сортировка
@app.get("/recipes/filter_by_cooking_time/{max_cooking_time}", response_model=List[schemas.RecipeGet])
def filter_recipes_by_time(max_cooking_time: int, gt: Optional[bool] = False, desc: Optional[bool] = False,
                           session: Session = Depends(get_db)):
    '''
    Функция принимает максимальное время, и выводит рецепты, общее время готовки которых не превышает данное число.
    -gt - необязательный аргумент, вернёт рецепты, время готовки которых превышает переданное
    -desc - сортировка в порядке убывания
    '''
    if gt:
        recipes = session.query(Recipe).join(Step).group_by(Recipe) \
            .having(func.sum(Step.step_time) > max_cooking_time).order_by(func.sum(Step.step_time)).all()
    else:
        recipes = session.query(Recipe).join(Step).group_by(Recipe) \
            .having(func.sum(Step.step_time) <= max_cooking_time).order_by(func.sum(Step.step_time)).all()
    if desc:
        recipes.reverse()
    return recipes


# Фильтрация по переданному списку ингредиентов
@app.post("/recipes/filter_by_ingredients", response_model=List[schemas.RecipeGet])  #
def filter_recipes_by_ingredients(ingredients: List[str], session: Session = Depends(get_db)):
    '''
    Функция принимает список ингредиентов, и возвращает рецепты, в состав которых
    переданные ингредиенты входят
    '''
    unique_ingredients = session.query(UniqueIngredient).all()
    unique_ingredient_names = [ingredient.name.lower() for ingredient in unique_ingredients]  # уникальные имена из бд
    # список поступивших ингредиентов, которые есть в бд
    received_ingredients = [ingredient.lower() for ingredient in ingredients
                            if ingredient.lower() in unique_ingredient_names]

    # Join между Recipe+Ingredient, фильтрация по имени, группировка по id, и сверка количества ингредиентов группы
    recipes = (session.query(Recipe).join(Ingredient).filter(Ingredient.name.in_(received_ingredients))
               .group_by(Recipe.id).having(func.count(Ingredient.name) == len(received_ingredients)).all())
    return recipes


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
