# app/models/recipes.py
from app.extensions import dba


class Recipe(dba.Model):
    __tablename__ = "recipes"
    id = dba.Column(dba.Integer, primary_key=True)
    user_id = dba.Column(dba.Integer, nullable=False)
    title = dba.Column(dba.Text, nullable=False, unique=True)
    ingredients = dba.Column(dba.Text, nullable=False)
    instructions = dba.Column(dba.Text, nullable=False, server_default="")
    is_public = dba.Column(dba.Integer, nullable=False, server_default="1")
    # RELATIONSHIP: collection of this recipe's ratings
    ratings = dba.relationship("Rating", back_populates="recipe")

class Rating(dba.Model):
    __tablename__ = "ratings"
    id = dba.Column(dba.Integer, primary_key=True)
    user_id = dba.Column(dba.Integer, nullable=False)
    recipe_id = dba.Column(dba.Integer, dba.ForeignKey("recipes.id"), nullable=False)
    score = dba.Column(dba.Integer, nullable=False, server_default="1")
    comment = dba.Column(dba.String(120), nullable=True)
    # RELATIONSHIP: to the owning recipe
    recipe = dba.relationship("Recipe", back_populates="ratings")
