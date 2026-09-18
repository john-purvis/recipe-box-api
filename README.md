# Recipe Box API

Owner: John Purvis - cloned from recipe-box-api skeleton by John S. Berta

A small, working Flask + SQLite API for keeping recipes. Full CRUD, clean
status codes - and Flask JWT authentication.

* New users may register, login and use the system immediately.
* Authenticated users may view, add, update, and delete recipes.
* Authenticated users may also update their own user details (e.g. email or phone)
* Authorization is enforced so that:
     * Users may only view recipes that are their own or public.
     * Users may only change recipes that are their own
     * User may only delete recipes that are their own.
* Admin users may:
     * view, add, update, and delete any recipes
     * view, add, update, and delete users

An 'admin' user comes already installed.
The default admin password is super_secret_password_for_admin_user and may be changed.

# .env
An .env file contains database information and the system key used
for JWT authentication and authorization.  This file is required and should be
created with at least the two keys below in this format:
```
JWT_SECRET_KEY=\<Your JWT key\>
DATABASE_NAME=\<Your Database Name\> (Defaults to recipes.db)
```

## Run it

```
Use 'python init_db.py' to initialize the database prior to first run

Use 'python app.py' to run the flask web application
```
Requires Python 3.10+ and Flask (`pip install -r requirements.txt`).


## Endpoints

| Method | Path         | Success          | Errors                                                |
|--------|--------------|------------------|-------------------------------------------------------|
| GET    | /recipes     | 200              | 403 not authorized                                    |
| GET    | /recipes/&lt;id&gt;   | 200     | 403 · 404                                             |
| POST   | /recipes     | 201              | 400 bad body · 403 · 409 duplicate title              |
| PATCH  | /recipes/&lt;id&gt;   | 200     | 400 · 403 · 404 · 409                                 |
| DELETE | /recipes/&lt;id&gt;   | 204     | 403 · 404                                             |
|                                                                                                  |
| `is_public` is stored on every recipe and defaults to 'True'                                     |
| recipes marked private will only be visible to their owners and admins.                          |
|                                                                                                  |
| POST   | /login       | 200              | 400 bad body · 401 invalid username or password       |
| POST   | /logout      | 200              | 403                                                   |
| POST   | /register    | 201 user created | 400 bad body · 409 duplicate username / email / phone |
| PATCH  | /users/&lt;id&gt;   | 200       | 400 · 403 · 404 · 409                                 |
| DELETE | /users/&lt;id&gt;   | 204       | 403 · 404                                             |

## Try it

Display the API homepage:
```
curl -i http://127.0.0.1:5000/
```
EXPECT:
     200 OK with html file contents

Display the API docs:
```
curl -i http://127.0.0.1:5000/apidocs/
```
EXPECT:
     200 OK with html doc contents

Create a user:
```
curl -i http://127.0.0.1:5000/register -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "test", "email": "test@testytester.com", "phone": "5558675309" }'
```
EXPECT:
     200 OK with user

Login to obtain a JWT token (used in following methods):
```
curl -i http://127.0.0.1:5000/login -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "test" }'
```
EXPECT:
     200 OK with token
     Note the token that is retruned by login.  You will need this for routes requiring authorization.
     The token will look something like 'eyJhbGciOiJIUzI1NiIsInR5...'

List the recipes (not authorized):
```
curl -i http://127.0.0.1:5000/recipes \
     -H "Authorization: Bearer INVALID_TOKEN_STRING"
```
EXPECT:
     422 UNPROCESSABLE ENTITY

List the recipes (authorized):
```
curl -i http://127.0.0.1:5000/recipes \
 -H "Authorization: Bearer <YOUR_TOKEN_FROM_LOGIN_WITHOUT_QUOTES>"
```
EXPECT:
     200 with recipe list

Get one recipe (public):
```
curl -i http://127.0.0.1:5000/recipes/1 \
     -H "Authorization: Bearer <YOUR_TOKEN_FROM_LOGIN_WITHOUT_QUOTES>"
```
EXPECT:
     200 with recipe
     recipe 1 is public so anyone can view it

Get one recipe (private):
```
curl -i http://127.0.0.1:5000/recipes/3 \
     -H "Authorization: Bearer <YOUR_TOKEN_FROM_LOGIN_WITHOUT_QUOTES>"
```
EXPECT:
     404 NOT FOUND
     recipe 3 is private and owned by admin so it will not be found
     or appear in the recipes list until the owner sets it to public

Create your own recipe:
```
curl -i POST http://127.0.0.1:5000/recipes -H "Content-Type: application/json" \
     -H "Authorization: Bearer <YOUR_TOKEN_FROM_LOGIN_WITHOUT_QUOTES>"
     -d '{"title": "Toast", "ingredients": "bread", "instructions": "Put in toaster and wait until brown.", "is_public": "False"}'
```
EXPECT:
     200 with recipe
     note that if 'is_public = False' is not included, it defaults to 'True'

Update recipe:
```
curl -i PATCH "http://localhost:5000/recipes/3" \
     -H "accept: application/json" \
     -H "Authorization: Bearer <YOUR_TOKEN_FROM_LOGIN_WITHOUT_QUOTES>" \
     -H "Content-Type: application/json" -d "{ \"is_public\": true}"
```
EXPECT:
     200 and recipe (if user owns recipe or is_admin)
     403 FORBIDDEN (if user does not own the recipe)

Delete recipe:
```
curl -i DELETE http://127.0.0.1:5000/recipes/1
     -H "accept: application/json" \
     -H "Authorization: Bearer <YOUR_TOKEN_FROM_LOGIN_WITHOUT_QUOTES>"
```
EXPECT:
     204 (if user owns recipe or is_admin)

List user(s):
```
curl -i GET "http://localhost:5000/users" \
     -H "accept: application/json" \
     -H "Authorization: Bearer <YOUR_TOKEN_FROM_LOGIN_WITHOUT_QUOTES>"
```
EXPECT:
     200 and list of users or self

Update user:
```
curl -i PATCH "http://localhost:5000/users/1" \
     -H "accept: application/json" \
     -H "Authorization: Bearer <YOUR_TOKEN_FROM_LOGIN_WITHOUT_QUOTES>" \
     -H "Content-Type: application/json" -d "{ \"phone\": \"1231231234\"}"
```
EXPECT:
     200 and user (if user is self or user is_admin)
     403 FORBIDDEN (if user not admin tries to edit another user)

Delete user:
```
curl -i DELETE "http://localhost:5000/users/1" \
     -H "accept: application/json" \
     -H "Authorization: Bearer <YOUR_TOKEN_FROM_LOGIN_WITHOUT_QUOTES>"
```
EXPECT:
     204 CONTENT REMOVED (if user is_admin)
     403 FORBIDDEN (if user is not admin)


## Swagger Docs
http://localhost:5000/apidocs/

## Postman
https://www.postman.com/