# tests/manual_test.py
from dotenv import load_dotenv
load_dotenv()

from app import create_app

app = create_app("testing")
print("DATABASE:", app.config["DATABASE"])

client = app.test_client()

# 1. Register a user
resp = client.post(
    "/auth/register",
    json={"username": "testuser", "email": "testuser@recipe_box.com", "phone": "9998887777", "password": "secret"}
)
print("REGISTER:", resp.status_code, resp.json)

# 2. Try login with same credentials
resp = client.post(
    "/auth/login",
    json={"username": "testuser", "password": "secret"}
)
print("LOGIN:", resp.status_code, resp.json)
