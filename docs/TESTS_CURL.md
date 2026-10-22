
# REGISTER USER
$ curl -i -X POST http://localhost:5000/auth/register -H "Content-Type: application/json" -d '{"username": "john_test", "password": "secret", "email": "john_test@example.com", "phone": "3332224444"}'
HTTP/1.1 201 CREATED
Server: Werkzeug/3.1.8 Python/3.14.8
Date: Fri, 16 Oct 2026 16:25:54 GMT
Content-Type: application/json
Content-Length: 40
Connection: close

{
  "message": "registered john_test"
}

# REGISTER USER (2ND TIME WITH ERROR)
$ curl -i -X POST "http://localhost:5000/auth/register" -H "Content-Type: application/json" -d '{"username": "john_test", "password": "secret", "email": "john_test@example.com", "phone": "3332224444"}'
HTTP/1.1 409 CONFLICT
Server: Werkzeug/3.1.8 Python/3.14.8
Date: Sat, 17 Oct 2026 08:59:00 GMT
Content-Type: application/json
Content-Length: 32
Connection: close

{
  "error": "username taken"
}


# LOGIN
$ curl -i -X POST http://localhost:5000/auth/login \
-H "Content-Type: application/json" \
-d '{"username": "john_test", "password": "secret"}'
HTTP/1.1 200 OK
Server: Werkzeug/3.1.8 Python/3.14.8
Date: Sat, 17 Oct 2026 09:00:08 GMT
Content-Type: application/json
Content-Length: 399
Connection: close

{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MjIyNzYwOCwianRpIjoiYjFhZWNiYmMtOGFiMi00OTRjLTg2M2MtZWYzZGViM2ZiMjU4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjQiLCJuYmYiOjE3OTIyMjc2MDgsImNzcmYiOiIzYmZhYjg5NS1hMjU3LTRlMTYtYmY0YS1kNTZmYjgzNzgyNzgiLCJleHAiOjE3OTIyMjg1MDgsImlzX2FkbWluIjpmYWxzZX0.dJnxA5j5VZTLvAXZcUwNDpJxJyFqpOZ2Gcqct7DXLnY"
}




# LIST RECIPES
curl -i -X GET "http://localhost:5000/recipes/" -H "accept: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MjIyNzYwOCwianRpIjoiYjFhZWNiYmMtOGFiMi00OTRjLTg2M2MtZWYzZGViM2ZiMjU4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjQiLCJuYmYiOjE3OTIyMjc2MDgsImNzcmYiOiIzYmZhYjg5NS1hMjU3LTRlMTYtYmY0YS1kNTZmYjgzNzgyNzgiLCJleHAiOjE3OTIyMjg1MDgsImlzX2FkbWluIjpmYWxzZX0.dJnxA5j5VZTLvAXZcUwNDpJxJyFqpOZ2Gcqct7DXLnY"
HTTP/1.1 200 OK
Server: Werkzeug/3.1.8 Python/3.14.8
Date: Sat, 17 Oct 2026 09:02:08 GMT
Content-Type: application/json
Content-Length: 957
Connection: close

[
  {
    "id": 1,
    "ingredients": "eggs, tomatoes, peppers, onion, cumin, paprika",
    "instructions": "Simmer the sauce, crack in the eggs, cover until just set.",
    "is_public": true,
    "title": "Shakshuka",
    "user_id": 3
  },
  {
    "id": 2,
    "ingredients": "rolled oats, milk, yogurt, chia seeds, honey",
    "instructions": "Stir everything together and refrigerate overnight.",
    "is_public": true,
    "title": "Overnight oats",
    "user_id": 1
  },
  {
    "id": 4,
    "ingredients": "Chicken and stuff",
    "instructions": "Put other stuff on chicken and cook it.",
    "is_public": true,
    "title": "Alice's Homestyle Fried Chicken",
    "user_id": 2
  },
  {
    "id": 5,
    "ingredients": "bread, cheese, butter",
    "instructions": "Place cheese inside two slices of bread and using butter, grill until cheese is melted and bread is brown.",
    "is_public": true,
    "title": "Grilled Cheese",
    "user_id": 2
  }
]




# GET RECIPE 4
curl -i -X GET "http://localhost:5000/recipes/4" -H "accept: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MjIyNzYwOCwianRpIjoiYjFhZWNiYmMtOGFiMi00OTRjLTg2M2MtZWYzZGViM2ZiMjU4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjQiLCJuYmYiOjE3OTIyMjc2MDgsImNzcmYiOiIzYmZhYjg5NS1hMjU3LTRlMTYtYmY0YS1kNTZmYjgzNzgyNzgiLCJleHAiOjE3OTIyMjg1MDgsImlzX2FkbWluIjpmYWxzZX0.dJnxA5j5VZTLvAXZcUwNDpJxJyFqpOZ2Gcqct7DXLnY"
HTTP/1.1 200 OK
Server: Werkzeug/3.1.8 Python/3.14.8
Date: Sat, 17 Oct 2026 09:03:16 GMT
Content-Type: application/json
Content-Length: 196
Connection: close

{
  "id": 4,
  "ingredients": "Chicken and stuff",
  "instructions": "Put other stuff on chicken and cook it.",
  "is_public": true,
  "title": "Alice's Homestyle Fried Chicken",
  "user_id": 2
}




# CREATE RECIPE
curl -i -X POST "http://localhost:5000/recipes/" -H "accept: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MjIyNzYwOCwianRpIjoiYjFhZWNiYmMtOGFiMi00OTRjLTg2M2MtZWYzZGViM2ZiMjU4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjQiLCJuYmYiOjE3OTIyMjc2MDgsImNzcmYiOiIzYmZhYjg5NS1hMjU3LTRlMTYtYmY0YS1kNTZmYjgzNzgyNzgiLCJleHAiOjE3OTIyMjg1MDgsImlzX2FkbWluIjpmYWxzZX0.dJnxA5j5VZTLvAXZcUwNDpJxJyFqpOZ2Gcqct7DXLnY" -H "Content-Type: application/json" -d "{ \"ingredients\": \"Water\", \"instructions\": \"Heat the water to boiling\", \"is_public\": true, \"title\": \"Boiled Water\"}"
HTTP/1.1 201 CREATED
Server: Werkzeug/3.1.8 Python/3.14.8
Date: Sat, 17 Oct 2026 09:08:46 GMT
Content-Type: application/json
Content-Length: 151
Connection: close

{
  "id": 6,
  "ingredients": "Water",
  "instructions": "Heat the water to boiling",
  "is_public": true,
  "title": "Boiled Water",
  "user_id": 4
}

# CREATE RECIPE (WITH ERROR)
curl -i -X POST "http://localhost:5000/recipes/" -H "accept: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MjIyNzYwOCwianRpIjoiYjFhZWNiYmMtOGFiMi00OTRjLTg2M2MtZWYzZGViM2ZiMjU4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjQiLCJuYmYiOjE3OTIyMjc2MDgsImNzcmYiOiIzYmZhYjg5NS1hMjU3LTRlMTYtYmY0YS1kNTZmYjgzNzgyNzgiLCJleHAiOjE3OTIyMjg1MDgsImlzX2FkbWluIjpmYWxzZX0.dJnxA5j5VZTLvAXZcUwNDpJxJyFqpOZ2Gcqct7DXLnY" -H "Content-Type: application/json" -d "{ \"ingredients\": \"Water\", \"instructions\": \"Heat the water to boiling\", \"is_public\": true, \"title\": \"Boiled Water\"}"
HTTP/1.1 409 CONFLICT
Server: Werkzeug/3.1.8 Python/3.14.8
Date: Sat, 17 Oct 2026 09:09:25 GMT
Content-Type: application/json
Content-Length: 57
Connection: close

{
  "error": "a recipe with that title already exists"
}




# DELETE RECIPE
curl -i -X DELETE "http://localhost:5000/recipes/6" -H "accept: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MjIyNzYwOCwianRpIjoiYjFhZWNiYmMtOGFiMi00OTRjLTg2M2MtZWYzZGViM2ZiMjU4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjQiLCJuYmYiOjE3OTIyMjc2MDgsImNzcmYiOiIzYmZhYjg5NS1hMjU3LTRlMTYtYmY0YS1kNTZmYjgzNzgyNzgiLCJleHAiOjE3OTIyMjg1MDgsImlzX2FkbWluIjpmYWxzZX0.dJnxA5j5VZTLvAXZcUwNDpJxJyFqpOZ2Gcqct7DXLnY"
HTTP/1.1 204 NO CONTENT
Server: Werkzeug/3.1.8 Python/3.14.8
Date: Sat, 17 Oct 2026 09:08:20 GMT
Content-Type: text/html; charset=utf-8
Connection: close

# DELETE RECIPE (WITH ERROR)
curl -i -X DELETE "http://localhost:5000/recipes/5" -H "accept: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MjIyNzYwOCwianRpIjoiYjFhZWNiYmMtOGFiMi00OTRjLTg2M2MtZWYzZGViM2ZiMjU4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjQiLCJuYmYiOjE3OTIyMjc2MDgsImNzcmYiOiIzYmZhYjg5NS1hMjU3LTRlMTYtYmY0YS1kNTZmYjgzNzgyNzgiLCJleHAiOjE3OTIyMjg1MDgsImlzX2FkbWluIjpmYWxzZX0.dJnxA5j5VZTLvAXZcUwNDpJxJyFqpOZ2Gcqct7DXLnY"
HTTP/1.1 403 FORBIDDEN
Server: Werkzeug/3.1.8 Python/3.14.8
Date: Sat, 17 Oct 2026 09:07:38 GMT
Content-Type: application/json
Content-Length: 31
Connection: close

{
  "error": "access denied"
}

# DELETE RECIPE (NOT FOUND)
$ curl -i -X DELETE "http://localhost:5000/recipes/6" -H "accept: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MjIyNzYwOCwianRpIjoiYjFhZWNiYmMtOGFiMi00OTRjLTg2M2MtZWYzZGViM2ZiMjU4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjQiLCJuYmYiOjE3OTIyMjc2MDgsImNzcmYiOiIzYmZhYjg5NS1hMjU3LTRlMTYtYmY0YS1kNTZmYjgzNzgyNzgiLCJleHAiOjE3OTIyMjg1MDgsImlzX2FkbWluIjpmYWxzZX0.dJnxA5j5VZTLvAXZcUwNDpJxJyFqpOZ2Gcqct7DXLnY"
HTTP/1.1 404 NOT FOUND
Server: Werkzeug/3.1.8 Python/3.14.8
Date: Sat, 17 Oct 2026 09:10:58 GMT
Content-Type: application/json
Content-Length: 34
Connection: close

{
  "error": "recipe not found"
}











