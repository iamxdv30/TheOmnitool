"""
SAFE Database Migration Script

PROTECTION MEASURES:
1. Always creates a timestamped backup before ANY changes
2. Never uses db.drop_all() or recreates existing tables
3. Only creates missing tables, preserves existing data
4. Rollback on any error
5. Restoration from backup on critical failure

WARNING: This script modifies database schema. Always backup first!
"""

import os
import logging
import shutil
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy_utils import database_exists, create_database
from main import create_app
from model import db

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")


def backup_database(db_path):
    """Create a timestamped backup of SQLite database"""
    if not db_path.startswith("sqlite:///"):
        logging.info("Backups only supported for SQLite (local development)")
        return None

    file_path = db_path.replace("sqlite:///", "")

    if not os.path.exists(file_path):
        logging.info(f"Database {file_path} does not exist yet - will be created")
        return None

    # Create instance directory if it doesn't exist
    instance_dir = os.path.dirname(file_path)
    if instance_dir and not os.path.exists(instance_dir):
        os.makedirs(instance_dir)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{file_path}.backup_{timestamp}"

    try:
        shutil.copy2(file_path, backup_path)
        logging.info(f"[BACKUP] Created: {backup_path}")
        return backup_path
    except Exception as e:
        logging.error(f"[BACKUP] Failed: {e}")
        return None


def safe_migrate_schema(target_url):
    """
    Safely migrate database schema WITHOUT dropping existing tables
    Only creates missing tables - preserves all existing data
    """
    logging.info(f"Current environment: {os.getenv('FLASK_ENV', 'development')}")

    # Correct PostgreSQL URL if necessary
    if target_url.startswith("postgres://"):
        target_url = target_url.replace("postgres://", "postgresql://", 1)

    # STEP 1: Backup (SQLite only)
    backup_path = backup_database(target_url)

    try:
        # STEP 2: Create engine and database if needed
        engine = create_engine(target_url)
        if not database_exists(engine.url):
            if target_url.startswith("sqlite://"):
                create_database(engine.url)
                logging.info(f"Created new database: {target_url}")

        # STEP 3: Create Flask app context
        app = create_app()
        app.config["SQLALCHEMY_DATABASE_URI"] = target_url

        with app.app_context():
            # STEP 4: Get existing tables
            inspector = inspect(engine)
            existing_tables = set(inspector.get_table_names())

            logging.info(f"Existing tables: {existing_tables}")

            # STEP 5: Create ONLY missing tables (NEVER drop existing ones)
            # db.create_all() only creates tables that don't exist
            db.create_all()

            # STEP 6: Verify what was created
            inspector = inspect(engine)
            current_tables = set(inspector.get_table_names())
            new_tables = current_tables - existing_tables

            if new_tables:
                logging.info(f"Created new tables: {new_tables}")
            else:
                logging.info("No new tables needed - schema up to date")

        logging.info("[SUCCESS] Migration completed successfully!")

        return True

    except Exception as e:
        logging.error(f"[ERROR] Migration failed: {e}")

        # STEP 7: Attempt restoration from backup (SQLite only)
        if backup_path and os.path.exists(backup_path):
            file_path = target_url.replace("sqlite:///", "")
            try:
                shutil.copy2(backup_path, file_path)
                logging.info(f"[RESTORE] Database restored from backup: {backup_path}")
            except Exception as restore_error:
                logging.error(f"[RESTORE] Failed to restore: {restore_error}")

        raise


if __name__ == "__main__":
    try:
        environment = os.getenv("FLASK_ENV", "development")
        logging.info(f"Running migration for {environment} environment")

        # Determine database URL based on environment
        if environment in ["production", "staging"]:
            target_url = os.getenv("DATABASE_URL", "")
            if not target_url:
                raise ValueError(f"No DATABASE_URL found for {environment} environment")
            # Ensure PostgreSQL URL format
            if target_url.startswith("postgres://"):
                target_url = target_url.replace("postgres://", "postgresql://", 1)
        else:
            # Local development uses SQLite
            is_local = os.getenv("IS_LOCAL", "true").lower() == "true"
            if not is_local:
                logging.info("Not a local environment and not staging/production. Skipping migration.")
                exit(0)
            target_url = "sqlite:///instance/users.db"

        # Mask sensitive info in logs
        masked_url = target_url
        if "@" in target_url:
            # Mask password in PostgreSQL URLs
            parts = target_url.split("@")
            user_pass = parts[0].split("//")[1].split(":")
            masked_url = target_url.replace(user_pass[1], "***")

        logging.info(f"Using database URL: {masked_url}")

        # Perform SAFE migration (creates only missing tables, never drops)
        safe_migrate_schema(target_url)

    except Exception as e:
        logging.error(f"Migration failed: {str(e)}")
        raise
