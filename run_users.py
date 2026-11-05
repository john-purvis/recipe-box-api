# run_users.py
"""
Recipe Box - Users API.

A working Flask + SQLite CRUD API for users.
"""
from dotenv import load_dotenv

load_dotenv()
load_dotenv(override=True)

from users import create_app

user_app = create_app("development")

if __name__ == "__main__":
    user_app.run(debug=True, port=5001)
