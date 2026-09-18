"""Create the application's SQLite database.

This script will attempt to load and execute the SQL in `recipes.db.sql` (which
contains table DDL and seed data). If that file is missing it falls back to a
minimal inline schema and seed list.

Run once after cloning: python init_db.py
"""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent
SQL_FILE = ROOT / "recipes.db.sql"

SCHEMA = """
CREATE TABLE IF NOT EXISTS "users" (
	"id"	        INTEGER PRIMARY KEY      , -- internal primary key
	"username"	    TEXT NOT NULL UNIQUE     , -- handle shown in the UI (must be unique)
	"email"	        TEXT NOT NULL UNIQUE     , -- contact (must be unique)
    "phone"         TEXT NOT NULL UNIQUE     , -- contact (must be unique)
	"password_hash"	TEXT NOT NULL DEFAULT '' , -- non-readable password representation (NOT reversible)
	"is_admin"      BOOLEAN DEFAULT 0          -- is user an administrator

    -- Boolean constraint (Restricts input strictly to 0 or 1)
    CONSTRAINT hc_boolean_check CHECK (is_admin IN (0, 1))
);
CREATE TABLE IF NOT EXISTS recipes (
(
	id           INTEGER PRIMARY KEY     ,
	user_id		 INTEGER NOT NULL		 ,
	title        TEXT NOT NULL UNIQUE    ,
	ingredients  TEXT NOT NULL           ,
	instructions TEXT NOT NULL DEFAULT '',
	is_public    INTEGER NOT NULL DEFAULT 1

    -- Boolean constraint (Restricts input strictly to 0 or 1)
    CONSTRAINT hc_boolean_check CHECK (is_public IN (0, 1)),

    -- Foreign Key constraint
    CONSTRAINT fk_user_id
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE -- Deletes settings if the user is deleted
);

"""
SEED_USERS = [
    (0, "admin", "admin@recipe_box_api", "0000000000", \
     "scrypt:32768:8:1$SYxXXuy01KOEZfMA$579b16bfe0004a331b6c07c6542bc7f7eae776196d15614bb88833c9cdb9bdacad5c8fc9e6170180d5b8c39afada1e2b014e32413a398017c82ff07b804d3501", 1)
]
SEED_RECIPES = [
    (
        0,
        "Shakshuka",
        "eggs, tomatoes, peppers, onion, cumin, paprika",
        "Simmer the sauce, crack in the eggs, cover until just set.",
        1,
    ),
    (
        0,
        "Overnight oats",
        "rolled oats, milk, yogurt, chia seeds, honey",
        "Stir everything together and refrigerate overnight.",
        1,
    ),
    (
        0,
        "Secret family hot sauce",
        "habaneros, garlic, vinegar, a secret ingredient",
        "If we wrote it down here, it wouldn't be a secret.",
        0,
    ),
]

def main():
    db_path = ROOT / "recipes.db"
    connection = sqlite3.connect(str(db_path))

    if SQL_FILE.exists():
        sql = SQL_FILE.read_text(encoding="utf-8")
        connection.executescript(sql)
        connection.commit()
        print(f"Applied schema and seed values from {SQL_FILE.name} to {db_path.name}.")
    else:
        connection.executescript(SCHEMA)
        existing = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if existing == 0:
            connection.executemany(
                "INSERT INTO users (id, username, email, phone, password_hash, is_admin)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                SEED_USERS,
            )
            connection.commit()
            print(f"Created {db_path.name} and seeded {len(SEED_USERS)} users.")
        else:
            print(f"{db_path.name} already has {existing} users - nothing to do.")

        existing = connection.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
        if existing == 0:
            connection.executemany(
                "INSERT INTO recipes (title, ingredients, instructions, is_public)"
                " VALUES (?, ?, ?, ?)",
                SEED_RECIPES,
            )
            connection.commit()
            print(f"Created {db_path.name} and seeded {len(SEED_RECIPES)} recipes.")
        else:
            print(f"{db_path.name} already has {existing} recipes - nothing to do.")

    connection.close()

if __name__ == "__main__":
    main()
