# recipes/__init__.py
from dotenv import load_dotenv  # noqa: F401
from flasgger import Swagger
from flask import Flask, g, jsonify
from flask_jwt_extended import (
    JWTManager,
)

from recipes.config import DevelopmentConfig, ProductionConfig, TestingConfig
from recipes.routes_recipe import recipes_bp
from recipes.routes_root import root_bp


def create_app(config_name="development"):
    print("Recipe Application API starting...")
    recipe_app = Flask(__name__)

    config_classes = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }
    recipe_app.config.from_object(config_classes[config_name])

    # Fetch variables from environment
    DEBUG                      = recipe_app.config["DEBUG"]
    JSON_SORT_KEYS             = recipe_app.config["JSON_SORT_KEYS"]

    BASE_DIR                   = recipe_app.config["BASE_DIR"]
    DATABASE                   = recipe_app.config["DATABASE"]
    SQLALCHEMY_DATABASE_URI    = recipe_app.config["SQLALCHEMY_DATABASE_URI"]

    CACHE_TYPE                 = recipe_app.config["CACHE_TYPE"]
    CACHE_DEFAULT_TIMEOUT      = recipe_app.config["CACHE_DEFAULT_TIMEOUT"]

    GATEWAY_SERVICE_BASE_URL   = recipe_app.config["GATEWAY_SERVICE_BASE_URL"]
    USER_SERVICE_BASE_URL      = recipe_app.config["USER_SERVICE_BASE_URL"]
    RECIPE_SERVICE_BASE_URL    = recipe_app.config["RECIPE_SERVICE_BASE_URL"]
    NUTRITION_SERVICE_BASE_URL = recipe_app.config["NUTRITION_SERVICE_BASE_URL"]

    recipe_app.json.sort_keys = JSON_SORT_KEYS
    recipe_app.json.sort_keys = False

    print(f"Environment                      = {config_name}")
    print(f"    DEBUG                        = {DEBUG}")
    print(f"    JSON_SORT_KEYS               = {JSON_SORT_KEYS}")

    print(f"    BASE_DIR                     = {BASE_DIR}")
    print(f"    DATABASE                     = {DATABASE}")
    print(f"    SQLALCHEMY_DATABASE_URI      = {SQLALCHEMY_DATABASE_URI}")

    print(f"    CACHE_TYPE                   = {CACHE_TYPE}")
    print(f"    CACHE_DEFAULT_TIMEOUT        = {CACHE_DEFAULT_TIMEOUT}")

    print(f"    GATEWAY_SERVICE_BASE_URL     = {GATEWAY_SERVICE_BASE_URL}")
    print(f"    USER_SERVICE_BASE_URL        = {USER_SERVICE_BASE_URL}")
    print(f"    RECIPE_SERVICE_BASE_URL      = {RECIPE_SERVICE_BASE_URL}")
    print(f"    NUTRITION_SERVICE_BASE_URL   = {NUTRITION_SERVICE_BASE_URL}")

    # init SQLAlchemy, migarations, and cache
    from recipes.extensions import cache, limiter, migrate, recipe_db
    from recipes.models.recipes import Recipe

    print("Initializing SQLAchemy...")
    recipe_db.init_app(recipe_app)
    print("    enabling migrations...")
    migrate.init_app(recipe_app, recipe_db)
    print("    enabling caching...")
    cache.init_app(recipe_app)
    print("    enabling limiter...")
    limiter.init_app(recipe_app)

    print("Registering Blueprints...")
    recipe_app.register_blueprint(root_bp)
    recipe_app.register_blueprint(recipes_bp, url_prefix="/recipes")

    # The securityDefinition below is used by Swagger to describe the
    # authentication mechanism for the API.
    # It creates the Authorize button and input box in the Swagger interface,
    # allowing users to input their JWT token for authenticated requests.
    swagger_data = {
        "swagger": "2.0",
        "info": {
            "title": "Recipe Book API",
            "version": "1.0.0"
        },
        "securityDefinitions": {
            "AuthKey": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Enter your JWT token with the 'Bearer' prefix. Example: 'Bearer eyJhbGciOi...'"
            },
            "InternalTokenAuth": {
                "type": "apiKey",
                "name": "X-Internal-Token",
                "in": "header",
                "description": "Enter your internal security token. Example: 'XSWT-sdfgkfd...'"
            }
        }
    }
    print("Initializing Swagger Docs...")
    swagger = Swagger(recipe_app, template=swagger_data)  # noqa: F841
    print("Initializing JWT Manager...")
    jwt_manager = JWTManager(recipe_app)  # noqa: F841

    # Custom error handler for when a user exceeds their limit
    @recipe_app.errorhandler(429)
    def ratelimit_handler(e: Exception):
        return jsonify({
            "error": "Rate limit exceeded",
            "description": str(e.description)
        }), 429

    @recipe_app.teardown_appcontext
    def close_db(exception: Exception):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @recipe_app.shell_context_processor
    def make_shell_context():
        return {"db": recipe_db, "Recipe": Recipe}

    return recipe_app