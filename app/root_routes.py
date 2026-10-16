
from flask import Blueprint, jsonify, request, send_from_directory

from .common import require_authorization

root_bp = Blueprint("root", __name__)

@root_bp.get("/")
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
    return send_from_directory(root_bp.root_path, "index.html")

@root_bp.route("/health", methods=["GET"])
def healthcheck():
    """
    Perform a health check of the recipe box API.
    ---
    tags:
      - Health Check HTML
    parameters:
      - name: type
        in: query
        type: string
        required: true
        enum: ['json', 'html']
        description: Choose the output format.
    responses:
      200:
        description: Success response containing the requested format
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                data:
                  type: string
            example:
              status: "success"
              data: "OK"
          text/plain:
            schema:
              type: string
            example: "<html><body><span>Recipe Box API Health: OK</span></body></html>"
      409:
        description: Failure response containing the requested format
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                data:
                  type: string
            example:
              status: "failure"
              data: "EXCEPTION"
          text/plain:
            schema:
              type: string
            example: "<html><body><span>Recipe Box API Health: EXCEPTION</span></body></html>"
    """
    from .common import get_db
    # Get parameter: provide a default value and cast the data type
    return_type = request.args.get('type', default="html", type=str)
    try:
        db = get_db()
        db.execute("SELECT 1 FROM recipes LIMIT 1")
    except Exception as e:  # noqa: BLE001
        if return_type == "html":
            return f"<html><body><span>Recipe Box API Health: {e}</span></body></html>", 409
        elif return_type == "json":
            return jsonify({"status": "failure", "data": f"{e}"}), 409
        else:
            return ""
    if return_type == "html":
        return "<html><body><span>Recipe Box API Health: OK</span></body></html>", 200
    elif return_type == "json":
        return jsonify({"status": "success", "data": "OK"}), 200
    else:
        return ""

@root_bp.route("/whoami", methods=["GET"])
@require_authorization
def whoami(**kwargs):
    """
    Endpoint to return the user ID of the currently authenticated user.
    ---
    tags:
    - Authentication
    security:
    - AuthKey: []  # <--- Tells Swagger to fetch the token from the lock box
    responses:
        200:
            description: The user ID of the currently authenticated user
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            user_id:
                                type: string
        401:
            description: Unauthorized (not logged in)
        403:
            description: Access denied (not the owner or an admin)
    """
    # Extract from kwargs
    user_id = kwargs.get('current_user_id')
    is_admin = kwargs.get('is_admin')
    # current_user = kwargs.get('current_user')

    return {"user_id": user_id, "is_admin": is_admin}, 200
