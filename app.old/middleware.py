# app/middleware.py
from functools import wraps

from flask import current_app
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required


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

        # Pull data directly out of the validated token payload
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get("is_admin", False)

        # Inject the context variables as keyword arguments into the route
        return f(
            current_user_id=current_user_id,
            is_admin=is_admin,
            *args, **kwargs  # noqa: B026
        )
    return decorated_function
