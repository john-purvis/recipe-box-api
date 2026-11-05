# recipes/db.py
import sqlite3

from flask import current_app, g

from recipes.models.recipes import Rating, Recipe


def mock_user(current_user_id):
    return {
        "id": current_user_id,
        "username": "",
        "email": "",
        "password_hash": "",
        "phone": "",
        "is_admin": ""
    }

def recipe_to_dict(recipe: Recipe):
    if not recipe:
        return None

    return {
        "id": recipe.id,
        "user_id": recipe.user_id,
        "title": recipe.title,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "is_public": recipe.is_public,
    }

def rating_to_dict(rating: Rating):
    if not rating:
        return None

    return {
        "id": rating.id,
        "user_id": rating.user_id,
        "recipe_id": rating.recipe_id,
        "score": rating.score,
        "comment": rating.comment,
    }

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

        try:
            db = get_db()
            db.execute("SELECT 1 FROM recipes LIMIT 1")
        except Exception:  # noqa: BLE001
            print("DATABASE: Creating")
            db.executescript("""
BEGIN TRANSACTION;
DROP TABLE IF EXISTS "users";
CREATE TABLE IF NOT EXISTS users
    (
        id            INTEGER NOT NULL            ,
        username      TEXT NOT NULL               ,
        email         TEXT NOT NULL               ,
        phone         TEXT NOT NULL               ,
        password_hash TEXT DEFAULT '' NOT NULL    ,
        is_admin      INTEGER DEFAULT '0' NOT NULL,
        location      VARCHAR(120)                ,
        CONSTRAINT pk_users
        PRIMARY KEY (id)                          ,
        CONSTRAINT uq_users_email
        UNIQUE (email)                            ,
        CONSTRAINT uq_users_phone
        UNIQUE (phone)                            ,
        CONSTRAINT uq_users_username
        UNIQUE (username)
    )
;
DROP TABLE IF EXISTS "recipes";
CREATE TABLE IF NOT EXISTS recipes
    (
        id           INTEGER NOT NULL             ,
        user_id      INTEGER NOT NULL             ,
        title        TEXT NOT NULL                ,
        ingredients  TEXT NOT NULL                ,
        instructions TEXT DEFAULT '' NOT NULL     ,
        is_public    INTEGER DEFAULT '1' NOT NULL ,
        CONSTRAINT pk_recipes
        PRIMARY KEY (id)                          ,
        CONSTRAINT fk_recipes_user_id_users
        FOREIGN KEY(user_id) REFERENCES users (id),
        CONSTRAINT uq_recipes_title
        UNIQUE (title)
    )
;
DROP TABLE IF EXISTS "ratings";
CREATE TABLE IF NOT EXISTS ratings
    (
        id        INTEGER NOT NULL                    ,
        user_id   INTEGER NOT NULL                    ,
        recipe_id INTEGER NOT NULL                    ,
        score     INTEGER DEFAULT '1' NOT NULL        ,
        comment   VARCHAR(120)                        ,
        CONSTRAINT pk_ratings
        PRIMARY KEY (id)                              ,
        CONSTRAINT fk_ratings_recipe_id_recipes
        FOREIGN KEY(recipe_id) REFERENCES recipes (id),
        CONSTRAINT fk_ratings_user_id_users
        FOREIGN KEY(user_id) REFERENCES users (id)
    )
;
-- seed admin user (pwd: super_secret_password_for_admin_user)
INSERT INTO "users" ("id","username","email","phone","password_hash","is_admin") VALUES (0,'admin','admin@recipe_box.com','0000000000','scrypt:32768:8:1$SYxXXuy01KOEZfMA$579b16bfe0004a331b6c07c6542bc7f7eae776196d15614bb88833c9cdb9bdacad5c8fc9e6170180d5b8c39afada1e2b014e32413a398017c82ff07b804d3501',1);
-- seed other users (pwd: winston)
INSERT INTO "users" ("id","username","email","phone","password_hash","is_admin") VALUES (1,'user','user@recipe_box.com','1234567890','scrypt:32768:8:1$099rSfvhTV1ffmtV$3b1e538293d15a0ffe4dbf5f2dcb68398e6b710f13616f9c475e05ab8e64950fd18fd88cf63b2adf200b37f28f04ccd98481a2cc22f44aef2dd9f5bab604b600',0);
INSERT INTO "users" ("id","username","email","phone","password_hash","is_admin") VALUES (2,'alice','alice@recipe_box.com','1111111111','scrypt:32768:8:1$b3oAtov0CDNhcukO$b0845043b9204cad68ea7e09b3a981b477ff2d4d4404e54a9bd15b14fb319a8fdb21981c72fecf37a295bb412e1d2bcc47150d2c6772c4fad904622d42f62372',0);
INSERT INTO "users" ("id","username","email","phone","password_hash","is_admin") VALUES (3,'bob','bob@recipe_box.com','2222222222','scrypt:32768:8:1$wFoVbmHsG7cSDSyV$51d0842a627b9baed408936a999d17418e9259da0a6165502ed0e319dc1b6462a6a70919d2fffda5c8ee5f791e9b11eb9c1f15344a8e9161018ae6a83765687e',0);
INSERT INTO "users" ("id","username","email","phone","password_hash","is_admin") VALUES('5','jackie','jackie@recipe_box.com','9998887777','scrypt:32768:8:1$ByGpJLmJIDU5D6l4$267050942a8ac225fa85dba283b0f3597148936e94d0b1d0bbc2241c466dcd0dc0b3963a5e90f7ef6ff7e2a25370962c4b7efc113966204cb2f87da4b350a471','0');
-- seed recipes
INSERT INTO "recipes" ("id","user_id","title","ingredients","instructions","is_public") VALUES('1','3','Shakshuka','eggs, tomatoes, peppers, onion, cumin, paprika','Simmer the sauce, crack in the eggs, cover until just set.','1');
INSERT INTO "recipes" ("id","user_id","title","ingredients","instructions","is_public") VALUES('2','1','Overnight oats','rolled oats, milk, yogurt, chia seeds, honey','Stir everything together and refrigerate overnight.','1');
INSERT INTO "recipes" ("id","user_id","title","ingredients","instructions","is_public") VALUES('4','2','Alice''s Homestyle Fried Chicken','Chicken and stuff','Put other stuff on chicken and cook it.','1');
INSERT INTO "recipes" ("id","user_id","title","ingredients","instructions","is_public") VALUES('5','2','Grilled Cheese','bread, cheese, butter','Place cheese inside two slices of bread and using butter, grill until cheese is melted and bread is brown.','1');
INSERT INTO "recipes" ("id","user_id","title","ingredients","instructions","is_public") VALUES('6','5','Spaghetti Bolognese','spaghetti, ground beef, tomato sauce, onion, garlic','Boil pasta, Cook beef, Add sauce, Combine and serve','1');
-- seed ratings
INSERT INTO "ratings" ("id","user_id","recipe_id","score","comment") VALUES('1','1','1','5','Great recipe!');
INSERT INTO "ratings" ("id","user_id","recipe_id","score","comment") VALUES('2','2','6','4','Excellent!');
INSERT INTO "ratings" ("id","user_id","recipe_id","score","comment") VALUES('3','2','5','4','Very Good!');
COMMIT;
            """)
            db.commit()
            print("DATABASE: Created")
