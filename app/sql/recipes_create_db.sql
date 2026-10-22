BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS users
    (
        id            INTEGER NOT NULL            ,
        username      TEXT NOT NULL               ,
        email         TEXT NOT NULL               ,
        phone         TEXT NOT NULL               ,
        password_hash TEXT DEFAULT '' NOT NULL    ,
        is_admin      INTEGER DEFAULT '0' NOT NULL,
        PRIMARY KEY (id)                          ,
        UNIQUE (email)                            ,
        UNIQUE (phone)                            ,
        UNIQUE (username)
    )
;
CREATE TABLE recipes
    (
        id           INTEGER NOT NULL             ,
        user_id      INTEGER NOT NULL             ,
        title        TEXT NOT NULL                ,
        ingredients  TEXT NOT NULL                ,
        instructions TEXT DEFAULT '' NOT NULL     ,
        is_public    INTEGER DEFAULT '1' NOT NULL ,
        PRIMARY KEY (id)                          ,
        FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
        UNIQUE (title)
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
INSERT INTO "recipes" ("id","user_id","title","ingredients","instructions","is_public") VALUES (1,3,'Shakshuka','eggs, tomatoes, peppers, onion, cumin, paprika','Simmer the sauce, crack in the eggs, cover until just set.',1);
INSERT INTO "recipes" ("id","user_id","title","ingredients","instructions","is_public") VALUES (2,1,'Overnight oats','rolled oats, milk, yogurt, chia seeds, honey','Stir everything together and refrigerate overnight.',1);
INSERT INTO "recipes" ("id","user_id","title","ingredients","instructions","is_public") VALUES (4,2,'Alice''s Homestyle Fried Chicken','Chicken and stuff','Put other stuff on chicken and cook it.',1);
INSERT INTO "recipes" ("id","user_id","title","ingredients","instructions","is_public") VALUES('5','2','Grilled Cheese','bread, cheese, butter','Place cheese inside two slices of bread and using butter, grill until cheese is melted and bread is brown.','1');
COMMIT;
