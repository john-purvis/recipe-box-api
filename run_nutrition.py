# run_nutrition.py
"""
Recipe Box - Nutrition API.

A working Flask + SQLite CRUD API for recipes.
"""
from dotenv import load_dotenv

load_dotenv()
load_dotenv(override=True)

# from app import app
from nutrition import create_app

nutrition_app = create_app("development")

if __name__ == "__main__":
    nutrition_app.run(debug=True, port=5003)
