from app.extensions import dba


class Recipe(dba.Model):
    __tablename__ = "recipes"
    id = dba.Column(dba.Integer, primary_key=True)
    user_id = dba.Column(dba.Integer, dba.ForeignKey("users.id"), nullable=False)
    title = dba.Column(dba.Text, nullable=False, unique=True)
    ingredients = dba.Column(dba.Text, nullable=False)
    instructions = dba.Column(dba.Text, nullable=False, server_default="")
    is_public = dba.Column(dba.Integer, nullable=False, server_default="1")
    # RELATIONSHIP: to the owning user
    user = dba.relationship("User", back_populates="recipes")
    # RELATIONSHIP: collection of this recipe's ratings
    ratings = dba.relationship("Rating", back_populates="recipe")

class User(dba.Model):
    __tablename__ = "users"
    id = dba.Column(dba.Integer, primary_key=True)
    username = dba.Column(dba.Text, nullable=False, unique=True)
    email = dba.Column(dba.Text, nullable=False, unique=True)
    phone = dba.Column(dba.Text, nullable=False, unique=True)
    password_hash = dba.Column(dba.Text, nullable=False, server_default="")
    is_admin = dba.Column(dba.Integer, nullable=False, server_default="0")
    # NEW: nullable location
    location = dba.Column(dba.String(120), nullable=True)
    # RELATIONSHIP: collection of this user's recipes
    recipes = dba.relationship("Recipe", back_populates="user")
    # RELATIONSHIP: collection of this user's ratings
    ratings = dba.relationship("Rating", back_populates="user")

class Rating(dba.Model):
    # NEW: ratings model / table
    __tablename__ = "ratings"
    id = dba.Column(dba.Integer, primary_key=True)
    user_id = dba.Column(dba.Integer, dba.ForeignKey("users.id"), nullable=False)
    recipe_id = dba.Column(dba.Integer, dba.ForeignKey("recipes.id"), nullable=False)
    score = dba.Column(dba.Integer, nullable=False, server_default="1")
    comment = dba.Column(dba.String(120), nullable=True)
    # RELATIONSHIP: to the owning user
    user = dba.relationship("User", back_populates="ratings")
    # RELATIONSHIP: to the owning recipe
    recipe = dba.relationship("Recipe", back_populates="ratings")
