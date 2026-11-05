"""
Recipe Box - Recipes API (separate service).

A Flask + SQLite CRUD API for recipes, running on port 5002.
"""
from dotenv import load_dotenv

load_dotenv()
load_dotenv(override=True)

from recipes import create_app

recipe_app = create_app("development")

if __name__ == "__main__":
    recipe_app.run(debug=True, port=5002)
