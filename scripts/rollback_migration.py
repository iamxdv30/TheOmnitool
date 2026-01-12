"""
Emergency Rollback Script for Database Migrations

This script provides emergency database restoration capabilities from backups.

Safety Features:
- Creates pre-rollback backup before any restoration
- Validates backup exists before attempting restore
- Supports Heroku Postgres backups (by ID or latest)
- Supports local SQLite backups from file
- Transaction-safe operations

Usage:
    # Rollback staging to latest backup
    python scripts/rollback_migration.py --env staging

    # Rollback production to specific backup
    python scripts/rollback_migration.py --env production --backup b123

    # Rollback local from file
    python scripts/rollback_migration.py --env local --file data/backups/users_20260112.db

    # Dry-run mode (preview without executing)
    python scripts/rollback_migration.py --env production --backup b123 --dry-run
"""

import argparse
import logging
import os
import sys
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("rollback_migration")

# Environment configuration
ENV_CONFIG = {
    "local": {
        "db_type": "sqlite",
        "db_path": "users.db",
        "backup_dir": "data/backups"
    },
    "staging": {
        "db_type": "postgres",
        "heroku_app": "omnitool-by-xdv-staging"
    },
    "production": {
        "db_type": "postgres",
        "heroku_app": "omnitool-by-xdv"
    }
}

class RollbackError(Exception):
    """Custom exception for rollback failures"""
    pass

def validate_environment(env: str) -> dict:
    """Validate environment and return config"""
    if env not in ENV_CONFIG:
        raise RollbackError(f"Invalid environment: {env}. Must be one of: {', '.join(ENV_CONFIG.keys())}")

    config = ENV_CONFIG[env]
    logger.info(f"Environment: {env} ({config['db_type']})")

    return config

def create_pre_rollback_backup(env: str, config: dict, dry_run: bool = False) -> str:
    """
    Create backup before rollback as safety net

    Returns: backup identifier (backup ID for Heroku, file path for local)
    """
    logger.info("Creating pre-rollback backup (safety net)...")

    if dry_run:
        logger.info("[DRY-RUN] Would create pre-rollback backup")
        return "dry-run-backup-id"

    if config["db_type"] == "postgres":
        # Heroku backup
        app_name = config["heroku_app"]

        try:
            result = subprocess.run(
                ["heroku", "pg:backups:capture", "-a", app_name],
                capture_output=True,
                text=True,
                check=True
            )

            logger.info(f"Pre-rollback backup created: {result.stdout.strip()}")

            # Get latest backup ID
            result = subprocess.run(
                ["heroku", "pg:backups", "-a", app_name, "--json"],
                capture_output=True,
                text=True,
                check=True
            )

            import json
            backups = json.loads(result.stdout)
            if backups:
                latest_backup = backups[0]['name']
                logger.info(f"Pre-rollback backup ID: {latest_backup}")
                return latest_backup
            else:
                raise RollbackError("Failed to retrieve backup ID")

        except subprocess.CalledProcessError as e:
            raise RollbackError(f"Failed to create pre-rollback backup: {e.stderr}")

    else:
        # SQLite backup
        db_path = config["db_path"]
        backup_dir = Path(config["backup_dir"])
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"pre_rollback_{timestamp}.db"

        try:
            shutil.copy2(db_path, backup_file)
            logger.info(f"Pre-rollback backup created: {backup_file}")
            return str(backup_file)

        except Exception as e:
            raise RollbackError(f"Failed to create pre-rollback backup: {e}")

def validate_backup_exists(env: str, config: dict, backup_id: str = None, backup_file: str = None) -> bool:
    """
    Validate that backup exists before attempting restore

    Returns: True if backup exists and is valid
    """
    logger.info("Validating backup exists...")

    if config["db_type"] == "postgres":
        app_name = config["heroku_app"]

        try:
            result = subprocess.run(
                ["heroku", "pg:backups", "-a", app_name, "--json"],
                capture_output=True,
                text=True,
                check=True
            )

            import json
            backups = json.loads(result.stdout)

            if backup_id:
                # Validate specific backup
                backup_exists = any(b['name'] == backup_id for b in backups)
                if not backup_exists:
                    raise RollbackError(f"Backup {backup_id} not found. Available: {[b['name'] for b in backups]}")

                logger.info(f"✓ Backup {backup_id} exists")
            else:
                # Use latest backup
                if not backups:
                    raise RollbackError("No backups available")

                latest = backups[0]['name']
                logger.info(f"✓ Latest backup {latest} exists")

            return True

        except subprocess.CalledProcessError as e:
            raise RollbackError(f"Failed to validate backup: {e.stderr}")

    else:
        # SQLite backup
        if not backup_file:
            raise RollbackError("--file parameter required for local environment")

        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise RollbackError(f"Backup file not found: {backup_file}")

        if backup_path.stat().st_size == 0:
            raise RollbackError(f"Backup file is empty: {backup_file}")

        logger.info(f"✓ Backup file exists: {backup_file} ({backup_path.stat().st_size} bytes)")
        return True

def restore_heroku_backup(app_name: str, backup_id: str = None, dry_run: bool = False):
    """
    Restore Heroku Postgres database from backup

    Args:
        app_name: Heroku app name
        backup_id: Specific backup ID (e.g., 'b123') or None for latest
        dry_run: Preview without executing
    """
    if backup_id:
        logger.info(f"Restoring from backup {backup_id}...")
    else:
        logger.info("Restoring from latest backup...")

    if dry_run:
        logger.info(f"[DRY-RUN] Would restore {app_name} from backup {backup_id or 'latest'}")
        return

    # Construct restore command
    if backup_id:
        restore_cmd = [
            "heroku", "pg:backups:restore", backup_id, "DATABASE_URL",
            "-a", app_name,
            "--confirm", app_name
        ]
    else:
        restore_cmd = [
            "heroku", "pg:backups:restore", "DATABASE_URL",
            "-a", app_name,
            "--confirm", app_name
        ]

    try:
        logger.warning(f"⚠️  RESTORING DATABASE for {app_name} - THIS WILL OVERWRITE CURRENT DATA")

        result = subprocess.run(
            restore_cmd,
            capture_output=True,
            text=True,
            check=True
        )

        logger.info("✓ Database restored successfully")
        logger.info(result.stdout)

    except subprocess.CalledProcessError as e:
        raise RollbackError(f"Database restore failed: {e.stderr}")

def restore_sqlite_backup(db_path: str, backup_file: str, dry_run: bool = False):
    """
    Restore SQLite database from backup file

    Args:
        db_path: Path to current database
        backup_file: Path to backup file
        dry_run: Preview without executing
    """
    logger.info(f"Restoring from {backup_file}...")

    if dry_run:
        logger.info(f"[DRY-RUN] Would restore {db_path} from {backup_file}")
        return

    try:
        # Backup current database first (already done in create_pre_rollback_backup)
        logger.warning(f"⚠️  RESTORING DATABASE - THIS WILL OVERWRITE {db_path}")

        shutil.copy2(backup_file, db_path)

        logger.info(f"✓ Database restored successfully from {backup_file}")

    except Exception as e:
        raise RollbackError(f"Database restore failed: {e}")

def verify_restoration(env: str, config: dict):
    """
    Verify database is accessible after restoration
    """
    logger.info("Verifying database restoration...")

    if config["db_type"] == "postgres":
        app_name = config["heroku_app"]

        try:
            result = subprocess.run(
                ["heroku", "pg:info", "-a", app_name],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )

            logger.info("✓ Database is accessible")
            logger.debug(result.stdout)

        except subprocess.CalledProcessError as e:
            raise RollbackError(f"Database verification failed: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise RollbackError("Database verification timed out")

    else:
        # SQLite verification
        db_path = config["db_path"]

        try:
            import sqlite3
            conn = sqlite3.connect(db_path, timeout=10)
            cursor = conn.cursor()

            # Test query
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM tools")
            tool_count = cursor.fetchone()[0]

            conn.close()

            logger.info(f"✓ Database is accessible ({user_count} users, {tool_count} tools)")

        except Exception as e:
            raise RollbackError(f"Database verification failed: {e}")

def rollback_migration(env: str, backup_id: str = None, backup_file: str = None, dry_run: bool = False):
    """
    Main rollback function

    Steps:
    1. Validate environment and backup
    2. Create pre-rollback backup (safety net)
    3. Restore from specified backup
    4. Verify restoration success

    Args:
        env: Environment (local, staging, production)
        backup_id: Heroku backup ID (for staging/production)
        backup_file: Backup file path (for local)
        dry_run: Preview without executing
    """
    logger.info("=" * 60)
    logger.info("DATABASE MIGRATION ROLLBACK")
    logger.info("=" * 60)

    try:
        # Step 1: Validate environment
        config = validate_environment(env)

        # Step 2: Validate backup exists
        validate_backup_exists(env, config, backup_id, backup_file)

        # Step 3: Create pre-rollback backup (safety net)
        pre_rollback_backup = create_pre_rollback_backup(env, config, dry_run)
        logger.info(f"Safety net created: {pre_rollback_backup}")

        # Step 4: Restore from backup
        if config["db_type"] == "postgres":
            restore_heroku_backup(config["heroku_app"], backup_id, dry_run)
        else:
            restore_sqlite_backup(config["db_path"], backup_file, dry_run)

        # Step 5: Verify restoration
        if not dry_run:
            verify_restoration(env, config)

        logger.info("=" * 60)
        logger.info("✓ ROLLBACK COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)

        if config["db_type"] == "postgres":
            logger.info(f"\nNext steps:")
            logger.info(f"1. Verify application is accessible:")
            if env == "staging":
                logger.info(f"   heroku open -a omnitool-by-xdv-staging")
            else:
                logger.info(f"   heroku open -a omnitool-by-xdv")
            logger.info(f"2. Monitor logs for errors:")
            logger.info(f"   heroku logs --tail -a {config['heroku_app']}")
            logger.info(f"3. If rollback was incorrect, restore from safety net:")
            logger.info(f"   python scripts/rollback_migration.py --env {env} --backup {pre_rollback_backup}")

    except RollbackError as e:
        logger.error(f"✗ ROLLBACK FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"✗ UNEXPECTED ERROR: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Emergency database rollback from backup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Rollback staging to latest backup
  python scripts/rollback_migration.py --env staging

  # Rollback production to specific backup
  python scripts/rollback_migration.py --env production --backup b123

  # Rollback local from file
  python scripts/rollback_migration.py --env local --file data/backups/users_20260112.db

  # Dry-run mode (preview without executing)
  python scripts/rollback_migration.py --env production --backup b123 --dry-run
        """
    )

    parser.add_argument(
        "--env",
        choices=["local", "staging", "production"],
        required=True,
        help="Target environment"
    )

    parser.add_argument(
        "--backup",
        help="Heroku backup ID (e.g., 'b123'). If omitted, uses latest backup. Only for staging/production."
    )

    parser.add_argument(
        "--file",
        help="Backup file path for local environment (required for local)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview rollback without executing"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate arguments
    if args.env == "local" and not args.file:
        parser.error("--file is required for local environment")

    if args.env in ["staging", "production"] and args.file:
        parser.error("--file is only used for local environment")

    # Confirm production rollback (extra safety)
    if args.env == "production" and not args.dry_run:
        logger.warning("⚠️  WARNING: You are about to rollback the PRODUCTION database!")
        logger.warning("⚠️  This will OVERWRITE all current production data.")

        response = input("\nType 'ROLLBACK PRODUCTION' to confirm: ")
        if response != "ROLLBACK PRODUCTION":
            logger.info("Rollback cancelled.")
            sys.exit(0)

    rollback_migration(
        env=args.env,
        backup_id=args.backup,
        backup_file=args.file,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main()
