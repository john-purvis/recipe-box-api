import os


class Config:
    key = os.environ.get("JWT_SECRET_KEY")
    if not key:
        raise RuntimeError("JWT_SECRET_KEY environment variable is required")
    JWT_SECRET_KEY = key
    JSON_SORT_KEYS = bool(os.environ.get("JSON_SORT_KEYS", "False"))

class DevelopmentConfig(Config):
    PYTHON_DEBUG = os.environ.get("DEV_FLASK_DEBUG") == "True"
    FLASK_DEBUG = os.environ.get("DEV_FLASK_DEBUG") == "True"
    db_name = os.environ.get("DEV_DATABASE")
    if not db_name:
        raise RuntimeError("DEV_DATABASE environment variable is required")
    DATABASE = db_name

class TestingConfig(Config):
    PYTHON_DEBUG = os.environ.get("TST_FLASK_DEBUG") == "True"
    FLASK_DEBUG = os.environ.get("TST_FLASK_DEBUG") == "True"
    db_name = os.environ.get("TST_DATABASE")
    if not db_name:
        raise RuntimeError("TST_DATABASE environment variable is required")
    DATABASE = db_name

class ProductionConfig(Config):
    PYTHON_DEBUG = os.environ.get("PRD_FLASK_DEBUG") == "True"
    FLASK_DEBUG = os.environ.get("PRD_FLASK_DEBUG") == "True"
    db_name = os.environ.get("PRD_DATABASE")
    if not db_name:
        raise RuntimeError("PRD_DATABASE environment variable is required")
    DATABASE = db_name
