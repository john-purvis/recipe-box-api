# app/middleware.py
from functools import wraps

from flask import current_app, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.db import user_to_dict
from app.models.recipes import User


def require_authorization(f):
    """
    Custom decorator that bundles Flask-JWT-Extended authentication
    and automatically injects user context arguments into the route
    for authorization checks.
    """
    @wraps(f)
    @jwt_required()  # Automatically catches expired/invalid tokens
    def decorated_function(*args, **kwargs):
        if current_app.debug:
            print("DEBUG: require_authorization CALLED for", f.__name__)

        # 1. Pull data directly out of the validated token payload
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get("is_admin", False)

        # 2. Fetch the fresh user row from the database
        user = (
            User.query
            .filter(
                User.id == current_user_id
            )
            .first()
        )

        if not user:
            return jsonify({'message': 'User profile no longer exists'}), 404

        # 3. Inject the context variables as keyword arguments into the route
        return f(
            current_user_id=current_user_id,
            is_admin=is_admin,
            current_user=user_to_dict(user),
            *args, **kwargs  # noqa: B026
        )
    return decorated_function