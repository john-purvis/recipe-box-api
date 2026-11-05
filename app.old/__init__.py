# app/__init__.py
from dotenv import load_dotenv  # noqa: F401
from flasgger import Swagger
from flask import Flask, g, jsonify
from flask_jwt_extended import (
    JWTManager,
)

from app.config import DevelopmentConfig, ProductionConfig, TestingConfig
from app.routes_recipe import recipes_bp
from app.routes_root import root_bp


def create_app(config_name="development"):
    print("Application starting...")
    app = Flask(__name__)

    config_classes = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }
    app.config.from_object(config_classes[config_name])

    # Fetch variables from environment
    DEBUG                      = app.config["DEBUG"]
    JSON_SORT_KEYS             = app.config["JSON_SORT_KEYS"]
    BASE_DIR                   = app.config["BASE_DIR"]
    DATABASE                   = app.config["DATABASE"]
    SQLALCHEMY_DATABASE_URI    = app.config["SQLALCHEMY_DATABASE_URI"]
    CACHE_TYPE                 = app.config["CACHE_TYPE"]
    CACHE_DEFAULT_TIMEOUT      = app.config["CACHE_DEFAULT_TIMEOUT"]
    NUTRITION_SERVICE_BASE_URL = app.config["NUTRITION_SERVICE_BASE_URL"]

    app.json.sort_keys = JSON_SORT_KEYS
    app.json.sort_keys = False

    print(f"Environment                      = {config_name}")
    print(f"    DEBUG                        = {DEBUG}")
    print(f"    BASE_DIR                     = {BASE_DIR}")
    print(f"    JSON_SORT_KEYS               = {JSON_SORT_KEYS}")
    print(f"    DATABASE                     = {DATABASE}")
    print(f"    SQLALCHEMY_DATABASE_URI      = {SQLALCHEMY_DATABASE_URI}")
    print(f"    CACHE_TYPE                   = {CACHE_TYPE}")
    print(f"    CACHE_DEFAULT_TIMEOUT        = {CACHE_DEFAULT_TIMEOUT}")
    print(f"    NUTRITION_SERVICE_BASE_URL   = {NUTRITION_SERVICE_BASE_URL}")

    # init SQLAlchemy, migarations, and cache
    from app.extensions import cache, dba, limiter, migrate
    from app.models.recipes import Recipe

    print("Initializing SQLAchemy...")
    dba.init_app(app)
    print("    enabling migrations...")
    migrate.init_app(app, dba)
    print("    enabling caching...")
    cache.init_app(app)
    print("    enabling limiter...")
    limiter.init_app(app)

    print("Registering Blueprints...")
    app.register_blueprint(root_bp)
    app.register_blueprint(recipes_bp, url_prefix="/recipes")

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
    swagger = Swagger(app, template=swagger_data)  # noqa: F841
    print("Initializing JWT Manager...")
    jwt_manager = JWTManager(app)  # noqa: F841

    # Custom error handler for when a user exceeds their limit
    @app.errorhandler(429)
    def ratelimit_handler(e: Exception):
        return jsonify({
            "error": "Rate limit exceeded",
            "description": str(e.description)
        }), 429

    @app.teardown_appcontext
    def close_db(exception: Exception):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @app.shell_context_processor
    def make_shell_context():
        return {"db": dba, "Recipe": Recipe}

    return app