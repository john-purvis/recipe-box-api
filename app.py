"""
Recipe Box API.

A working Flask + SQLite CRUD API for recipes.
"""

import os
import sqlite3
from functools import wraps

from flasgger import Swagger
from flask import Flask, g, json, jsonify, request, send_from_directory

# Import native components from the Flask extension
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# The securityDefinitions below is used by Swagger to describe the
# authentication mechanism for the API.
# It creates the Authorize button and input box in the Swagger interface,
# allowing users to input their JWT token for authenticated requests.
swagger_data = {
    "swagger": "2.0",
    "info": {
        "title": "Recipe Book API",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "AuthKey": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter your JWT token with the 'Bearer' prefix. Example: 'Bearer eyJhbGciOi...'"
        }
    }
}

swagger = Swagger(app, template=swagger_data)
jwt_manager = JWTManager(app)

# Turn off automatic alphabetical sorting of JSON keys in responses for better readability
app.config["JSON_SORT_KEYS"] = os.environ.get("JSON_SORT_KEYS", "false").lower() == "false"
# The modern way to disable alphabetical key sorting in Flask 2.3+
app.json.sort_keys = False

# Fetch variables from environment fallback to strings if missing
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'default-safe-fallback-key-for-local-dev')
DATABASE = os.environ.get('DATABASE_NAME', 'recipes.db')

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def require_authorization(f):
    """
    Custom decorator that bundles Flask-JWT-Extended authentication
    and automatically injects user context arguments into the route
    for authorization checks.
    """
    @wraps(f)
    @jwt_required()  # Automatically catches expired/invalid tokens
    def decorated_function(*args, **kwargs):
        # 1. Pull data directly out of the validated token payload
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get("is_admin", False)

        # 2. Fetch the fresh user row from the database
        conn = get_db()
        user_row = conn.execute('SELECT * FROM users WHERE id = ?', (current_user_id,)).fetchone()
        # conn.close()

        if not user_row:
            return jsonify({'message': 'User profile no longer exists'}), 404

        # 3. Inject the context variables as keyword arguments into the route
        return f(
            current_user_id=current_user_id,
            is_admin=is_admin,
            current_user=user_row,
            *args, **kwargs  # noqa: B026
        )
    return decorated_function

def row_to_dict(row):
    """
    Convert a SQLite row object to a dictionary.
    This function dynamically builds a dictionary from the row's keys and values,
    ensuring that only the columns present in the row are included.
    """
    if not row:
        return None

    json_str = {key: row[key] for key in row.keys()}  # noqa: SIM118

    # 2. Check if the target field exists in the dictionary
    if "is_admin" in json_str:
        value = json_str["is_admin"]

        # Check for numeric 1/0 or string "1"/"0"
        if value in (1, "1"):
            json_str["is_admin"] = True
        elif value in (0, "0"):
            json_str["is_admin"] = False

    if "is_public" in json_str:
        value = json_str["is_public"]

        # Check for numeric 1/0 or string "1"/"0"
        if value in (1, "1"):
            json_str["is_public"] = True
        elif value in (0, "0"):
            json_str["is_public"] = False

    return json_str


@app.get("/")
def home():
    """
    Serve the homepage of the Recipe Box API..
    ---
    tags:
      - Home
    responses:
        200:
            description: The homepage of the Recipe Box API
            content:
            text/html:
                schema:
                type: string
                example: "<html><body><h1>Welcome to the Recipe Box API</h1></body></html>"
    """
    return send_from_directory(app.root_path, "index.html")


@app.post("/register")
def create_user():
    """
    User registration endpoint that creates a new user in the database.
    ---
    tags:
      - Registration
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
            email:
              type: string
            phone:
              type: string
    responses:
      201:
        description: User created successfully
      400:
        description: Bad request
      409:
        description: Username already taken
    """
    data = request.get_json(silent=True) or {}
    username, password, email, phone = data.get("username"), data.get("password"), data.get("email"), data.get("phone")
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400
    db = get_db()
    try:
        # Hash the password before storing it in the database
        password_hash = generate_password_hash(password)
        # Insert the new user into the database
        db.execute(
            "INSERT INTO users (username, password_hash, email, phone) VALUES (?, ?, ?, ?)",
            (username, password_hash, email, phone)
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "username taken"}), 409
    return jsonify({"message": f"registered {username}"}), 201


@app.post('/login')
def login():
    """
    User login endpoint that authenticates a user and returns a JWT token.
    ---
    tags:
      - Login / Logout
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful, returns a JWT token
      400:
        description: Missing credentials
      401:
        description: Invalid username or password
    """
    auth_data = request.get_json()
    if not auth_data or 'username' not in auth_data or 'password' not in auth_data:
        return jsonify({'message': 'Missing credentials'}), 400

    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (auth_data['username'],)).fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], auth_data['password']):
        # Use the database user ID as the primary token identity
        # JWT_extended version 4.0 requires the identity to be a string, so we convert it here
        user_id = str(user['id'])

        # Add custom claims for quick authorization checks (e.g., roles)
        custom_claims = {"is_admin": bool(user['is_admin'])} # Assumes an 'is_admin' column exists

        # Generate token with identity and extra attributes
        access_token = create_access_token(identity=user_id, additional_claims=custom_claims)

        return jsonify({'message': 'Login successful', 'token': access_token}), 200

    return jsonify({'message': 'Invalid username or password'}), 401

@app.post('/logout')
@require_authorization
def logout(**kwargs):
    """
    User logout endpoint that invalidates the JWT token.
    ---
    tags:
      - Login / Logout
    security:
        - AuthKey: []  # <--- Tells Swagger to fetch the token from the lock box
    responses:
        200:
            description: Logout successful
        403:
            description: Access denied (not logged in)
    """
    # In a real application, you would implement token revocation here.
    # For this example, we'll just return a success message.
    return jsonify({'message': 'Logout successful'}), 200


@app.get("/recipes")
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
    """
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

@app.get("/recipes/<int:recipe_id>")
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
      403:
        description: Access denied (not logged in)
      404:
        description: Recipe not found
    """
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

@app.post("/recipes")
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
      403:
        description: Access denied (not logged in)
      409:
        description: A recipe with the same title already exists
    """
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

@app.patch("/recipes/<int:recipe_id>")
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
      403:
        description: Access denied (not the owner or an admin)
      404:
        description: Recipe not found
      409:
        description: A recipe with the same title already exists
    """
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

@app.delete("/recipes/<int:recipe_id>")
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
      403:
        description: Access denied (not the owner or an admin)
      404:
        description: Recipe not found
    """
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

@app.get("/users")
@require_authorization
def list_users(**kwargs):
    """
    List all users.
    ---
    tags:
      - Users
    security:
      - AuthKey: []  # <--- Tells Swagger to fetch the token from the lock box
    responses:
        200:
            description: A list of users
            content:
            application/json:
                schema:
                type: array
                items:
                    type: object
                    properties:
                    id:
                        type: integer
                    email:
                        type: string
                    phone:
                        type: string
                    is_admin:
                        type: boolean
    """
    # Extract from kwargs
    user_id_str = kwargs.get('current_user_id')
    is_admin = kwargs.get('is_admin')
    # current_user = kwargs.get('current_user')
    if is_admin:
        # Admin users can see all users
        rows = get_db().execute("SELECT id, email, phone, is_admin FROM users ORDER BY id").fetchall()
    else:
        # Non-admin users can only see their own user properties
        rows = get_db().execute("SELECT id, email, phone, is_admin FROM users WHERE id = ?", (user_id_str,)).fetchall()
    return jsonify([row_to_dict(r) for r in rows]), 200

@app.patch('/users/<int:user_id>')
@require_authorization # <--- This decorator enforces authentication and injects user context into the route using **kwargs for authorization checks
def update_user(user_id, **kwargs):
    """
    Update the details and / or password for a user in the database.
    ---
    tags:
      - Users
    security:
        - AuthKey: []  # <--- Tells Swagger to fetch the token from the lock box
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            password:
              type: string
            email:
              type: string
            phone:
              type: string
    responses:
      200:
        description: User updated successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                email:
                  type: string
                phone:
                  type: string
                is_admin:
                  type: boolean
    """
    # Extract from kwargs
    user_id_str = kwargs.get('current_user_id')
    is_admin = kwargs.get('is_admin')
    # current_user = kwargs.get('current_user')
    # get data from request body - silent=True returns None if data not found instead of raising an error
    data = request.get_json(silent=True) or {}
    # check ownership for update operation - only the owner or an admin can update a user
    if str(user_id) != user_id_str and is_admin is not True:
        return jsonify({"error": "access denied"}), 403
    # authenticated and authorized to update the user
    db = get_db()
    fields, values = [], []
    for column in ("password", "email", "phone"):
        if column in data:
            fields.append(f"{column} = ?")
            values.append(data[column])
    if not fields:
        return jsonify({"error": "nothing to update"}), 400
    values.append(user_id)
    try:
        cur = db.execute(
            f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values
        )
        db.commit()
    except sqlite3.IntegrityError:
        if data.get("email") and data.get("phone"):
            return jsonify({"error": "a user with that email or phone number already exists"}), 409
        elif data.get("email"):
            return jsonify({"error": "a user with that email already exists"}), 409
        elif data.get("phone"):
            return jsonify({"error": "a user with that phone number already exists"}), 409
    if cur.rowcount == 0:
        return jsonify({"error": "user not found"}), 404
    row = db.execute(
        "SELECT id, email, phone, is_admin FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    return jsonify(row_to_dict(row)), 200

@app.delete('/users/<int:user_id>')
@require_authorization
def delete_user(user_id, **kwargs):
    """
    Delete a user from the database.
    ---
    tags:
      - Users
    security:
        - AuthKey: []  # <--- Tells Swagger to fetch the token from the lock box
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: User deleted successfully
      403:
        description: Access denied (not the owner or an admin)
      404:
        description: User not found
    """
    # Extract from kwargs
    # user_id_str = kwargs.get('current_user_id')
    is_admin = kwargs.get('is_admin')
    # current_user = kwargs.get('current_user')
    db = get_db()
    # only the admin can delete a user
    if is_admin is not True:
        return jsonify({"error": "access denied"}), 403
    # authenticated and authorized to delete the user
    cur = db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "user not found"}), 404
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)
