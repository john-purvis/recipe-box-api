import sqlite3

from flask import Blueprint, jsonify, request

from .common import require_authorization

recipes_bp = Blueprint("recipes", __name__)

@recipes_bp.get("/")
@require_authorization
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
    from .common import get_db, row_to_dict

    # Extract from kwargs
    user_id_str = kwargs.get('current_user_id')
    is_admin = kwargs.get('is_admin')
    # current_user = kwargs.get('current_user')
    if is_admin:
        # Admin users can see all recipes
        rows = get_db().execute("SELECT * FROM recipes ORDER BY id").fetchall()
    else:
        # Non-admin users can only see their own recipes or public recipes
        rows = get_db().execute("SELECT * FROM recipes WHERE (user_id = ? OR is_public = 1) ORDER BY id", (user_id_str,)).fetchall()
    return jsonify([row_to_dict(r) for r in rows]), 200

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
    from .common import get_db, row_to_dict

    # Extract from kwargs
    user_id_str = kwargs.get('current_user_id')
    is_admin = kwargs.get('is_admin')
    # current_user = kwargs.get('current_user')
    if is_admin:
        row = get_db().execute(
            "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
        ).fetchone()
    else:
        # Non-admin users can only access their own recipes or public recipes
        row = get_db().execute(
            "SELECT * FROM recipes WHERE id = ? AND (user_id = ? OR is_public = 1)",
            (recipe_id, user_id_str)
        ).fetchone()
    if row is None:
        return jsonify({"error": "recipe not found"}), 404
    return jsonify(row_to_dict(row)), 200

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
    from .common import get_db, row_to_dict

    # Extract from kwargs
    user_id_str = kwargs.get('current_user_id')
    # is_admin = kwargs.get('is_admin')
    # current_user = kwargs.get('current_user')
    # get data from request body - silent=True returns None if data not found instead of raising an error
    data = request.get_json(silent=True)
    if not data or not data.get("title") or not data.get("ingredients"):
        return jsonify({"error": "title and ingredients are required"}), 400
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO recipes (user_id, title, ingredients, instructions, is_public)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                user_id_str,
                data["title"],
                data["ingredients"],
                data.get("instructions", ""),
                1 if data.get("is_public", True) else 0,
            ),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "a recipe with that title already exists"}), 409
    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
    return jsonify(row_to_dict(row)), 201

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
    from .common import get_db, row_to_dict

    # Extract from kwargs
    user_id_str = kwargs.get('current_user_id')
    is_admin = kwargs.get('is_admin')
    # current_user = kwargs.get('current_user')
    # get data from request body - silent=True returns None if data not found instead of raising an error
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "a JSON body is required"}), 400
    db = get_db()
    # check ownership for update operation - only the owner or an admin can update a recipe
    check_recipe = db.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    if not check_recipe:
        return jsonify({"error": "recipe not found"}), 404
    if str(check_recipe["user_id"]) != user_id_str and is_admin is not True:
        return jsonify({"error": "access denied"}), 403
    # authenticated and authorized to update the recipe
    fields, values = [], []
    for column in ("title", "ingredients", "instructions"):
        if column in data:
            fields.append(f"{column} = ?")
            values.append(data[column])
    if "is_public" in data:
        fields.append("is_public = ?")
        values.append(1 if data["is_public"] else 0)
    if not fields:
        return jsonify({"error": "nothing to update"}), 400
    values.append(recipe_id)
    try:
        cur = db.execute(
            f"UPDATE recipes SET {', '.join(fields)} WHERE id = ?", values
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "a recipe with that title already exists"}), 409
    if cur.rowcount == 0:
        return jsonify({"error": "recipe not found"}), 404
    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
    ).fetchone()
    return jsonify(row_to_dict(row)), 200

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
    from .common import get_db

    # Extract from kwargs
    user_id_str = kwargs.get('current_user_id')
    is_admin = kwargs.get('is_admin')
    # current_user = kwargs.get('current_user')
    db = get_db()
    # check ownership for delete operation - only the owner or an admin can delete a recipe
    check_recipe = db.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    if not check_recipe:
        return jsonify({"error": "recipe not found"}), 404
    if str(check_recipe["user_id"]) != user_id_str and is_admin is not True:
        return jsonify({"error": "access denied"}), 403
    # authenticated and authorized to delete the recipe
    cur = db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "recipe not found"}), 404
    return "", 204
