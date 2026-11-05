
# app/services/rating_service.py

from flask import current_app
from sqlalchemy import func

from app.db import rating_to_dict
from app.extensions import dba
from app.models.recipes import Rating


def rate_recipe_for_user(recipe_id: int, user_id: int, score: int):
    # fetch rating
    rating = (
        Rating.query
        .filter(
            Rating.recipe_id == recipe_id,
            Rating.user_id == user_id
        )
        .first()
    )
    # if found, then update
    if rating:
        rating.score = score
        rating.comment = None

    # if not found, then add
    if not rating:
        rating = Rating(
            user_id=user_id,
            recipe_id=recipe_id,
            score=score,
            comment=None,
        )
        dba.session.add(rating)

    try:
        # commit add / update
        dba.session.commit()
        # if commit succeeds, use a single aggregation query
        # to calculate values
        # Using the query puts the work on the database
        result = (
            dba.session.query(
                func.avg(Rating.score).label("average_score"),
                func.count(Rating.id).label("ratings_count")
            )
            .filter(
                Rating.recipe_id == recipe_id,
                Rating.score > 0
            )
            .first()
        )

        # Access the calculated values safely
        average_score = float(result.average_score) if result.average_score else 0.0
        ratings_count = result.ratings_count or 0
        # convert to dict and add the aggregate values
        rating_data = rating_to_dict(rating)
        rating_data["average_score"] = average_score
        rating_data["ratings_count"] = ratings_count
        return rating_data, None
    except Exception as e:  # noqa: BLE001
        # this will not be an IntegrityError, this is unexpected
        # rollback the transaction
        dba.session.rollback()
        if current_app.debug:
            print(f"DEBUG: Error occurred rating a recipe, {e}")
        # return the error
        return None, "unknown error"
