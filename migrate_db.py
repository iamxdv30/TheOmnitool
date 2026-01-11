"""
Database Migration Script using Flask-Migrate (Alembic)

Usage:
    Local: python migrate_db.py
    Heroku: python migrate_db.py

This script applies pending migration scripts to the database.
It is safe for both SQLite (Development) and PostgreSQL (Staging/Production).
"""

import os
import logging
from flask_migrate import upgrade
from main import create_app
from sync_tools import sync_tools  # Import the sync logic

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("migrate_db")

def run_migrations():
    """
    Applies database migrations using Flask-Migrate (Alembic).
    Then syncs tool definitions (Data Migration).
    """
    environment = os.getenv("FLASK_ENV", "development")
    logger.info(f"Starting migration for environment: {environment}")

    try:
        # Create Flask application context
        app = create_app()
        
        with app.app_context():
            # Get the database URL for logging (masking sensitive info)
            db_url = app.config.get("SQLALCHEMY_DATABASE_URI", "")
            if "@" in db_url:
                # Mask password in PostgreSQL URLs
                parts = db_url.split("@")
                user_pass = parts[0].split("//")[1].split(":")
                masked_url = db_url.replace(user_pass[1], "***")
            else:
                masked_url = db_url
            
            logger.info(f"Target Database: {masked_url}")

            # 1. SCHEMA MIGRATION (Tables/Columns)
            # Flask-Migrate/Alembic is idempotent: it checks the version table first.
            logger.info("[STEP 1] Checking for Schema Changes...")
            try:
                upgrade()
                logger.info("Schema check complete (Any pending migrations applied).")
            except Exception as e:
                logger.error(f"Schema migration error: {e}")
                raise

            # 2. DATA MIGRATION (Tools/Rows)
            # This runs our smart sync which only updates if data changed.
            logger.info("[STEP 2] Verifying Tool Definitions...")
            sync_tools()
            
            logger.info("Smart Migration completed successfully.")

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        # Re-raise to ensure the deployment fails if migration fails
        raise

if __name__ == "__main__":
    run_migrations()
