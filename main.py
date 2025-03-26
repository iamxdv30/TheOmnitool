import os
from urllib.parse import urlparse
from flask import Flask, request, get_flashed_messages, redirect, abort
from flask_migrate import Migrate
from jinja2 import FileSystemLoader, ChoiceLoader
from routes.auth_routes import auth
from routes.user_routes import user
from routes.admin_routes import admin
from routes.tool_routes import tool
from model.model import db
import re
import logging
from model.model import User, Admin, SuperAdmin, Tool, ToolAccess
from datetime import timedelta


#New imports as of October 12, 2024
from routes.contact_routes import contact, configure_mail
from dotenv import load_dotenv



# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables from .env
load_dotenv()

# Factory function to create a Flask app


def configure_session(app):
    # Configure session to expire when browser closes
    app.config.update(
        # Session will expire when browser closes
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),  # Backup expiry time
        SESSION_PERMANENT=False,  # This ensures cookie expires when browser closes
        SESSION_COOKIE_SECURE=True,  # Only send cookie over HTTPS
        SESSION_COOKIE_HTTPONLY=True,  # Prevent JavaScript access to session cookie
        SESSION_COOKIE_SAMESITE='Lax'  # Protect against CSRF
    )

def create_app():
    # Determine if we're running locally
    is_local = os.environ.get('IS_LOCAL', 'true').lower() == 'true'
    environment = os.getenv('FLASK_ENV', 'development')

    logging.info(f"Current environment: {environment}")

    app = Flask(__name__, static_folder="static")

    # Configure session settings
    configure_session(app)

    # Configure Flask-Mail
    configure_mail(app)

    # Configure logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.ERROR)
        app.logger.info('Application startup')

    # Set the secret key based on the environment
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key_for_development')
    logging.info(f"Using secret key: {app.config['SECRET_KEY']}")

    # Database configuration
    if is_local:
        database_url = 'sqlite:///users.db'
    else:
        # Use DATABASE_URL provided by Heroku
        database_url = os.getenv('DATABASE_URL', '')

    # Replace deprecated PostgreSQL connection string format
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the db and migrations
    db.init_app(app)
    migrate = Migrate(app, db)  # Ensure that Migrate is properly set up

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(admin)
    app.register_blueprint(tool)
    app.register_blueprint(contact)

    @app.route("/environment")
    def show_environment():
        if environment == "production":
            abort(404)
        db_url = app.config["SQLALCHEMY_DATABASE_URI"]
        # Mask the password in the DB URL
        masked_db_url = re.sub(r"://[^:]+:[^@]+@", "://****:****@", db_url)
        return f"Current environment: {environment}<br>Database URL: {masked_db_url}"

    # Custom method override handling
    @app.before_request
    def handle_method_override():
        if request.form and "_method" in request.form:
            method = request.form["_method"].upper()
            if method in ["PUT", "DELETE", "PATCH"]:
                request.environ["REQUEST_METHOD"] = method

    # Ensure HTTPS is recognized and redirects are properly handled
    @app.before_request
    def handle_headers():
        # Recognize HTTPS if behind a proxy
        if request.headers.get("X-Forwarded-Proto") == "https":
            request.environ["wsgi.url_scheme"] = "https"

        # Use X-Forwarded-Host if present for host header
        forwarded_host = request.headers.get("X-Forwarded-Host")
        if forwarded_host:
            request.environ["HTTP_HOST"] = forwarded_host

        # Redirect to HTTPS in production
        if environment == "production" and not request.is_secure:
            url = request.url.replace("http://", "https://", 1)
            return redirect(url, code=301)

    # Add security headers
    @app.after_request
    def add_security_headers(response):
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com;"
        )
        return response

    # Configure Jinja2 template loading
    with app.app_context():
        app.jinja_env.loader = ChoiceLoader([
            FileSystemLoader("Tools/templates"),  # Load templates from Tools/templates
            FileSystemLoader("templates"),  # Load templates from the model templates directory
        ])

    # Inject flashed messages for templates
    @app.context_processor
    def inject_flashed_messages():
        return dict(messages=get_flashed_messages(with_categories=True))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
