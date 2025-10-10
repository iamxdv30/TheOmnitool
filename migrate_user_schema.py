"""
Migration script to update User schema from old to new format
- Combines fname/lname into name
- Adds email verification fields
- Adds OAuth support fields
- Adds account management fields
"""

import os
os.environ['FLASK_ENV'] = 'development'
os.environ['IS_LOCAL'] = 'true'

from main import create_app
from model import db
from sqlalchemy import text, inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_schema():
    """Migrate database schema from old to new format"""
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        existing_columns = [col['name'] for col in inspector.get_columns('users')]

        logger.info(f"Existing columns: {existing_columns}")

        # Check if migration is needed
        if 'name' in existing_columns:
            logger.info("Migration already completed - 'name' column exists")
            return

        if 'fname' not in existing_columns:
            logger.error("Old schema not found - cannot migrate")
            return

        logger.info("Starting schema migration...")

        try:
            # Add new columns
            logger.info("Adding new columns...")

            with db.engine.begin() as conn:
                # Add name column (temporary nullable)
                conn.execute(text("ALTER TABLE users ADD COLUMN name VARCHAR(100)"))

                # Combine fname and lname into name
                logger.info("Migrating user names...")
                conn.execute(text("""
                    UPDATE users
                    SET name = fname || ' ' || lname
                    WHERE name IS NULL
                """))

                # Add authentication columns
                logger.info("Adding authentication columns...")
                conn.execute(text("ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 0"))
                conn.execute(text("ALTER TABLE users ADD COLUMN email_verification_token VARCHAR(255)"))
                conn.execute(text("ALTER TABLE users ADD COLUMN email_verification_sent_at DATETIME"))

                # Add OAuth columns
                logger.info("Adding OAuth columns...")
                conn.execute(text("ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(50)"))
                conn.execute(text("ALTER TABLE users ADD COLUMN oauth_id VARCHAR(255)"))
                conn.execute(text("ALTER TABLE users ADD COLUMN requires_password_setup BOOLEAN DEFAULT 0"))

                # Add account management columns
                logger.info("Adding account management columns...")
                conn.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME"))
                conn.execute(text("ALTER TABLE users ADD COLUMN updated_at DATETIME"))
                conn.execute(text("ALTER TABLE users ADD COLUMN last_login DATETIME"))
                conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1"))

                # Set defaults for existing users
                logger.info("Setting defaults for existing users...")
                conn.execute(text("""
                    UPDATE users
                    SET
                        email_verified = 1,
                        oauth_provider = 'manual',
                        is_active = 1,
                        created_at = datetime('now'),
                        updated_at = datetime('now')
                    WHERE email_verified IS NULL
                """))

                # Make password nullable for OAuth users (future)
                # SQLite doesn't support making columns nullable, so we'll handle this in application logic

                logger.info("Schema migration completed successfully!")
                logger.info("NOTE: Old columns (fname, lname, address, city, state, zip) are kept for backward compatibility")

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise

if __name__ == "__main__":
    migrate_schema()
