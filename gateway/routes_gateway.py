# gateway/root_routes.py

import asyncio

import httpx
import requests
from flask import Blueprint, current_app, jsonify, request

from gateway.extensions import cache, limiter
from gateway.middleware import require_authorization

gateway_bp = Blueprint("gateway", __name__)

def httpx_sync_get(url: str):
    if not url:
        print("[Gateway][Error] No URL parameter")
        return jsonify({"error": "No URL parameter"}), 500

     # auth header token
    auth_header = request.headers.get("Authorization", None)
    auth_token_type, auth_token = auth_header.split(" ")  # noqa: RUF059

    # internal security token
    itkn = current_app.config["INTERNAL_SERVICE_TOKEN"]
    if not itkn and current_app.debug:
        print("[Gateway][Error] Internal token not in configuration !!!")
        return jsonify({"error": "Server configuration error"}), 500

    # create request header(s)
    if auth_token:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "X-Internal-Token": "XSWT-" + itkn
        }
    else:
        headers = {
            "Content-Type": "application/json",
            "X-Internal-Token": "XSWT-" + itkn
        }

    try:
        # Make the synchronous HTTP GET request
        # timeout=5 ensures the Flask app won't hang indefinitely if the external site is slow
        response = requests.get(url, headers=headers, timeout=5)

        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        # Parse the JSON response from the external site
        data = response.json()
        return jsonify({"status": "success", "data": data}), 200

    except requests.exceptions.Timeout:
        if current_app.debug:
            print(f"[Gateway][Error] Time out calling {url}")
        return jsonify({"error": "The request to the external server timed out"}), 504
    except requests.exceptions.HTTPError as err:
        if current_app.debug:
            print(f"[Gateway][Error] HTTP error calling {url}: {err}")
        return jsonify({"error": f"HTTP error occurred: {err}"}), response.status_code
    except requests.exceptions.RequestException as err:
        if current_app.debug:
            print(f"[Gateway][Error] An error occurred calling {url}: {err}")
        return jsonify({"error": f"An error occurred: {err}"}), 500

@gateway_bp.get("/relay")
def relay():
    """
    Just gets the user service homepage and sends it back as a test
    ---
    tags:
    - User Service Home
    responses:
        200:
            description: The homepage of the Recipe Box Users API
            content:
            text/html:
                schema:
                type: string
                example: "<html><body><h1>Welcome to the Recipe Box API</h1></body></html>"
    """
    # auth header token
    auth_header = request.headers.get("Authorization", None)
    auth_token_type, auth_token = auth_header.split(" ") if auth_header else None, None  # noqa: F841

    # internal security token
    itkn = current_app.config["INTERNAL_SERVICE_TOKEN"]
    if not itkn and current_app.debug:
        print("[Gateway][Error] Internal token not in configuration !!!")
        return jsonify({"error": "Server configuration error"}), 500

    # create request header(s)
    if auth_token:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "X-Internal-Token": "XSWT-" + itkn
        }
    else:
        headers = {
            "Content-Type": "application/json",
            "X-Internal-Token": "XSWT-" + itkn
        }

    # get the payload (username and pwd)
    payload = request.get_json(silent=True)  # noqa: F841

    # construct the user service url
    user_service_base = current_app.config["USER_SERVICE_BASE_URL"]
    user_service_url = f"{user_service_base}/"

    try:
      # Use a client session to execute the POST request
      with httpx.Client() as client:
          response = client.get(user_service_url, headers=headers, timeout=5)

          # Let all errors pass thru except server timeout
          if response.status_code == 504:
            response.raise_for_status()

          # Relay the content back to whoever called you
          return response.content

    except requests.exceptions.Timeout:
        if current_app.debug:
            print(f"[Gateway][Error] Time out calling {user_service_url}")
        return jsonify({"error": "The request to the users service timed out"}), 504
    except requests.exceptions.HTTPError as err:
        if current_app.debug:
            print(f"[Gateway][Error] HTTP error calling {user_service_url}: {err}")
        return jsonify({"error": f"HTTP error occurred: {err}"}), response.status_code
    except requests.exceptions.RequestException as err:
        if current_app.debug:
            print(f"[Gateway][Error] An error occurred calling {user_service_url}: {err}")
        return jsonify({"error": f"An error occurred: {err}"}), 500


@gateway_bp.post("/login")
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
    auth_url = current_app.config["USER_SERVICE_BASE_URL"] + "/login"
    payload = request.get_json() or {}

    with httpx.Client() as client:
        resp = client.post(auth_url, json=payload, timeout=5)

    return jsonify(resp.json()), resp.status_code


# @gateway_bp.post("/login")
# @limiter.limit("3 per minute")
# def login():
#     """
#     User login endpoint that authenticates a user and returns a JWT token.
#     ---
#     tags:
#       - Login / Logout
#     parameters:
#       - name: body
#         in: body
#         required: true
#         schema:
#           type: object
#           properties:
#             username:
#               type: string
#             password:
#               type: string
#     responses:
#       200:
#         description: Login successful, returns a JWT token
#       400:
#         description: Missing credentials
#       401:
#         description: Invalid username or password
#     """
#     # auth header token
#     auth_header = request.headers.get("Authorization", None)
#     auth_token_type, auth_token = auth_header.split(" ") if auth_header else None, None

#     # internal security token
#     itkn = current_app.config["INTERNAL_SERVICE_TOKEN"]
#     if not itkn and current_app.debug:
#         print("[Gateway][Error] Internal token not in configuration !!!")
#         return jsonify({"error": "Server configuration error"}), 500

#     # create request header(s)
#     if auth_token:
#         headers = {
#             "Authorization": f"Bearer {auth_token}",
#             "Content-Type": "application/json",
#             "X-Internal-Token": "XSWT-" + itkn
#         }
#     else:
#         headers = {
#             "Content-Type": "application/json",
#             "X-Internal-Token": "XSWT-" + itkn
#         }

#     # get the payload (username and pwd)
#     data = request.get_json()

#     # construct the user service url
#     user_service_base = current_app.config["USER_SERVICE_BASE_URL"]
#     user_service_url = f"{user_service_base}/login"

#     try:
#       # Use a client session to execute the POST request
#       with httpx.Client() as client:
#           response = client.post(user_service_url, headers=headers, json=data, timeout=5)

#           # Raise an exception for 4xx/5xx errors if needed
#           response.raise_for_status()

#           # Relay the JSON answer back to whoever called you
#           return response.json()

#     except requests.exceptions.Timeout:
#         if current_app.debug:
#             print(f"[Gateway][Error] Time out calling {user_service_url}")
#         return jsonify({"error": "The request to the external server timed out"}), 504
#     except requests.exceptions.HTTPError as err:
#         if current_app.debug:
#             print(f"[Gateway][Error] HTTP error calling {user_service_url}: {err}")
#         return jsonify({"error": f"HTTP error occurred: {err}"}), response.status_code
#     except requests.exceptions.RequestException as err:
#         if current_app.debug:
#             print(f"[Gateway][Error] An error occurred calling {user_service_url}: {err}")
#         return jsonify({"error": f"An error occurred: {err}"}), 500


@gateway_bp.post('/logout')
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
    auth_token = kwargs.get("auth_token")  # noqa: F841
    user_id_str = kwargs.get("current_user_id")  # noqa: F841
    is_admin = kwargs.get("is_admin")  # noqa: F841

    return jsonify({
        "message": "Logout successful. Please delete your token on the client."
    }), 200



@gateway_bp.get("/me")
# @require_authorization
async def me(**kwargs):
    # auth_token = kwargs.get("auth_token")  # noqa: F841
    # user_id_str = kwargs.get("current_user_id")  # noqa: F841
    # is_admin = kwargs.get("is_admin")  # noqa: F841

    # auth_header = request.headers.get("Authorization")
    # headers = {"Authorization": auth_header} if auth_header else {}

    # auth header token
    auth_header = request.headers.get("Authorization", None)
    auth_token_type, auth_token = tuple(auth_header.split(" ")) if auth_header else tuple(None, None)  # noqa: RUF059

    # internal security token
    itkn = current_app.config["INTERNAL_SERVICE_TOKEN"]
    if not itkn and current_app.debug:
        print("[Gateway][Error] Internal token not in configuration !!!")
        return jsonify({"error": "Server configuration error"}), 500

    # create request header(s)
    if auth_token:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "X-Internal-Token": "XSWT-" + itkn
        }
    else:
        headers = {
            "Content-Type": "application/json",
            "X-Internal-Token": "XSWT-" + itkn
        }

    user_url = current_app.config["USER_SERVICE_BASE_URL"] + "/me"
    recipes_url = current_app.config["RECIPE_SERVICE_BASE_URL"] + "/recipes/"
    nutrition_url = current_app.config["NUTRITION_SERVICE_BASE_URL"] + "/summary"

    async with httpx.AsyncClient(timeout=3.0) as client:
        async def get_user():
            try:
                r = await client.get(user_url, headers=headers)
                r.raise_for_status()
                return {"ok": True, "data": r.json()}
            except Exception as ex1:  # noqa: BLE001
                return {"ok": False, "data": None}

        async def get_recipes():
            try:
                r = await client.get(recipes_url, headers=headers)
                r.raise_for_status()
                return {"ok": True, "data": r.json()}
            except Exception as ex2:  # noqa: BLE001
                return {"ok": False, "data": None}

        async def get_nutrition():
            try:
                r = await client.get(nutrition_url, headers=headers)
                r.raise_for_status()
                return {"ok": True, "data": r.json()}
            except Exception as ex3:  # noqa: BLE001
                return {"ok": False, "data": None}

        user_res, recipes_res, nutrition_res = await asyncio.gather(
            get_user(), get_recipes(), get_nutrition(), return_exceptions=False
        )

    missing = []
    if not user_res["ok"]:
        missing.append("user")
    if not recipes_res["ok"]:
        missing.append("recipes")
    if not nutrition_res["ok"]:
        missing.append("nutrition")

    body = {
        "complete": len(missing) == 0,
        "missing": missing,
        "user": user_res["data"],
        "recipes": recipes_res["data"],
        "nutrition": nutrition_res["data"],
    }

    status = 200 if user_res["ok"] else 207  # 207 = multi-status / partial
    return jsonify(body), status


@gateway_bp.get("/recipes")
@require_authorization
@cache.memoize(timeout=30)
@limiter.exempt # Completely bypasses all rate limits
def list_recipes(**kwargs):
    """
    List all recipes.
    ---
    tags:
      - Recipes
    security:
      - AuthKey: []  # <--- Tells Swagger to fetch the token from the lock box
      - InternalTokenAuth: []  # Requires both security requirements to be met
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
    # auth header token
    auth_header = request.headers.get("Authorization", None)
    auth_token_type, auth_token = tuple(auth_header.split(" ")) if auth_header else tuple(None, None)  # noqa: RUF059

    # internal security token
    itkn = current_app.config["INTERNAL_SERVICE_TOKEN"]
    if not itkn and current_app.debug:
        print("[Gateway][Error] Internal token not in configuration !!!")
        return jsonify({"error": "Server configuration error"}), 500

    # create request header(s)
    if auth_token:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "X-Internal-Token": "XSWT-" + itkn
        }
    else:
        headers = {
            "Content-Type": "application/json",
            "X-Internal-Token": "XSWT-" + itkn
        }

    # get the payload
    payload = request.get_json(silent=True)  # noqa: F841

    # construct the user service url
    recipe_service_base = current_app.config["RECIPE_SERVICE_BASE_URL"]
    recipe_service_url = f"{recipe_service_base}/recipes/"

    try:
      # Use a client session to execute the POST request
      with httpx.Client() as client:
          response = client.get(recipe_service_url, headers=headers, timeout=5)

          # Let all errors pass thru except server timeout
          if response.status_code == 504:
            response.raise_for_status()

          # Relay the content back to whoever called you
          return response.content

    except requests.exceptions.Timeout:
        if current_app.debug:
            print(f"[Gateway][Error] Time out calling {recipe_service_url}")
        return jsonify({"error": "The request to the recipe service timed out"}), 504
    except requests.exceptions.HTTPError as err:
        if current_app.debug:
            print(f"[Gateway][Error] HTTP error calling {recipe_service_url}: {err}")
        return jsonify({"error": f"HTTP error occurred: {err}"}), response.status_code
    except requests.exceptions.RequestException as err:
        if current_app.debug:
            print(f"[Gateway][Error] An error occurred calling {recipe_service_url}: {err}")
        return jsonify({"error": f"An error occurred: {err}"}), 500


@gateway_bp.get("/recipes/<int:recipe_id>")
@require_authorization
@limiter.exempt # Completely bypasses all rate limits
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
    # auth header token
    auth_header = request.headers.get("Authorization", None)
    auth_token_type, auth_token = tuple(auth_header.split(" ")) if auth_header else tuple(None, None)  # noqa: RUF059

    # internal security token
    itkn = current_app.config["INTERNAL_SERVICE_TOKEN"]
    if not itkn and current_app.debug:
        print("[Gateway][Error] Internal token not in configuration !!!")
        return jsonify({"error": "Server configuration error"}), 500

    # create request header(s)
    if auth_token:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "X-Internal-Token": "XSWT-" + itkn
        }
    else:
        headers = {
            "Content-Type": "application/json",
            "X-Internal-Token": "XSWT-" + itkn
        }

    # get the payload
    payload = request.get_json(silent=True)  # noqa: F841

    # construct the user service url
    recipe_service_base = current_app.config["RECIPE_SERVICE_BASE_URL"]
    recipe_service_url = f"{recipe_service_base}/recipes/{recipe_id}"

    try:
      # Use a client session to execute the POST request
      with httpx.Client() as client:
          response = client.get(recipe_service_url, headers=headers, timeout=5)

          # Let all errors pass thru except server timeout
          if response.status_code == 504:
            response.raise_for_status()

          # Relay the content back to whoever called you
          return response.content

    except requests.exceptions.Timeout:
        if current_app.debug:
            print(f"[Gateway][Error] Time out calling {recipe_service_url}")
        return jsonify({"error": "The request to the recipe service timed out"}), 504
    except requests.exceptions.HTTPError as err:
        if current_app.debug:
            print(f"[Gateway][Error] HTTP error calling {recipe_service_url}: {err}")
        return jsonify({"error": f"HTTP error occurred: {err}"}), response.status_code
    except requests.exceptions.RequestException as err:
        if current_app.debug:
            print(f"[Gateway][Error] An error occurred calling {recipe_service_url}: {err}")
        return jsonify({"error": f"An error occurred: {err}"}), 500