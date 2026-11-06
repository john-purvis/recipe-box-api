# run_gateway.py
"""
Recipe Box - Recipes API.

A working Flask + SQLite CRUD API for recipes.
"""
import asyncio

from dotenv import load_dotenv

load_dotenv()
load_dotenv(override=True)

# from app import app
from gateway import create_app

gateway_app = create_app("development")

if __name__ == "__main__":
    gateway_app.run(debug=True, port=5000)
