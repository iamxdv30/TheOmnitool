import os
os.environ["FLASK_APP"] = "main.py"

from flask import Flask, request, get_flashed_messages, redirect
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
    app.config['PREFERRED_URL_SCHEME'] = 'https'

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

    @app.before_request
    def handle_headers():
        # Ensure HTTPS is recognized when behind a proxy
        if request.headers.get('X-Forwarded-Proto') == 'https':
            request.environ['wsgi.url_scheme'] = 'https'
        
        # Instead of modifying request.host, we'll use X-Forwarded-Host when present
        forwarded_host = request.headers.get('X-Forwarded-Host')
        if forwarded_host:
            # Store the forwarded host in the request environment
            request.environ['HTTP_HOST'] = forwarded_host

        # Optionally, enforce HTTPS
        if not request.is_secure:
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
        
    @app.after_request
    def add_security_headers(response):
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;"
        return response

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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))