# app/recipe_routes.py
import asyncio
import json
import posixpath
import random
import time
from typing import Any, Optional
from urllib.parse import unquote_plus, urlparse

import httpx
from flask import Blueprint, current_app, jsonify, request

from app.extensions import cache, limiter
from app.middleware import require_authorization
from app.services.rating_service import rate_recipe_for_user
from app.services.recipe_service import (
    create_recipe_for_user,
    delete_recipe_for_user,
    get_recipe_for_user,
    list_recipes_for_user,
    update_recipe_for_user,
)

recipes_bp = Blueprint("recipes", __name__)

TIMEOUT_SECONDS = 0.5

class SafeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Exception):
            return f"{type(obj).__name__}: {obj!s}"
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

class Result:
    def __init__(self, id: int, status: str, elapsed_time: Optional[float],  # noqa: UP045
                 start: Optional[float] = None, end: Optional[float] = None,  # noqa: UP045
                 error: Optional[Any] = None, message: Optional[str] = None,  # noqa: UP045
                 data: Optional[list[Any]] = None):  # noqa: UP045
        self.id = id
        self.status = status
        self.start = start
        self.end = end
        self.elapsed_time = elapsed_time
        self.error = error
        self.message = message
        self.total_results = len(data) if data else None

        if data:
            # Convert internal objects if they have a serialization method
            self.data = [r.to_dict() if hasattr(r, 'to_dict') else r for r in data]
        else:
            self.data = None

    def to_dict(self) -> dict:
        """Converts to a dictionary, cleaning up exceptions."""
        return {
            "id": self.id,
            "status": self.status,
            "start": self.start,
            "end": self.end,
            "elapsed_time": self.elapsed_time,
            "error": f"{type(self.error).__name__}: {self.error!s}" if isinstance(self.error, Exception) else self.error,
            "message": self.message,
            "total_results": self.total_results,
            "data": self.data
        }

    def to_json(self) -> str:
        """Converts directly to a valid JSON string."""
        return json.dumps(self.to_dict(), cls=SafeEncoder)

@recipes_bp.get("/get_the_slow_service_again_like_we_have_done_50_times_now/<int:thread_id>")
async def slow_summary(thread_id: int, **kwargs):
    responses = []
    base_url = current_app.config["NUTRITION_SERVICE_BASE_URL"]
    url = f"{base_url}/nutrition/eggs"
    #  accepts client id or random
    if not thread_id:
        id = random.randint(1, 10000)
    else:
        id = thread_id
    #  start the timer
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        # debug
        print(f"[async_test-{id}]: fetching {url}")
        async with asyncio.timeout(TIMEOUT_SECONDS):
            responses = await asyncio.gather(
                client.get(url),
                client.get(url),
                client.get(url),
            )
        # responses = await asyncio.gather(
        #     client.get(url),
        #     client.get(url),
        #     client.get(url),
        # )
        # responses.append(await client.get(url))
        # responses.append(await client.get(url))
        # responses.append(await client.get(url))
    end = time.perf_counter()
    elapsed = end - start
    # debug
    print(
        f"[async_test-{id}]: status: 200, "
        f"elapsed time: {elapsed:.3f} seconds"
    )
    result =  Result(
        id=id,
        status=200,
        elapsed_time=f"{elapsed:.3f} seconds",
        data=[r.json() for r in responses],
    )
    return jsonify(result.to_json()), 200

@recipes_bp.get("/async_test/<int:thread_id>")
async def async_test(thread_id: int, **kwargs):
    base_url = current_app.config["NUTRITION_SERVICE_BASE_URL"]
    url = f"{base_url}/nutrition/eggs"
    #  accepts client id or random
    if not thread_id:
        id = random.randint(1, 10000)
    else:
        id = thread_id
    #  start the timer
    start = time.perf_counter()
    if current_app.debug:
        print("DEBUG: HITTING DB FOR /recipes")
    # user_id_str = kwargs.get("current_user_id")
    # is_admin = kwargs.get("is_admin")
    # recipes = list_recipes_for_user(user_id_str, is_admin)
    #  debug
    print(f"[async_test-{id}]: route hit")
    try:
        async with httpx.AsyncClient() as client:
            # debug
            print(f"[async_test-{id}]: fetching {url}")
            async with asyncio.timeout(TIMEOUT_SECONDS):
                responses = await asyncio.gather(
                    client.get(url),
                    client.get(url),
                    client.get(url),
                )
            # responses = await asyncio.gather(
            #     client.get(url),
            #     client.get(url),
            #     client.get(url),
            # )
        end = time.perf_counter()
        elapsed = end - start
        # debug
        print(
            f"[async_test-{id}]: status: 200, "
            f"elapsed time: {elapsed:.3f} seconds"
        )
        result =  Result(
            id=id,
            status=200,
            elapsed_time=f"{elapsed:.3f} seconds",
            data=[r.json() for r in responses],
        )
        return jsonify(result.to_json()), 200
    except asyncio.TimeoutError as texc:  # noqa: F841, UP041
        end = time.perf_counter()
        elapsed = end - start
        parsed_url = urlparse(url)
        path = parsed_url.path
        ingredient = unquote_plus(posixpath.basename(path))
        print(
            f"[async_test-{id}]: status: 408 (timeout), "
            f"elapsed time: {elapsed:.3f} seconds"
        )
        result =  Result(
            id=id,
            status=408,
            elapsed_time=f"{elapsed:.3f} seconds",
            error=f"timeout after {TIMEOUT_SECONDS} seconds",
            data=None
        )
        return jsonify(result.to_json()), 408
    except httpx.ConnectError as cexc:
        end = time.perf_counter()
        elapsed = end - start
        parsed_url = urlparse(url)
        path = parsed_url.path
        ingredient = unquote_plus(posixpath.basename(path))
        result =  Result(
            id=id,
            status=500,
            elapsed_time=f"{elapsed:.3f} seconds",
            error=str(cexc) + " " + str(cexc.request),
            data=None
        )
        return jsonify(result.to_json()), 500
    except Exception as exc:  # noqa: BLE001, F841
        end = time.perf_counter()
        elapsed = end - start
        parsed_url = urlparse(url)
        path = parsed_url.path
        ingredient = unquote_plus(posixpath.basename(path))  # noqa: F841
        if responses:
          result =  Result(
              id=id,
              status=500,
              elapsed_time=f"{elapsed:.3f} seconds",
              data=[r.json() for r in responses] if responses else None
          )
        else:
          result =  Result(
              id=id,
              status=500,
              elapsed_time=f"{elapsed:.3f} seconds",
              data=None
          )
        return jsonify(result.to_json()), 500


@recipes_bp.get("/")
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
    if current_app.debug:
        print("DEBUG: HITTING DB FOR /recipes")
    user_id_str = kwargs.get("current_user_id")
    is_admin = kwargs.get("is_admin")
    recipes = list_recipes_for_user(user_id_str, is_admin)
    return jsonify(recipes), 200

@recipes_bp.get("/<int:recipe_id>")
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
    user_id_str = kwargs.get("current_user_id")
    is_admin = kwargs.get("is_admin")

    recipe = get_recipe_for_user(recipe_id, user_id_str, is_admin)
    if recipe is None:
        return jsonify({"error": "recipe not found"}), 404
    return jsonify(recipe), 200

@recipes_bp.post("/")
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
      401:
        description: Unauthorized (not logged in)
      403:
        description: Access denied (not logged in)
      409:
        description: A recipe with the same title already exists
    """
    user_id_str = kwargs.get("current_user_id")
    data = request.get_json(silent=True)

    if not data or not data.get("title") or not data.get("ingredients"):
        return jsonify({"error": "title and ingredients are required"}), 400

    recipe, error = create_recipe_for_user(user_id_str, data)
    if error:
        return jsonify({"error": error}), 409

    # if the create_recipe succeeds then delete cached entry for the list_recipes route
    if current_app.debug:
        print("DEBUG: deleting cache for list_recipes")
    cache.delete_memoized(list_recipes)
    return jsonify(recipe), 201

@recipes_bp.patch("/<int:recipe_id>")
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
      401:
        description: Unauthorized (not logged in)
      403:
        description: Access denied (not the owner or an admin)
      404:
        description: Recipe not found
      409:
        description: A recipe with the same title already exists
    """
    user_id_str = kwargs.get("current_user_id")
    is_admin = kwargs.get("is_admin")

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "a JSON body is required"}), 400

    recipe, error = update_recipe_for_user(recipe_id, user_id_str, is_admin, data)

    if error == "recipe_not_found":
        return jsonify({"error": "recipe not found"}), 404
    if error == "access_denied":
        return jsonify({"error": "access denied"}), 403
    if error == "nothing_to_update":
        return jsonify({"error": "nothing to update"}), 400
    if error == "duplicate_title":
        return jsonify({"error": "a recipe with that title already exists"}), 409

    # if the update_recipe succeeds then delete cached entry for the list_recipes route
    if current_app.debug:
        print("DEBUG: deleting cache for list_recipes")
    cache.delete_memoized(list_recipes)
    return jsonify(recipe), 200

@recipes_bp.delete("/<int:recipe_id>")
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
      401:
        description: Unauthorized (not logged in)
      403:
        description: Access denied (not the owner or an admin)
      404:
        description: Recipe not found
    """
    user_id_str = kwargs.get("current_user_id")
    is_admin = kwargs.get("is_admin")

    error = delete_recipe_for_user(recipe_id, user_id_str, is_admin)

    if error == "recipe_not_found":
        return jsonify({"error": "recipe not found"}), 404
    if error == "access_denied":
        return jsonify({"error": "access denied"}), 403

    # if the delete_recipe succeeds then delete cached entry for the list_recipes route
    if current_app.debug:
        print("DEBUG: deleting cache for list_recipes")
    cache.delete_memoized(list_recipes)
    return "", 204

@recipes_bp.post("/<int:recipe_id>/ratings")
@require_authorization
def rate_recipe(recipe_id, **kwargs):
    """
    Rate a recipe by its ID.
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
            score:
              type: integer
              minimum: 1
              maximum: 5
    responses:
      200:
        description: Rating updated successfully
      400:
        description: Invalid request body
      401:
        description: Unauthorized (not logged in)
    """
    user_id_str = kwargs.get("current_user_id")
    # is_admin = kwargs.get("is_admin")

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "a JSON body is required"}), 400

    try:
      score = int(data["score"])
    except:  # noqa: E722
        return jsonify({"error": "score must be a number"}), 400

    rating, error = rate_recipe_for_user(recipe_id, int(user_id_str), score)

    if error == "nothing_to_update":
        return jsonify({"error": "nothing to update"}), 400
    if error == "unknown error":
        return jsonify({"error": "an unidentified error occurred"}), 500

    return jsonify(rating), 200