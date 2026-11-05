# run_app.py
"""
Recipe Box - Recipes API.

A working Flask + SQLite CRUD API for recipes.
"""
from dotenv import load_dotenv

load_dotenv()
load_dotenv(override=True)

# from app import app
from app import create_app

app = create_app("development")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
