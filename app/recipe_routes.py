# app/recipe_routes.py
from flask import Blueprint, current_app, jsonify, request

from app.extensions import cache
from app.middleware import require_authorization
from app.services.recipe_service import (
    create_recipe_for_user,
    delete_recipe_for_user,
    get_recipe_for_user,
    list_recipes_for_user,
    update_recipe_for_user,
)

recipes_bp = Blueprint("recipes", __name__)

@recipes_bp.get("/")
@cache.memoize(timeout=30)
def list_recipes(**kwargs):
    """
    List all recipes.
    ---
    tags:
      - Recipes
    security:
      - AuthKey: []  # <--- Tells Swagger to fetch the token from the lock box
    responses:
      200:
        description: A list of recipes
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  user_id:
                    type: integer
                  title:
                    type: string
                  ingredients:
                    type: string
                  instructions:
                    type: string
                  is_public:
                    type: boolean
      401:
        description: Unauthorized (not logged in)
      403:
        description: Access denied (not logged in)
    """
    if current_app.debug:
        print("DEBUG: HITTING DB FOR /recipes")
    user_id_str = kwargs.get("current_user_id")
    is_admin = kwargs.get("is_admin")
    recipes = list_recipes_for_user(user_id_str, is_admin)
    return jsonify(recipes), 200

@recipes_bp.get("/<int:recipe_id>")
@require_authorization
def get_recipe(recipe_id, **kwargs):
    """
    Get a recipe by its ID.
    ---
    tags:
      - Recipes
    security:
      - AuthKey: []  # <--- Tells Swagger to fetch the token from the lock box
    parameters:
      - name: recipe_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Recipe found
      401:
        description: Unauthorized (not logged in)
      403:
        description: Access denied (not logged in)
      404:
        description: Recipe not found
    """
    user_id_str = kwargs.get("current_user_id")
    is_admin = kwargs.get("is_admin")

    recipe = get_recipe_for_user(recipe_id, user_id_str, is_admin)
    if recipe is None:
        return jsonify({"error": "recipe not found"}), 404
    return jsonify(recipe), 200

@recipes_bp.post("/")
@require_authorization
def create_recipe(**kwargs):
    """
    Create a new recipe.
    ---
    tags:
      - Recipes
    security:
      - AuthKey: []  # <--- Tells Swagger to fetch the token from the lock box
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            ingredients:
              type: string
            instructions:
              type: string
            is_public:
              type: boolean
    responses:
      201:
        description: Recipe created successfully
      400:
        description: Invalid request body
      401:
        description: Unauthorized (not logged in)
      403:
        description: Access denied (not logged in)
      409:
        description: A recipe with the same title already exists
    """
    user_id_str = kwargs.get("current_user_id")
    data = request.get_json(silent=True)

    if not data or not data.get("title") or not data.get("ingredients"):
        return jsonify({"error": "title and ingredients are required"}), 400

    recipe, error = create_recipe_for_user(user_id_str, data)
    if error:
        return jsonify({"error": error}), 409

    # if the create_recipe succeeds then delete cached entry for the list_recipes route
    if current_app.debug:
        print("DEBUG: deleting cache for list_recipes")
    cache.delete_memoized(list_recipes)
    return jsonify(recipe), 201

@recipes_bp.patch("/<int:recipe_id>")
@require_authorization
def update_recipe(recipe_id, **kwargs):
    """
    Update a recipe by its ID.
    ---
    tags:
      - Recipes
    security:
      - AuthKey: []  # <--- Tells Swagger to fetch the token from the lock box
    parameters:
      - name: recipe_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            ingredients:
              type: string
            instructions:
              type: string
            is_public:
              type: boolean
    responses:
      200:
        description: Recipe updated successfully
      400:
        description: Invalid request body
      401:
        description: Unauthorized (not logged in)
      403:
        description: Access denied (not the owner or an admin)
      404:
        description: Recipe not found
      409:
        description: A recipe with the same title already exists
    """
    user_id_str = kwargs.get("current_user_id")
    is_admin = kwargs.get("is_admin")

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "a JSON body is required"}), 400

    recipe, error = update_recipe_for_user(recipe_id, user_id_str, is_admin, data)

    if error == "recipe_not_found":
        return jsonify({"error": "recipe not found"}), 404
    if error == "access_denied":
        return jsonify({"error": "access denied"}), 403
    if error == "nothing_to_update":
        return jsonify({"error": "nothing to update"}), 400
    if error == "duplicate_title":
        return jsonify({"error": "a recipe with that title already exists"}), 409

    # if the update_recipe succeeds then delete cached entry for the list_recipes route
    if current_app.debug:
        print("DEBUG: deleting cache for list_recipes")
    return jsonify(recipe), 200

@recipes_bp.delete("/<int:recipe_id>")
@require_authorization
def delete_recipe(recipe_id, **kwargs):
    """
    Delete a recipe by its ID.
    ---
    tags:
      - Recipes
    security:
      - AuthKey: []  # <--- Tells Swagger to fetch the token from the lock box
    parameters:
      - name: recipe_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Recipe deleted successfully
      401:
        description: Unauthorized (not logged in)
      403:
        description: Access denied (not the owner or an admin)
      404:
        description: Recipe not found
    """
    user_id_str = kwargs.get("current_user_id")
    is_admin = kwargs.get("is_admin")

    error = delete_recipe_for_user(recipe_id, user_id_str, is_admin)

    if error == "recipe_not_found":
        return jsonify({"error": "recipe not found"}), 404
    if error == "access_denied":
        return jsonify({"error": "access denied"}), 403

    # if the delete_recipe succeeds then delete cached entry for the list_recipes route
    if current_app.debug:
        print("DEBUG: deleting cache for list_recipes")
    return "", 204
