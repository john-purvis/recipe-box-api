# nutrition/middleware.py
from functools import wraps

from flask import current_app, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required


def verify_internal_token():
    token = request.headers.get("X-Internal-Token")
    if token is None:
        return jsonify({"error": "missing_internal_token"}), 401

    actual_token = token.replace("XSWT-", "", 1)

    expected = current_app.config.get("INTERNAL_SERVICE_TOKEN")
    if not expected or actual_token != expected:
        return jsonify({"error": "invalid_internal_token"}), 401

    return None  # means "ok"

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
