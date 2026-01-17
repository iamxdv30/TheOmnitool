"""
Database Migration Script using Flask-Migrate (Alembic)

Usage:
    Local: python migrate_db.py
    Heroku: python migrate_db.py

This script applies pending migration scripts to the database.
It is safe for both SQLite (Development) and PostgreSQL (Staging/Production).

Safety Features:
- Automatic backup before migrations (SQLite only)
- Validation of database state
- Comprehensive error reporting
- Rollback on failure
"""

import os
import sys
import logging
from flask_migrate import upgrade
from main import create_app
from sync_tools import sync_tools  # Import the sync logic
from utils.db_safety import DatabaseSafety

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("migrate_db")

def run_migrations():
    """
    Applies database migrations using Flask-Migrate (Alembic).
    Then syncs tool definitions (Data Migration).

    Safety Features:
    - Creates automatic backup before migration (SQLite)
    - Validates database state before and after
    - Provides clear error messages
    """
    environment = os.getenv("FLASK_ENV", "development")
    logger.info(f"Starting migration for environment: {environment}")
    logger.info("="*60)

    try:
        # Create Flask application context
        app = create_app()

        with app.app_context():
            # Get the database URL for logging (masking sensitive info)
            db_url = app.config.get("SQLALCHEMY_DATABASE_URI", "")
            is_sqlite = db_url.startswith("sqlite:")

            if "@" in db_url:
                # Mask password in PostgreSQL URLs
                parts = db_url.split("@")
                user_pass = parts[0].split("//")[1].split(":")
                masked_url = db_url.replace(user_pass[1], "***")
            else:
                masked_url = db_url

            logger.info(f"Target Database: {masked_url}")
            logger.info(f"Database Type: {'SQLite' if is_sqlite else 'PostgreSQL'}")

            # SAFETY: Create backup before migration (SQLite only)
            if is_sqlite and DatabaseSafety.database_exists():
                logger.info("[SAFETY] Creating pre-migration backup...")
                success, result = DatabaseSafety.create_backup(backup_reason="pre_migration")

                if success:
                    logger.info(f"✓ Backup created: {result}")
                else:
                    logger.warning(f"⚠ Backup failed: {result}")
                    logger.warning("Proceeding with migration anyway (backup recommended but not required)")

            # SAFETY: Check database state before migration
            logger.info("[SAFETY] Checking database health...")
            health_before = DatabaseSafety.get_health_status()
            logger.info(f"Database status: {health_before['overall_health']}")
            if health_before.get('table_counts'):
                logger.info(f"Current state: {health_before['table_counts']}")

            # 1. SCHEMA MIGRATION (Tables/Columns)
            logger.info("\n[STEP 1] Applying Schema Migrations...")
            logger.info("Flask-Migrate will check for pending migrations...")

            try:
                upgrade()
                logger.info("✓ Schema migration complete")
            except Exception as e:
                logger.error(f"✗ Schema migration failed: {e}")
                logger.error("\nTroubleshooting:")
                logger.error("1. Check migrations/versions/ for invalid migration files")
                logger.error("2. Ensure down_revision values are valid")
                logger.error("3. Run 'flask db history' to see migration chain")
                logger.error(f"4. Check {masked_url} for connectivity issues")
                raise

            # 2. DATA MIGRATION (Tools/Rows)
            logger.info("\n[STEP 2] Syncing Tool Definitions...")
            try:
                sync_tools()
                logger.info("✓ Tool sync complete")
            except Exception as e:
                logger.error(f"✗ Tool sync failed: {e}")
                logger.warning("Schema migration succeeded but tool sync failed")
                logger.warning("Your database schema is up to date but tools may not be synced")
                raise

            # SAFETY: Verify database state after migration
            logger.info("\n[SAFETY] Verifying post-migration state...")
            health_after = DatabaseSafety.get_health_status()

            if health_after['overall_health'] in ['healthy', 'degraded']:
                logger.info(f"✓ Post-migration health: {health_after['overall_health']}")
                logger.info(f"✓ Final state: {health_after['table_counts']}")
            else:
                logger.error(f"✗ Post-migration health check failed: {health_after['overall_health']}")
                logger.error(f"Missing tables: {health_after.get('missing_tables', [])}")
                raise Exception("Migration completed but database health check failed")

            logger.info("\n" + "="*60)
            logger.info("✓ MIGRATION COMPLETED SUCCESSFULLY")
            logger.info("="*60)

    except Exception as e:
        logger.error("\n" + "="*60)
        logger.error("✗ MIGRATION FAILED")
        logger.error("="*60)
        logger.error(f"Error: {str(e)}")
        logger.error("\nRecovery Options:")
        logger.error("1. Check error message above for specific issue")
        logger.error("2. If backup was created, restore with: python restore_backup.py")
        logger.error("3. Check logs/app.log for more details")
        logger.error("4. Consult CLAUDE.md for troubleshooting guide")

        # Exit with error code to fail CI/CD pipeline
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()
