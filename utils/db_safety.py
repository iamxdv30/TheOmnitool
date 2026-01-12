"""
Database Safety Utilities
Provides critical safety features for database operations:
- Schema validation
- Automatic backups
- Health checks
- Recovery procedures
"""
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DatabaseSafety:
    """Centralized database safety operations"""

    CRITICAL_TABLES = ['users', 'tools', 'tool_access']
    BACKUP_DIR = "zzDumpfiles/SQLite Database Backup"

    @staticmethod
    def get_db_path(app=None):
        """Get database path from app config or environment"""
        if app:
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        else:
            db_uri = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///users.db')

        # Extract path from SQLite URI
        if db_uri.startswith('sqlite:///'):
            path = db_uri.replace('sqlite:///', '')
            # Handle relative paths
            if not os.path.isabs(path):
                return os.path.join(os.getcwd(), 'instance', path)
            return path

        return None  # Not SQLite

    @staticmethod
    def database_exists(db_path=None):
        """Check if database file exists"""
        if db_path is None:
            db_path = DatabaseSafety.get_db_path()

        if db_path is None:
            return True  # Assume PostgreSQL exists

        return os.path.exists(db_path)

    @staticmethod
    def validate_schema(db_path=None):
        """
        Validate that all critical tables exist in the database
        Returns: (bool, list[str]) - (is_valid, missing_tables)
        """
        if db_path is None:
            db_path = DatabaseSafety.get_db_path()

        if db_path is None:
            logger.warning("Cannot validate PostgreSQL schema from this utility")
            return True, []

        if not os.path.exists(db_path):
            return False, DatabaseSafety.CRITICAL_TABLES

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}

            conn.close()

            # Check for critical tables
            missing_tables = [
                table for table in DatabaseSafety.CRITICAL_TABLES
                if table not in existing_tables
            ]

            is_valid = len(missing_tables) == 0
            return is_valid, missing_tables

        except Exception as e:
            logger.error(f"Error validating schema: {e}")
            return False, []

    @staticmethod
    def get_table_counts(db_path=None):
        """
        Get row counts for critical tables
        Returns: dict[table_name, count]
        """
        if db_path is None:
            db_path = DatabaseSafety.get_db_path()

        if db_path is None or not os.path.exists(db_path):
            return {}

        counts = {}
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            for table in DatabaseSafety.CRITICAL_TABLES:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    counts[table] = cursor.fetchone()[0]
                except:
                    counts[table] = -1  # Table doesn't exist

            conn.close()

        except Exception as e:
            logger.error(f"Error getting table counts: {e}")

        return counts

    @staticmethod
    def create_backup(db_path=None, backup_reason="manual"):
        """
        Create a backup of the database
        Returns: (bool, str) - (success, backup_path or error_message)
        """
        if db_path is None:
            db_path = DatabaseSafety.get_db_path()

        if db_path is None:
            return False, "Cannot backup PostgreSQL from this utility"

        if not os.path.exists(db_path):
            return False, f"Database file does not exist: {db_path}"

        try:
            # Create backup directory if it doesn't exist
            backup_dir = Path(DatabaseSafety.BACKUP_DIR)
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"users.db.backup_{backup_reason}_{timestamp}"
            backup_path = backup_dir / backup_filename

            # Copy database file
            shutil.copy2(db_path, backup_path)

            # Also keep a "latest" backup for quick access
            latest_backup = backup_dir / "users.db"
            shutil.copy2(db_path, latest_backup)

            logger.info(f"✓ Database backup created: {backup_path}")
            return True, str(backup_path)

        except Exception as e:
            error_msg = f"Failed to create backup: {e}"
            logger.error(error_msg)
            return False, error_msg

    @staticmethod
    def cleanup_old_backups(keep_days=7):
        """
        Remove backup files older than keep_days
        Returns: int - number of files removed
        """
        backup_dir = Path(DatabaseSafety.BACKUP_DIR)

        if not backup_dir.exists():
            return 0

        removed_count = 0
        cutoff_time = datetime.now().timestamp() - (keep_days * 86400)

        for backup_file in backup_dir.glob("users.db.backup_*"):
            if backup_file.stat().st_mtime < cutoff_time:
                try:
                    backup_file.unlink()
                    removed_count += 1
                    logger.info(f"Removed old backup: {backup_file.name}")
                except Exception as e:
                    logger.warning(f"Failed to remove {backup_file.name}: {e}")

        return removed_count

    @staticmethod
    def get_health_status(db_path=None):
        """
        Get comprehensive database health status
        Returns: dict with health information
        """
        status = {
            'database_exists': False,
            'schema_valid': False,
            'missing_tables': [],
            'table_counts': {},
            'has_users': False,
            'has_tools': False,
            'overall_health': 'critical'
        }

        if db_path is None:
            db_path = DatabaseSafety.get_db_path()

        # Check existence
        status['database_exists'] = DatabaseSafety.database_exists(db_path)

        if not status['database_exists']:
            return status

        # Check schema
        is_valid, missing = DatabaseSafety.validate_schema(db_path)
        status['schema_valid'] = is_valid
        status['missing_tables'] = missing

        if not is_valid:
            status['overall_health'] = 'critical'
            return status

        # Get table counts
        counts = DatabaseSafety.get_table_counts(db_path)
        status['table_counts'] = counts
        status['has_users'] = counts.get('users', 0) > 0
        status['has_tools'] = counts.get('tools', 0) > 0

        # Determine overall health
        if status['has_users'] and status['has_tools']:
            status['overall_health'] = 'healthy'
        elif status['has_tools']:
            status['overall_health'] = 'degraded'  # DB initialized but no users yet
        else:
            status['overall_health'] = 'critical'

        return status

    @staticmethod
    def initialize_if_needed(app):
        """
        Check database health and initialize if needed
        This should be called during app startup
        Returns: (bool, str) - (success, message)
        """
        db_path = DatabaseSafety.get_db_path(app)

        # Skip for PostgreSQL (production)
        if db_path is None:
            logger.info("Using PostgreSQL - skipping local safety checks")
            return True, "PostgreSQL database (managed by Heroku)"

        health = DatabaseSafety.get_health_status(db_path)

        if health['overall_health'] == 'healthy':
            logger.info(f"✓ Database health check passed: {health['table_counts']}")
            return True, "Database is healthy"

        if not health['database_exists']:
            logger.warning("⚠ Database file does not exist!")
            return False, "Database file missing - run migrate_db.py to initialize"

        if not health['schema_valid']:
            logger.error(f"✗ Database schema invalid! Missing tables: {health['missing_tables']}")
            return False, f"Schema invalid. Missing: {', '.join(health['missing_tables'])}"

        if health['overall_health'] == 'degraded':
            logger.warning("⚠ Database initialized but no users yet")
            return True, "Database schema valid, awaiting first user registration"

        return False, "Unknown database state"


def validate_database_on_startup(app):
    """
    Convenience function to validate database during app startup
    Logs warnings/errors but doesn't prevent app from starting
    """
    success, message = DatabaseSafety.initialize_if_needed(app)

    if not success:
        logger.error(f"DATABASE HEALTH CHECK FAILED: {message}")
        logger.error("Application may not function correctly!")
        logger.error("Run 'python migrate_db.py' to initialize the database")
    else:
        logger.info(f"Database status: {message}")

    return success
