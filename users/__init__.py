# users/__init__.py
from flasgger import Swagger
from flask import Flask, g, jsonify
from flask_jwt_extended import (
    JWTManager,
)

from users.config import DevelopmentConfig, ProductionConfig, TestingConfig
from users.routes_auth import auth_bp
from users.routes_root import root_bp


def create_app(config_name="development"):
    print("User application starting...")
    user_app = Flask(__name__)

    config_classes = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }
    user_app.config.from_object(config_classes[config_name])

    # Fetch variables from environment
    DEBUG                      = user_app.config["DEBUG"]
    JSON_SORT_KEYS             = user_app.config["JSON_SORT_KEYS"]

    BASE_DIR                   = user_app.config["BASE_DIR"]
    DATABASE                   = user_app.config["DATABASE"]
    SQLALCHEMY_DATABASE_URI    = user_app.config["SQLALCHEMY_DATABASE_URI"]

    CACHE_TYPE                 = user_app.config["CACHE_TYPE"]
    CACHE_DEFAULT_TIMEOUT      = user_app.config["CACHE_DEFAULT_TIMEOUT"]

    GATEWAY_SERVICE_BASE_URL   = user_app.config["GATEWAY_SERVICE_BASE_URL"]
    USER_SERVICE_BASE_URL      = user_app.config["USER_SERVICE_BASE_URL"]
    RECIPE_SERVICE_BASE_URL    = user_app.config["RECIPE_SERVICE_BASE_URL"]
    NUTRITION_SERVICE_BASE_URL = user_app.config["NUTRITION_SERVICE_BASE_URL"]

    user_app.json.sort_keys = JSON_SORT_KEYS
    user_app.json.sort_keys = False

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
    from users.extensions import cache, limiter, migrate, user_db
    from users.models.users import User

    print("Initializing SQLAchemy...")
    user_db.init_app(user_app)
    print("    enabling migrations...")
    migrate.init_app(user_app, user_db)
    print("    enabling caching...")
    cache.init_app(user_app)
    print("    enabling limiter...")
    limiter.init_app(user_app)

    print("Registering Blueprints...")
    user_app.register_blueprint(root_bp)
    user_app.register_blueprint(auth_bp, url_prefix="/auth")

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
            }
        }
    }
    print("Initializing Swagger Docs...")
    swagger = Swagger(user_app, template=swagger_data)  # noqa: F841
    print("Initializing JWT Manager...")
    jwt_manager = JWTManager(user_app)  # noqa: F841

    # Custom error handler for when a user exceeds their limit
    @user_app.errorhandler(429)
    def ratelimit_handler(e: Exception):
        return jsonify({
            "error": "Rate limit exceeded",
            "description": str(e.description)
        }), 429

    @user_app.teardown_appcontext
    def close_db(exception: Exception):
        user_db = g.pop("user_db", None)
        if user_db is not None:
            user_db.close()

    @user_app.shell_context_processor
    def make_shell_context():
        return {"user_db": user_db, "User": User}

    return user_app
