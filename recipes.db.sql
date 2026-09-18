BEGIN TRANSACTION;
DROP TABLE IF EXISTS "users";
CREATE TABLE "users" (
	"id"	        INTEGER PRIMARY KEY      , -- internal primary key
	"username"	    TEXT NOT NULL UNIQUE     , -- handle shown in the UI (must be unique)
	"email"	        TEXT NOT NULL UNIQUE     , -- contact (must be unique)
    "phone"         TEXT NOT NULL UNIQUE     , -- contact (must be unique)
	"password_hash"	TEXT NOT NULL DEFAULT '' , -- non-readable password representation (NOT reversible)
	"is_admin"      BOOLEAN DEFAULT 0          -- is user an administrator

    -- Boolean constraint (Restricts input strictly to 0 or 1)
    CONSTRAINT hc_boolean_check CHECK (is_admin IN (0, 1))
);
DROP TABLE IF EXISTS "recipes";
CREATE TABLE recipes
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
-- seed admin user
INSERT INTO "users"   ("id","username","email","phone","password_hash","is_admin") VALUES(0, 'admin', 'admin@recipe_box_api', '0000000000', 'scrypt:32768:8:1$SYxXXuy01KOEZfMA$579b16bfe0004a331b6c07c6542bc7f7eae776196d15614bb88833c9cdb9bdacad5c8fc9e6170180d5b8c39afada1e2b014e32413a398017c82ff07b804d3501', 1);
-- seed recipes
INSERT INTO "recipes" ("id","user_id","title","ingredients","instructions","is_public") VALUES (1,0,'Shakshuka','eggs, tomatoes, peppers, onion, cumin, paprika','Simmer the sauce, crack in the eggs, cover until just set.',1);
INSERT INTO "recipes" ("id","user_id","title","ingredients","instructions","is_public") VALUES (2,0,'Overnight oats','rolled oats, milk, yogurt, chia seeds, honey','Stir everything together and refrigerate overnight.',1);
INSERT INTO "recipes" ("id","user_id","title","ingredients","instructions","is_public") VALUES (3,0,'Secret family hot sauce','habaneros, garlic, vinegar, a secret ingredient','If we wrote it down here, it wouldn''t be a secret.',0);
COMMIT;
