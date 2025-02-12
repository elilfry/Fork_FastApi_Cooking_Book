from fastapi import HTTPException
from db.models import Recipe
from db.models import UniqueIngredient

def get_recipe_by_id(recipe_id, session):
    return session.query(Recipe).filter_by(id=recipe_id).first()

def check_unique_ingredients(session, ingredients):
    unique_ingredients = [uniq_ingredient.name for uniq_ingredient in session.query(UniqueIngredient).all()]
    for i in ingredients:
        if i.name.lower() not in unique_ingredients:
            session.add(UniqueIngredient(name=i.name.lower()))
            session.commit()
    return True


def check_recipe_not_none(recipe_db, session):
    if recipe_db is None:
        session.rollback()
        raise HTTPException(status_code=404, detail="Recipe not found")
    return True

