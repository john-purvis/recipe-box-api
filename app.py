"""
Recipe Box API.

A working Flask + SQLite CRUD API for recipes.
"""
from app import app

if __name__ == "__main__":
    app.run(debug=True, port=5000)
