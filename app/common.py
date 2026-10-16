import sqlite3
from functools import wraps

from flask import current_app, g, jsonify
from flask_jwt_extended import (
    get_jwt,
    get_jwt_identity,
    jwt_required,
)


def get_db():
    if "db" not in g:
        db_path = current_app.config["DATABASE"]
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

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

def require_authorization(f):
    print("require_authorization DECORATOR APPLIED to", f.__name__)
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