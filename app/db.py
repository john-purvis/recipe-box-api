# app/db.py
import sqlite3

from flask import current_app, g


def row_to_dict(row):
    """
    Convert a SQLite row object to a dictionary.
    This function dynamically builds a dictionary from the row's keys and values,
    ensuring that only the columns present in the row are included.
    """
    if not row:
        return None

    json_str = {key: row[key] for key in row.keys()}  # noqa: SIM118

    # 2. Check if the target field exists in the dictionary
    if "is_admin" in json_str:
        value = json_str["is_admin"]

        # Check for numeric 1/0 or string "1"/"0"
        if value in (1, "1"):
            json_str["is_admin"] = True
        elif value in (0, "0"):
            json_str["is_admin"] = False

    if "is_public" in json_str:
        value = json_str["is_public"]

        # Check for numeric 1/0 or string "1"/"0"
        if value in (1, "1"):
            json_str["is_public"] = True
        elif value in (0, "0"):
            json_str["is_public"] = False

    return json_str

def get_db():
    if "db" not in g:
        db_path = current_app.config["DATABASE"]
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def init_db(app):
    with app.app_context():
        db = get_db()
        db.executescript("""
        -- your CREATE TABLE IF NOT EXISTS users (...)
        -- your CREATE TABLE IF NOT EXISTS recipes (...)
        """)
        db.commit()
