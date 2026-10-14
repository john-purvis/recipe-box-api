"""
WSGI entry point for the Recipe Box API.

This file is the standard hook that production servers look for when they serve
Flask apps. WSGI servers such as Gunicorn or uWSGI import `application` and
then pass HTTP requests into it.

The important detail here is that this file can be executed directly as a script
or imported as a module. In either case, we need the Flask app object to be
available under the name `application`.
"""

import sys
from pathlib import Path

from flask import send_from_directory

# from app import app
from app import create_app

# use the factory in app to create the app
app = create_app()

# WSGI servers expect a variable called `application`.
# We expose the Flask instance under that standard name.
application = app

# Serve the static landing page stored in the app folder. The `index.html` file
# lives beside this script, so we build the directory path from the current file.
def _serve_index_html():
    """Return the static landing page for the root URL."""
    return send_from_directory(str(Path(__file__).resolve().parent), "index.html")

# If the app does not already define a homepage, add one. This keeps the root
# route available for the landing page while preserving any existing API routes.
if not any(rule.rule == "/" for rule in app.url_map.iter_rules()):
    @app.route("/")
    def landing_page():
        """Serve the project landing page at the home route."""
        return _serve_index_html()

# Also expose the same landing page directly at `/index.html`.
if not any(rule.rule == "/index.html" for rule in app.url_map.iter_rules()):
    @app.route("/index.html")
    def index_page():
        """Serve the landing page at the direct HTML filename."""
        return _serve_index_html()

# Development-server entry point. This block only runs when the file is executed
# directly, such as `python app/wsgi.py`.
if __name__ == "__main__":
    app.run(debug=True, port=5000)