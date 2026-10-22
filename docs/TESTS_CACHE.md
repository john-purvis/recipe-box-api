admin super_secret_password_for_admin_user


time curl -s -i -X GET "http://localhost:5000/recipes/" -H "accept: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MjYxNjE0NywianRpIjoiN2RhMTUwODItYWViNi00OGMwLWIzYzktYjg4ZTI4ZmRmNmU0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjAiLCJuYmYiOjE3OTI2MTYxNDcsImNzcmYiOiIwNjk2ZTI1NS0wNTk5LTQ1OTItYTY5Yi1mOThiY2FmNzdkNWIiLCJleHAiOjE3OTI2MTcwNDcsImlzX2FkbWluIjp0cnVlfQ.vmM-Wkaw-it7iNkuQxrTK-MuUYXNzMdr7ZL3R-nUC5I"

time curl -s -i -X GET "http://localhost:5000/recipes/"


curl -X POST "http://localhost:5000/auth/login" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"username\": \"jackie\", \"password\": \"winston\"}"

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MjYyMDY0NywianRpIjoiYTA1ZDM1NjgtZDM5ZC00MTU4LWEyOWYtNDUwMTM2MmJiMDQ4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjUiLCJuYmYiOjE3OTI2MjA2NDcsImNzcmYiOiJlOGQ4YzJmMC00MDBjLTQ2OWEtYWU3Ny1kMzM5NzkzMWZjZjIiLCJleHAiOjE3OTI2MjE1NDcsImlzX2FkbWluIjpmYWxzZX0.KbmpObCeVx9C-9lgtbTuEbj0GJM0g7w4odKtlvIN_ew


curl -X POST "http://localhost:5000/recipes/" -H "accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MjYyMDY0NywianRpIjoiYTA1ZDM1NjgtZDM5ZC00MTU4LWEyOWYtNDUwMTM2MmJiMDQ4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjUiLCJuYmYiOjE3OTI2MjA2NDcsImNzcmYiOiJlOGQ4YzJmMC00MDBjLTQ2OWEtYWU3Ny1kMzM5NzkzMWZjZjIiLCJleHAiOjE3OTI2MjE1NDcsImlzX2FkbWluIjpmYWxzZX0.KbmpObCeVx9C-9lgtbTuEbj0GJM0g7w4odKtlvIN_ew" -d '
{
  "title": "Spaghetti Bolognese",
  "description": "Classic meat sauce over pasta",
  "ingredients": "spaghetti, ground beef, tomato sauce, onion, garlic",
  "instructions": "Boil pasta, Cook beef, Add sauce, Combine and serve"
}'

curl -X POST "http://localhost:5000/recipes/" -H "accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MjYyMDY0NywianRpIjoiYTA1ZDM1NjgtZDM5ZC00MTU4LWEyOWYtNDUwMTM2MmJiMDQ4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjUiLCJuYmYiOjE3OTI2MjA2NDcsImNzcmYiOiJlOGQ4YzJmMC00MDBjLTQ2OWEtYWU3Ny1kMzM5NzkzMWZjZjIiLCJleHAiOjE3OTI2MjE1NDcsImlzX2FkbWluIjpmYWxzZX0.KbmpObCeVx9C-9lgtbTuEbj0GJM0g7w4odKtlvIN_ew" -d '
{
  "title": "Veggie Stir Fry",
  "description": "Quick mixed vegetable stir fry",
  "ingredients": "broccoli, carrot, bell pepper, soy sauce, garlic",
  "instructions": "Chop veggies, Stir fry on high heat, Add sauce, Serve with rice"
}
'

curl -X POST "http://localhost:5000/recipes/" -H "accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MjYyMDY0NywianRpIjoiYTA1ZDM1NjgtZDM5ZC00MTU4LWEyOWYtNDUwMTM2MmJiMDQ4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjUiLCJuYmYiOjE3OTI2MjA2NDcsImNzcmYiOiJlOGQ4YzJmMC00MDBjLTQ2OWEtYWU3Ny1kMzM5NzkzMWZjZjIiLCJleHAiOjE3OTI2MjE1NDcsImlzX2FkbWluIjpmYWxzZX0.KbmpObCeVx9C-9lgtbTuEbj0GJM0g7w4odKtlvIN_ew" -d '
{
  "title": "Pancakes",
  "description": "Fluffy breakfast pancakes",
  "ingredients": "flour, milk, egg, baking powder, butter",
  "instructions": "Mix batter, Heat pan, Cook pancakes, Serve with syrup"
}
'
