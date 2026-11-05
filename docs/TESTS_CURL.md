
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











================================================================================
================================================================================
================================================================================
INTERNAL SERVICE TOKEN TESTS (NO JWT TOKEN)

1.	No headers at all
$ curl -i -X GET "http://localhost:5002/recipes/"
HTTP/1.1 401 UNAUTHORIZED
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Thu, 05 Nov 2026 02:49:35 GMT
Content-Type: application/json
Content-Length: 40
Connection: close

{
  "error": "missing_internal_token"
}

2.	Wrong internal token
$ curl -i -X GET "http://localhost:5002/recipes/" -H "accept: application/json" -H "X-Internal-Token: XSWT-badtoken"
HTTP/1.1 401 UNAUTHORIZED
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Thu, 05 Nov 2026 02:50:49 GMT
Content-Type: application/json
Content-Length: 40
Connection: close

{
  "error": "invalid_internal_token"
}

3. Correct internal token, no JWT yet
$ curl -i -X GET "http://localhost:5002/recipes/" -H "accept: application/json" -H "X-Internal-Token: XSWT-sdfgkfdsosiojnovnonqklpsdfsdfgnjsdfbknfvbvklcfdfg"
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Thu, 05 Nov 2026 02:47:52 GMT
Content-Type: application/json
Content-Length: 945
Connection: close

[
  {
    "id": 1,
    "user_id": 3,
    "title": "Shakshuka",
    "ingredients": "eggs, tomatoes, peppers, onion, cumin, paprika",
    "instructions": "Simmer the sauce, crack in the eggs, cover until just set.",
    "is_public": 1
  },
  {
    "id": 2,
    "user_id": 1,
    "title": "Overnight oats",
    "ingredients": "rolled oats, milk, yogurt, chia seeds, honey",
    "instructions": "Stir everything together and refrigerate overnight.",
    "is_public": 1
  },
  {
    "id": 4,
    "user_id": 2,
    "title": "Alice's Homestyle Fried Chicken",
    "ingredients": "Chicken and stuff",
    "instructions": "Put other stuff on chicken and cook it.",
    "is_public": 1
  },
  {
    "id": 5,
    "user_id": 2,
    "title": "Grilled Cheese",
    "ingredients": "bread, cheese, butter",
    "instructions": "Place cheese inside two slices of bread and using butter, grill until cheese is melted and bread is brown.",
    "is_public": 1
  }
]


================================================================================
================================================================================
================================================================================
INTERNAL SERVICE TOKEN TESTS (JWT TOKEN TESTS)

1. No Authorization, valid internal token
$ curl -i -X GET "http://localhost:5002/recipes/" -H "accept: application/json" -H "X-Internal-Token: XSWT-sdfgkfdsosiojnovnonqklpsdfsdfgnjsdfbknfvbvklcfdfg"

2. Bad JWT, valid internal token
$ curl -i -X GET "http://localhost:5002/recipes/" -H "accept: application/json" -H "X-Internal-Token: XSWT-sdfgkfdsosiojnovnonqklpsdfsdfgnjsdfbknfvbvklcfdfg" -H "Authorization: Bearer BADJWT"
HTTP/1.1 422 UNPROCESSABLE ENTITY
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Thu, 05 Nov 2026 03:06:35 GMT
Content-Type: application/json
Content-Length: 35
Connection: close

{
  "msg": "Not enough segments"
}

$ curl -i -X GET "http://localhost:5002/recipes/" -H "accept: application/json" -H "X-Internal-Token: XSWT-sdfgkfdsosiojnovnonqklpsdfsdfgnjsdfbknfvbvklcfdfg" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5Mzg0NzY0MiwianRpIjoiNzdiNGUxMWYtYTYwZC00MTY2LTk3N2YtMzA1NjUwM2EwMmY1IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjIiLCJuYmYiOjE3OTM4NDc2NDIsImNzcmYiOiJlNDEzZDJiYS1hNDk1LTQ4NDYtODBmYi0xNWFmODVhODZhODYiLCJleHAiOjE3OTM4NDg1NDIsImlzX2FkbWluIjpmYWxzZX0.u9_1yU5HlMpFS_VJEJpqgE8LNuO-jcCvelDIIj_lI17"
HTTP/1.1 422 UNPROCESSABLE ENTITY
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Thu, 05 Nov 2026 03:07:22 GMT
Content-Type: application/json
Content-Length: 38
Connection: close

{
  "msg": "Invalid crypto padding"
}


3. Valid JWT, valid internal token (success)
$ curl -i -X GET "http://localhost:5002/recipes/" -H "accept: application/json" -H "X-Internal-Token: XSWT-sdfgkfdsosiojnovnonqklpsdfsdfgnjsdfbknfvbvklcfdfg" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5Mzg0NzY0MiwianRpIjoiNzdiNGUxMWYtYTYwZC00MTY2LTk3N2YtMzA1NjUwM2EwMmY1IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjIiLCJuYmYiOjE3OTM4NDc2NDIsImNzcmYiOiJlNDEzZDJiYS1hNDk1LTQ4NDYtODBmYi0xNWFmODVhODZhODYiLCJleHAiOjE3OTM4NDg1NDIsImlzX2FkbWluIjpmYWxzZX0.u9_1yU5HlMpFS_VJEJpqgE8LNuO-jcCvelDIIj_lI10"
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Thu, 05 Nov 2026 03:01:19 GMT
Content-Type: application/json
Content-Length: 945
Connection: close

[
  {
    "id": 1,
    "user_id": 3,
    "title": "Shakshuka",
    "ingredients": "eggs, tomatoes, peppers, onion, cumin, paprika",
    "instructions": "Simmer the sauce, crack in the eggs, cover until just set.",
    "is_public": 1
  },
  {
    "id": 2,
    "user_id": 1,
    "title": "Overnight oats",
    "ingredients": "rolled oats, milk, yogurt, chia seeds, honey",
    "instructions": "Stir everything together and refrigerate overnight.",
    "is_public": 1
  },
  {
    "id": 4,
    "user_id": 2,
    "title": "Alice's Homestyle Fried Chicken",
    "ingredients": "Chicken and stuff",
    "instructions": "Put other stuff on chicken and cook it.",
    "is_public": 1
  },
  {
    "id": 5,
    "user_id": 2,
    "title": "Grilled Cheese",
    "ingredients": "bread, cheese, butter",
    "instructions": "Place cheese inside two slices of bread and using butter, grill until cheese is melted and bread is brown.",
    "is_public": 1
  }
]
