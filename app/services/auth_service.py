# app/services/auth_service.py
from sqlite3 import IntegrityError

from werkzeug.security import check_password_hash, generate_password_hash

from app.db import user_to_dict
from app.extensions import dba
from app.models.recipes import User


def authenticate_user(username: str, password: str):
    """
    Return a user row (or dict) if credentials are valid, otherwise None.
    """
    user = (
        User.query
        .filter(
            User.username == username
        )
        .first()
    )
    if user and check_password_hash(user.password_hash, password):
        return user_to_dict(user)
    return None

def register_user(username, password, email, phone):
    """
    Return a tuple with success flag and message
    """
    # Hash the password before storing it in the database
    password_hash = generate_password_hash(password)

    user = User(
        username=username,
        email=email,
        phone=phone,
        password_hash=password_hash,
        is_admin=False,
    )
    dba.session.add(user)

    try:
        dba.session.commit()
    except IntegrityError:
        return False, "username taken"
    return True, f"registered {username}"

def list_users_for_user(current_user_id, is_admin):
    if is_admin:
        users = (
            User.query
            .order_by(User.username)
            .all()
        )
        return [user_to_dict(u) for u in users]
    else:
        users = (
            User.query
            .filter(
                User.id == current_user_id
            )
            .order_by(User.username)
            .all()
        )
        return [user_to_dict(u) for u in users]

def update_user_for_user(current_user_id, is_admin, user_id, data):
    # verify we have fields to update
    fields = []
    for column in ("password", "email", "phone", is_admin):
        if column in data:
            fields.append(f"{column}, ")
    if not fields:
        return None, "nothing_to_update"

    # Fetch user
    user = (
        User.query
        .filter(
            User.id == user_id
        )
        .first()
    )

    # Does the user exist?
    if not user:
        return None, "user_not_found"

    # check ownership for update operation - only the owner or an admin can update a user
    if str(user.id) != str(current_user_id) and is_admin is not True:
        return None, "access_denied"

    if "password" in data:
        # check for blank password
        if data["password"].strip() == "":
            # if password is blank, return the error
            return None, "password_is_empty"
        user.password_hash = generate_password_hash(data["password"])
    if "email" in data:
        user.email = data["email"]
    if "phone" in data:
        user.phone = data["phone"]
    if "is_admin" in data and is_admin is True:
        # only update is_admin if current user is admin
        # do not report the error, just silently fail to update
        # so as not to give a potential attacker more information
        user.is_admin = 1 if data["is_admin"] else 0

    try:
        # commit changes
        dba.session.commit()
    except IntegrityError:
        # rollback on error
        dba.session.rollback()

        # Investigate the reason for the error and report
        if data.get("email") and data.get("phone"):
            return user_to_dict(user), "duplicate_data"
        elif data.get("email"):
            return user_to_dict(user), "duplicate_email"
        elif data.get("phone"):
            return user_to_dict(user), "duplicate_phone"

    return user_to_dict(user), None

def delete_user_for_user(current_user_id, is_admin, user_id, data):
    user = (
        User.query
        .filter(
            User.id == user_id
        )
        .first()
    )
    if not user:
        return "user_not_found"

    if not is_admin:
        return "access_denied"

    dba.session.delete(user)

    # commit changes
    dba.session.commit()

    return None  # success