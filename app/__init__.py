from flasgger import Swagger
from flask import Flask, g
from flask_jwt_extended import (
  JWTManager,
)

from .auth_routes import auth_bp
from .config import DevelopmentConfig, ProductionConfig, TestingConfig
from .recipe_routes import recipes_bp
from .root_routes import root_bp


def create_app(config_name="development"):
  app = Flask(__name__)

  config_classes = {
      "development": DevelopmentConfig,
      "testing": TestingConfig,
      "production": ProductionConfig,
  }
  app.config.from_object(config_classes[config_name])

  from .db import init_db
  init_db(app)

  # Fetch variables from environment fallback to strings if missing
  JSON_SORT_KEYS = app.config["JSON_SORT_KEYS"]
  PYTHON_DEBUG   = app.config["PYTHON_DEBUG"]  # noqa: F841
  FLASK_DEBUG    = app.config["FLASK_DEBUG"]  # noqa: F841
  DATABASE       = app.config["DATABASE"]  # noqa: F841

  app.json.sort_keys = JSON_SORT_KEYS

  # app.register_blueprint(auth_bp)
  # app.register_blueprint(recipes_bp)
  app.register_blueprint(root_bp)
  app.register_blueprint(auth_bp, url_prefix="/auth")
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

  swagger = Swagger(app, template=swagger_data)  # noqa: F841
  jwt_manager = JWTManager(app)  # noqa: F841

  @app.teardown_appcontext
  def close_db(exception):
      print("DB close called inside app teardown")
      db = g.pop("db", None)
      if db is not None:
          db.close()

  return app