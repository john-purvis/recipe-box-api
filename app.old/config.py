# app/config.py
import os
from pathlib import Path


class Config:
    key = os.environ.get("JWT_SECRET_KEY")
    if not key:
        raise RuntimeError("JWT_SECRET_KEY environment variable is required")
    JWT_SECRET_KEY = key
    JSON_SORT_KEYS = bool(os.environ.get("JSON_SORT_KEYS", "False"))
    INTERNAL_SERVICE_TOKEN = os.environ.get("INTERNAL_SERVICE_TOKEN")
class DevelopmentConfig(Config):
    DEBUG = os.environ.get("DEV_DEBUG") == "True"
    db_name = os.environ.get("DEV_RECIPE_DATABASE")
    if not db_name:
        raise RuntimeError("DEV_RECIPE_DATABASE environment variable is required")
    # Force absolute path to the root recipes.db, ignoring any instance logic
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATABASE = BASE_DIR / db_name
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = os.environ.get("DEV_CACHE_TYPE")
    CACHE_DEFAULT_TIMEOUT = os.environ.get("DEV_CACHE_DEFAULT_TIMEOUT")
    GATEWAY_SERVICE_BASE_URL = os.environ.get("DEV_GATEWAY_SERVICE_BASE_URL")
    USER_SERVICE_BASE_URL = os.environ.get("DEV_USER_SERVICE_BASE_URL")
    RECIPE_SERVICE_BASE_URL = os.environ.get("DEV_RECIPE_SERVICE_BASE_URL")
    NUTRITION_SERVICE_BASE_URL = os.environ.get("DEV_NUTRITION_SERVICE_BASE_URL")
class TestingConfig(Config):
    DEBUG = os.environ.get("TST_DEBUG") == "True"
    db_name = os.environ.get("TST_RECIPE_DATABASE")
    if not db_name:
        raise RuntimeError("TST_RECIPE_DATABASE environment variable is required")
    # Force absolute path to the root recipes.db, ignoring any instance logic
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATABASE = BASE_DIR / db_name
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = os.environ.get("TST_CACHE_TYPE")
    CACHE_DEFAULT_TIMEOUT = os.environ.get("TST_CACHE_DEFAULT_TIMEOUT")
    GATEWAY_SERVICE_BASE_URL = os.environ.get("TST_GATEWAY_SERVICE_BASE_URL")
    USER_SERVICE_BASE_URL = os.environ.get("TST_USER_SERVICE_BASE_URL")
    RECIPE_SERVICE_BASE_URL = os.environ.get("TST_RECIPE_SERVICE_BASE_URL")
    NUTRITION_SERVICE_BASE_URL = os.environ.get("TST_NUTRITION_SERVICE_BASE_URL")
class ProductionConfig(Config):
    DEBUG = os.environ.get("PRD_DEBUG") == "False"
    db_name = os.environ.get("PRD_RECIPE_DATABASE")
    if not db_name:
        raise RuntimeError("PRD_RECIPE_DATABASE environment variable is required")
    # Force absolute path to the root recipes.db, ignoring any instance logic
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATABASE = BASE_DIR / db_name
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = os.environ.get("PRD_CACHE_TYPE")
    CACHE_DEFAULT_TIMEOUT = os.environ.get("PRD_CACHE_DEFAULT_TIMEOUT")
    GATEWAY_SERVICE_BASE_URL = os.environ.get("PRD_GATEWAY_SERVICE_BASE_URL")
    USER_SERVICE_BASE_URL = os.environ.get("PRD_USER_SERVICE_BASE_URL")
    RECIPE_SERVICE_BASE_URL = os.environ.get("PRD_RECIPE_SERVICE_BASE_URL")
    NUTRITION_SERVICE_BASE_URL = os.environ.get("PRD_NUTRITION_SERVICE_BASE_URL")