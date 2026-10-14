class Config:
    JSON_SORT_KEYS = False

class DevelopmentConfig(Config):
    DATABASE = "recipes.db"
    JWT_SECRET_KEY = "dev-secret-key"

class TestingConfig(Config):
    DATABASE = "test_recipes.db"
    JWT_SECRET_KEY = "test-secret-key"

class ProductionConfig(Config):
    DATABASE = "prod_recipes.db"
    JWT_SECRET_KEY = "prod-secret-key"
