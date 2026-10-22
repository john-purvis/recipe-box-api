# app/auth_routes.py
import sqlite3

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app.middleware import require_authorization
from app.services.auth_service import (
    authenticate_user,
    delete_user_for_user,
    list_users_for_user,
    register_user,
    update_user_for_user,
)

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
    auth_data = request.get_json()
    if not auth_data or 'username' not in auth_data or 'password' not in auth_data:
        return jsonify({'message': 'Missing credentials'}), 400

    user = authenticate_user(auth_data['username'], auth_data['password'])

    if user:
        # Use the user ID as the primary token identity
        # JWT_extended version 4.0 requires the identity to be a string, so we convert it here
        user_id = str(user['id'])

        # Add custom claims for quick authorization checks (e.g., roles)
        custom_claims = {"is_admin": bool(user['is_admin'])}

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
    data = request.get_json(silent=True) or {}
    username, password, email, phone = data.get("username"), data.get("password"), data.get("email"), data.get("phone")
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    success, message = register_user(username, password, email, phone)

    if not success:
        return jsonify({"error": f"{message}"}), 409
    return jsonify({"success": f"registered {username}"}), 201

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
    # Extract from kwargs
    user_id_str = kwargs.get('current_user_id')
    is_admin = kwargs.get('is_admin')
    users = list_users_for_user(user_id_str, is_admin)
    return jsonify(users), 200

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
    # Extract from kwargs
    user_id_str = kwargs.get('current_user_id')
    is_admin = kwargs.get('is_admin')

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "a JSON body is required"}), 400

    user, error = update_user_for_user(user_id_str, is_admin, user_id, data)

    # strip out any password_hash that may be in the user object
    if "password_hash" in user:
        user.pop("password_hash")

    if error == "password_is_empty":
        return jsonify({"error": "password cannot be blank"}), 400
    if error == "user_not_found":
        return jsonify({"error": "user not found"}), 404
    if error == "access_denied":
        return jsonify({"error": "access denied"}), 403
    if error == "nothing_to_update":
        return jsonify({"error": "nothing to update"}), 400
    if error == "duplicate_data":
        return jsonify({"error": "a user with that email or phone number already exists"}), 409
    if error == "duplicate_email":
        return jsonify({"error": "a user with that email already exists"}), 409
    if error == "duplicate_phone":
        return jsonify({"error": "a user with that phone number already exists"}), 409

    return jsonify(user), 200


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
    # Extract from kwargs
    user_id_str = kwargs.get('current_user_id')
    is_admin = kwargs.get('is_admin')
    # current_user = kwargs.get('current_user')

    error = delete_user_for_user(user_id_str, is_admin, user_id)

    if error == "user_not_found":
        return jsonify({"error": "user not found"}), 404
    if error == "access_denied":
        return jsonify({"error": "access denied"}), 403

    return "", 204
