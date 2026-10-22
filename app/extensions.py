# app/extensions.py

from flask_caching import Cache
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

dba = SQLAlchemy()
migrate = Migrate()
cache = Cache()
