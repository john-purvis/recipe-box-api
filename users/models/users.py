# users/models/users.py
from users.extensions import user_db


class User(user_db.Model):
    __tablename__ = "users"
    id = user_db.Column(user_db.Integer, primary_key=True)
    username = user_db.Column(user_db.Text, nullable=False, unique=True)
    email = user_db.Column(user_db.Text, nullable=False, unique=True)
    phone = user_db.Column(user_db.Text, nullable=False, unique=True)
    password_hash = user_db.Column(user_db.Text, nullable=False, server_default="")
    is_admin = user_db.Column(user_db.Integer, nullable=False, server_default="0")
    location = user_db.Column(user_db.String(120), nullable=True)
