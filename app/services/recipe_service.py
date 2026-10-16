# app/services/recipe_service.py
import sqlite3

from ..db import get_db, row_to_dict


def list_recipes_for_user(user_id, is_admin):
    db = get_db()
    if is_admin:
        rows = db.execute(
            "SELECT * FROM recipes ORDER BY id"
        ).fetchall()
    else:
        rows = db.execute(
            """
            SELECT * FROM recipes
            WHERE (user_id = ? OR is_public = 1)
            ORDER BY id
            """,
            (user_id,)
        ).fetchall()
    return [row_to_dict(r) for r in rows]

def get_recipe_for_user(recipe_id, user_id, is_admin):
    db = get_db()
    if is_admin:
        row = db.execute(
            "SELECT * FROM recipes WHERE id = ?",
            (recipe_id,)
        ).fetchone()
    else:
        row = db.execute(
            """
            SELECT * FROM recipes
            WHERE id = ?
              AND (user_id = ? OR is_public = 1)
            """,
            (recipe_id, user_id)
        ).fetchone()
    return row_to_dict(row) if row else None

def create_recipe_for_user(user_id, data):
    db = get_db()
    try:
        cur = db.execute(
            """
            INSERT INTO recipes (user_id, title, ingredients, instructions, is_public)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                data["title"],
                data["ingredients"],
                data.get("instructions", ""),
                1 if data.get("is_public", True) else 0,
            ),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return None, "a recipe with that title already exists"

    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?",
        (cur.lastrowid,)
    ).fetchone()
    return row_to_dict(row), None

def update_recipe_for_user(recipe_id, user_id, is_admin, data):
    db = get_db()

    check_recipe = db.execute(
        "SELECT * FROM recipes WHERE id = ?",
        (recipe_id,)
    ).fetchone()
    if not check_recipe:
        return None, "recipe_not_found"

    if str(check_recipe["user_id"]) != str(user_id) and not is_admin:
        return None, "access_denied"

    fields, values = [], []
    for column in ("title", "ingredients", "instructions"):
        if column in data:
            fields.append(f"{column} = ?")
            values.append(data[column])
    if "is_public" in data:
        fields.append("is_public = ?")
        values.append(1 if data["is_public"] else 0)

    if not fields:
        return None, "nothing_to_update"

    values.append(recipe_id)
    try:
        cur = db.execute(
            f"UPDATE recipes SET {', '.join(fields)} WHERE id = ?",
            values,
        )
        db.commit()
    except sqlite3.IntegrityError:
        return None, "duplicate_title"

    if cur.rowcount == 0:
        return None, "recipe_not_found"

    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?",
        (recipe_id,)
    ).fetchone()
    return row_to_dict(row), None

def delete_recipe_for_user(recipe_id, user_id, is_admin):
    db = get_db()

    check_recipe = db.execute(
        "SELECT * FROM recipes WHERE id = ?",
        (recipe_id,)
    ).fetchone()
    if not check_recipe:
        return "recipe_not_found"

    if str(check_recipe["user_id"]) != str(user_id) and not is_admin:
        return "access_denied"

    cur = db.execute(
        "DELETE FROM recipes WHERE id = ?",
        (recipe_id,)
    )
    db.commit()

    if cur.rowcount == 0:
        return "recipe_not_found"

    return None  # success
