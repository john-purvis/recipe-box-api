1. POST to /login and response to get JWT needed for create_recipe
$ curl -X POST "http://localhost:5000/auth/login" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"username\": \"jackie\", \"password\": \"winston\"}"
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MjYzMzcxMiwianRpIjoiMGY3NzgzYWQtYjE0Yi00NDM4LWIwOTgtNGEzNjgyMDEwZWM0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjUiLCJuYmYiOjE3OTI2MzM3MTIsImNzcmYiOiJhOGMxOGQyOS1lMWE0LTQzMWQtODE1Ny1iYjQ3NTA4OGFkZjkiLCJleHAiOjE3OTI2MzQ2MTIsImlzX2FkbWluIjpmYWxzZX0.1M5xFLHOH0pfo0X_tLsq_xXiYKSIv5Qjawk1T8NzFTc"
}

2. First GET to /recipes and response from list_recipes (not cached)
$ time curl -s -i -X GET "http://localhost:5000/recipes/"
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Thu, 22 Oct 2026 01:49:11 GMT
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

real    0m0.374s
user    0m0.031s
sys     0m0.015s

3. Second GET to /recipes and response from list_recipes (cached)
$ time curl -s -i -X GET "http://localhost:5000/recipes/"
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Thu, 22 Oct 2026 01:49:13 GMT
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

real    0m0.359s
user    0m0.000s
sys     0m0.031s

4. POST to /recipes and response from create_recipe (with delete_memoized)
$ curl -X POST "http://localhost:5000/recipes/" -H "accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MjYzMzcxMiwianRpIjoiMGY3NzgzYWQtYjE0Yi00NDM4LWIwOTgtNGEzNjgyMDEwZWM0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjUiLCJuYmYiOjE3OTI2MzM3MTIsImNzcmYiOiJhOGMxOGQyOS1lMWE0LTQzMWQtODE1Ny1iYjQ3NTA4OGFkZjkiLCJleHAiOjE3OTI2MzQ2MTIsImlzX2FkbWluIjpmYWxzZX0.1M5xFLHOH0pfo0X_tLsq_xXiYKSIv5Qjawk1T8NzFTc" -d '
{
  "title": "Spaghetti Bolognese",
  "description": "Classic meat sauce over pasta",
  "ingredients": "spaghetti, ground beef, tomato sauce, onion, garlic",
  "instructions": "Boil pasta, Cook beef, Add sauce, Combine and serve"
}'
{
  "id": 6,
  "user_id": 5,
  "title": "Spaghetti Bolognese",
  "ingredients": "spaghetti, ground beef, tomato sauce, onion, garlic",
  "instructions": "Boil pasta, Cook beef, Add sauce, Combine and serve",
  "is_public": 1
}

5. Third GET to /recipes and response from list_recipes (not cached)
$ time curl -s -i -X GET "http://localhost:5000/recipes/"                                           HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Thu, 22 Oct 2026 01:49:21 GMT
Content-Type: application/json
Content-Length: 1189
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
  },
  {
    "id": 6,
    "user_id": 5,
    "title": "Spaghetti Bolognese",
    "ingredients": "spaghetti, ground beef, tomato sauce, onion, garlic",
    "instructions": "Boil pasta, Cook beef, Add sauce, Combine and serve",
    "is_public": 1
  }
]

real    0m0.362s
user    0m0.015s
sys     0m0.031s
