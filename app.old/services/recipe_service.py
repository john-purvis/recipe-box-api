# app/services/recipe_service.py

from flask import current_app
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app.db import recipe_to_dict
from app.extensions import dba
from app.models.recipes import Recipe


def list_recipes_for_user(user_id, is_admin):
    if is_admin:
        recipes = (
            Recipe.query
            .order_by(Recipe.id)
            .all()
        )
        return [recipe_to_dict(r) for r in recipes]
    else:
        recipes = (
            Recipe.query
            .filter(
                (Recipe.user_id == user_id) | (Recipe.is_public == 1)
            )
            .order_by(Recipe.id)
            .all()
        )
        return [recipe_to_dict(r) for r in recipes]

def get_recipe_for_user(recipe_id, user_id, is_admin):
    if is_admin:
        recipe = (
            Recipe.query
            .filter(
                Recipe.id == recipe_id
            )
            .first()
        )
        return recipe_to_dict(recipe)
    else:
        recipe = (
            Recipe.query
            .filter(
                Recipe.id == recipe_id,
                or_(Recipe.user_id == user_id, Recipe.is_public == 1),
            )
            .first()
        )
    return recipe_to_dict(recipe)

def create_recipe_for_user(user_id, data):
    recipe = Recipe(
        user_id=user_id,
        title=data["title"],
        ingredients=data["ingredients"],
        instructions=data.get("instructions", ""),
        is_public=data.get("is_public", True),
    )
    dba.session.add(recipe)

    try:
        dba.session.commit()
    except IntegrityError:
        dba.session.rollback()
        return None, "a recipe with that title already exists"

    # At this point `recipe.id` is populated and the row is in the DB.
    if current_app.debug:
        print("DEBUG: recipe saved")
    return recipe_to_dict(recipe), None

def update_recipe_for_user(recipe_id, user_id, is_admin, data):
    # Fetch recipe
    recipe = (
        Recipe.query
        .filter(
            Recipe.id == recipe_id
        )
        .first()
    )

    # Check existence first
    if not recipe:
        return None, "recipe_not_found"

    # Check ownership using user_id
    # if str(recipe.user_id) != str(user_id) and not is_admin:
    #     return None, "access_denied"

    # Check ownership using foreign key relationship
    if str(recipe.user.id) != str(user_id) and not is_admin:
        return None, "access_denied"

    # Update the recipe
    if "title" in data:
        recipe.title = data["title"]
    if "ingredients" in data:
        recipe.ingredients = data["ingredients"]
    if "instructions" in data:
        recipe.instructions = data["instructions"]
    if "is_public" in data:
        recipe.is_public = 1 if data["is_public"] else 0

    try:
        # commit changes
        dba.session.commit()
    except IntegrityError:
        # rollback on error
        dba.session.rollback()
        return None, "a recipe with that title already exists"

    return recipe_to_dict(recipe), None

def delete_recipe_for_user(recipe_id, user_id, is_admin):
    recipe = (
        Recipe.query
        .filter(
            Recipe.id == recipe_id
        )
        .first()
    )
    if not recipe:
        return "recipe_not_found"

    # Check ownership using user_id
    # if str(recipe.user_id) != str(user_id) and not is_admin:
    #     return "access_denied"

    # Check ownership using foreign key relationship
    if str(recipe.user.id) != str(user_id) and not is_admin:
        return None, "access_denied"

    dba.session.delete(recipe)

    # commit changes
    dba.session.commit()

    return None  # success
