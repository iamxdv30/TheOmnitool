import os
os.environ["FLASK_APP"] = "main.py"

from flask import Flask, request, get_flashed_messages
from flask_migrate import Migrate
from jinja2 import FileSystemLoader, ChoiceLoader

# Import routes
from routes.auth_routes import auth
from routes.user_routes import user
from routes.admin_routes import admin
from routes.tool_routes import tool

# Import models
from model.model import db

import logging

# Factory function to create a Flask app
def create_app():
    app = Flask(__name__, static_folder="static")
    app.config['METHOD_OVERRIDE_EXCEPTIONS'] = True

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(admin)
    app.register_blueprint(tool)
    
    # Custom method override
    @app.before_request
    def handle_method_override():
        if request.form and '_method' in request.form:
            method = request.form['_method'].upper()
            if method in ['PUT', 'DELETE', 'PATCH']:
                request.environ['REQUEST_METHOD'] = method

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"  # Use SQLite for simplicity
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Disable tracking modifications
    app.config["SECRET_KEY"] = "XDVsuperuser@1993"  # Set a secret key for session management

    # Initialize the db with the app
    db.init_app(app)

    # Initialize the migrate with the app and db
    Migrate(app, db)

    # Set up Jinja2 to load templates from both directories
    with app.app_context():
        app.jinja_env.loader = ChoiceLoader([
            FileSystemLoader("Tools/templates"),  # Load templates from Tools/templates
            FileSystemLoader("templates"),  # Load templates from the model templates directory
        ])

        # Create all tables in the database
        db.create_all()  # Create the tables based on models

    # Set the template folder to the correct path
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    @app.context_processor
    def inject_flashed_messages():
        return dict(messages=get_flashed_messages(with_categories=True))

    return app

# The 'if __name__' block is still required to run the app
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)