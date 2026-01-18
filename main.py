import os
from urllib.parse import urlparse
from flask import Flask, request, get_flashed_messages, redirect, abort
from flask_migrate import Migrate
from jinja2 import FileSystemLoader, ChoiceLoader
import re
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables FIRST (before any module imports that might need them)
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


class NoiseFilter(logging.Filter):
    """Filter out noisy logs from file handler only (werkzeug HTTP requests, etc.)"""
    
    NOISY_LOGGERS = {'werkzeug', 'urllib3', 'sqlalchemy.engine'}
    
    def filter(self, record):
        # Allow WARNING and above from noisy loggers, block INFO/DEBUG
        if record.name in self.NOISY_LOGGERS:
            return record.levelno >= logging.WARNING
        return True


def setup_logging():
    """Setup centralized logging with automatic 30-day rotation"""
    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(filename)s:%(lineno)d]"
    )
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # TimedRotatingFileHandler - rotates daily, keeps 30 days of logs
    file_handler = TimedRotatingFileHandler(
        'logs/app.log',
        when='midnight',      # Rotate at midnight
        interval=1,           # Every 1 day
        backupCount=30,       # Keep 30 days of logs
        encoding='utf-8'
    )
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)
    file_handler.addFilter(NoiseFilter())  # Filter noisy logs from FILE only
    
    # Console handler for development - NO filter, shows everything including server URL
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)
    
    # Get root logger and configure it
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear any existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.info("Centralized logging initialized - logs will rotate daily, keeping 30 days")


# Initialize logging BEFORE importing blueprints
setup_logging()

# Now import blueprints (they will use the centralized logging)
from routes.auth_routes import auth
from routes.user_routes import user
from routes.admin_routes import admin
from routes.tool_routes import tool
from routes.contact_routes import contact, configure_mail, mail
from routes.health_routes import health
from routes.api import api_bp, register_api_routes
from model import db
from services import init_email_service




# Debug: Print environment variables
print("DEBUG: FLASK_ENV =", os.getenv('FLASK_ENV', 'development'))
print("DEBUG: IS_LOCAL =", os.getenv('IS_LOCAL', 'true'))

# Factory function to create a Flask app


def configure_session(app):
    is_local = os.getenv('IS_LOCAL', 'true').lower() == 'true'
    
    # Configure session to expire when browser closes
    app.config.update(
        # Session will expire when browser closes
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),  # Backup expiry time
        SESSION_PERMANENT=False,  # This ensures cookie expires when browser closes
        SESSION_COOKIE_SECURE=not is_local,  # Only require HTTPS in production
        SESSION_COOKIE_HTTPONLY=True,  # Prevent JavaScript access to session cookie
        SESSION_COOKIE_SAMESITE='Lax'  # Protect against CSRF
    )

def get_version():
    try:
        with open('VERSION', 'r') as f:
            for line in f:
                if line.strip().startswith('Current Version:'):
                    return line.split(':')[1].strip()
            # Fallback to first line if format is unexpected
            f.seek(0)
            return f.readline().strip()
    except Exception as e:
        print(f"Error reading VERSION file: {e}")
        return "1.0.0"  # Fallback version

def create_app():
    # Determine if we're running locally
    is_local = os.environ.get('IS_LOCAL', 'true').lower() == 'true'
    environment = os.getenv('FLASK_ENV', 'development')
    
    # Initialize Flask app
    app = Flask(__name__, static_folder="static")
    
    # Store version in app config
    app.config['VERSION'] = get_version()
    
    # Make version available to all templates
    @app.context_processor
    def inject_version():
        return {'version': app.config['VERSION']}
        
    logging.info(f"Current environment: {environment}")

    # Configure session settings
    configure_session(app)

    # Configure Flask-Mail
    configure_mail(app)

    # Initialize the email service with Flask-Mail instance
    init_email_service(mail)

    # Set the secret key based on the environment
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key_for_development')
    logging.info(f"Using secret key: {app.config['SECRET_KEY']}")

    # Database configuration
    if is_local:
        # Local development: Use SQLite
        database_url = 'sqlite:///users.db'
        logging.info(f"Using local SQLite database: {database_url}")
    else:
        # Production/Staging: Use DATABASE_URL from Heroku
        database_url = os.getenv('DATABASE_URL', '')

        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set in production!")

        # Replace deprecated PostgreSQL connection string format
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        # Log database connection (mask password)
        masked_db_url = re.sub(r"://[^:]+:[^@]+@", "://****:****@", database_url)
        logging.info(f"Using PostgreSQL database: {masked_db_url}")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the db and migrations
    db.init_app(app)
    migrate = Migrate(app, db, render_as_batch=True)  # Enable batch mode for SQLite

    # SAFETY: Validate database on startup
    from utils.db_safety import validate_database_on_startup
    validate_database_on_startup(app)

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(admin)
    app.register_blueprint(tool, url_prefix='/tools')
    app.register_blueprint(contact)
    app.register_blueprint(health)  # Health check endpoints

    # Register API blueprint (JSON endpoints for Next.js frontend)
    register_api_routes()  # Register sub-routes first
    app.register_blueprint(api_bp)  # Register main API blueprint at /api/v1

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
        is_local = os.getenv('IS_LOCAL', 'true').lower() == 'true'
        
        # Skip HTTPS checks in local development
        if is_local:
            return None
            
        # Production HTTPS handling
        if request.headers.get("X-Forwarded-Proto") == "https":
            request.environ["wsgi.url_scheme"] = "https"

        # Use X-Forwarded-Host if present for host header
        forwarded_host = request.headers.get("X-Forwarded-Host")
        if forwarded_host:
            request.environ["HTTP_HOST"] = forwarded_host

        # Redirect to HTTPS in production
        if not request.is_secure:
            url = request.url.replace("http://", "https://", 1)
            return redirect(url, code=301)

    # Add security headers
    @app.after_request
    def add_security_headers(response):
        is_local = os.getenv('IS_LOCAL', 'true').lower() == 'true'

        if not is_local:  # Only add strict security headers in production
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.google.com https://www.gstatic.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "frame-src https://www.google.com; "
                "img-src 'self' data:;"
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
    is_local = os.getenv('IS_LOCAL', 'true').lower() == 'true'
    host = '127.0.0.1' if is_local else '0.0.0.0'
    ssl_context = None if is_local else 'adhoc'  # Use HTTP for local, HTTPS for production
    
    app.run(
        host=host,
        port=int(os.environ.get('PORT', 5000)),
        debug=True,
        ssl_context=ssl_context
    )
