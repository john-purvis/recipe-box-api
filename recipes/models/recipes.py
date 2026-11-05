# recipes/models/recipes.py
from recipes.extensions import recipe_db


class Recipe(recipe_db.Model):
    __tablename__ = "recipes"
    id = recipe_db.Column(recipe_db.Integer, primary_key=True)
    user_id = recipe_db.Column(recipe_db.Integer, nullable=False)
    title = recipe_db.Column(recipe_db.Text, nullable=False, unique=True)
    ingredients = recipe_db.Column(recipe_db.Text, nullable=False)
    instructions = recipe_db.Column(recipe_db.Text, nullable=False, server_default="")
    is_public = recipe_db.Column(recipe_db.Integer, nullable=False, server_default="1")
    # RELATIONSHIP: collection of this recipe's ratings
    ratings = recipe_db.relationship("Rating", back_populates="recipe")

class Rating(recipe_db.Model):
    __tablename__ = "ratings"
    id = recipe_db.Column(recipe_db.Integer, primary_key=True)
    user_id = recipe_db.Column(recipe_db.Integer, nullable=False)
    recipe_id = recipe_db.Column(recipe_db.Integer, recipe_db.ForeignKey("recipes.id"), nullable=False)
    score = recipe_db.Column(recipe_db.Integer, nullable=False, server_default="1")
    comment = recipe_db.Column(recipe_db.String(120), nullable=True)
    # RELATIONSHIP: to the owning recipe
    recipe = recipe_db.relationship("Recipe", back_populates="ratings")
