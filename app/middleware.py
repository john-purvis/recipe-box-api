# app/middleware.py
from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from .db import get_db


def require_authorization(f):
    """
    Custom decorator that bundles Flask-JWT-Extended authentication
    and automatically injects user context arguments into the route
    for authorization checks.
    """
    @wraps(f)
    @jwt_required()  # Automatically catches expired/invalid tokens
    def decorated_function(*args, **kwargs):
        print("require_authorization CALLED for", f.__name__)

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