# recipes/extensions.py

from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

# Define the convention template
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Instantiate SQLAlchemy WITH the metadata/convention right away
metadata = MetaData(naming_convention=convention)

recipe_db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
cache = Cache()
limiter = Limiter(
    get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://", # Uses in-memory storage (fine for single-process development)
)
