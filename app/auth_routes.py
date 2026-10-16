import sqlite3

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from .common import require_authorization

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/login")
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
    from .common import get_db

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

@auth_bp.post("/register")
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
    from .common import get_db

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

@auth_bp.post('/logout')
@require_authorization
def logout(**kwargs):
    """
    User logout endpoint in a stateless JWT system.

    This does NOT invalidate the token on the server. Instead, the client
    must delete its stored JWT and stop sending it on future requests.
    ---
    tags:
      - Login / Logout
    security:
      - AuthKey: []
    responses:
      200:
        description: Logout acknowledged; client should discard token
      401:
        description: Unauthorized (no valid token provided)
    """
    return jsonify({
        "message": "Logout successful. Please delete your token on the client."
    }), 200

@auth_bp.get("/users")
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
      401:
        description: Unauthorized (not logged in)
      403:
        description: Access denied (not an admin)
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
    from .common import get_db, row_to_dict

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

@auth_bp.patch('/users/<int:user_id>')
@require_authorization
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
      400:
        description: Invalid request body
      401:
        description: Unauthorized (not logged in)
      403:
        description: Access denied (not the owner or an admin)
      404:
        description: User not found
      409:
        description: A user with that email or phone number already exists
    """
    from .common import get_db, row_to_dict

    # Extract from kwargs
    user_id_str = kwargs.get('current_user_id')
    is_admin = kwargs.get('is_admin')
    # current_user = kwargs.get('current_user')
    # get data from request body - silent=True returns None if data not found instead of raising an error
    data = request.get_json(silent=True) or {}
    # check ownership for update operation - only the owner or an admin can update a user
    if str(user_id) != user_id_str and is_admin is not True:
        return jsonify({"error": "access denied"}), 403
    pass_check = data.get("password")
    # check for blank password and remove it from the data dictionary to avoid storing a blank password hash
    if pass_check and pass_check.strip() == "":
        return jsonify({"error": "password cannot be blank"}), 400
    if pass_check:
        # remove "password" from data and store the hashed password in "password_hash"
        plain_text = data.pop("password")
        # Hash the password before storing it in the database
        data["password_hash"] = generate_password_hash(plain_text)
    # authenticated and authorized to update the user
    db = get_db()
    fields, values = [], []
    for column in ("password_hash", "email", "phone"):
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

@auth_bp.delete('/users/<int:user_id>')
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
      401:
        description: Unauthorized (not logged in)
      403:
        description: Access denied (not the owner or an admin)
      404:
        description: User not found
    """
    from .common import get_db

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
