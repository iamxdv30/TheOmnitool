"""
SQLite to PostgreSQL Migration Script

One-time migration of existing SQLite data to Docker PostgreSQL.
This script provides a safe, step-by-step migration process.

Usage:
    # Step 1: Export data from SQLite
    python scripts/migrate_sqlite_to_postgres.py --export

    # Step 2: Start Docker PostgreSQL
    .\\scripts\\docker-db.ps1 start   (Windows)
    ./scripts/docker-db.sh start      (Linux/Mac)

    # Step 3: Initialize PostgreSQL schema
    $env:USE_DOCKER_DB="true"; python migrate_db.py   (Windows PowerShell)
    USE_DOCKER_DB=true python migrate_db.py           (Linux/Mac)

    # Step 4: Import data to PostgreSQL
    $env:USE_DOCKER_DB="true"; python scripts/migrate_sqlite_to_postgres.py --import
    USE_DOCKER_DB=true python scripts/migrate_sqlite_to_postgres.py --import

    # Step 5: Verify migration
    $env:USE_DOCKER_DB="true"; python scripts/migrate_sqlite_to_postgres.py --verify
    USE_DOCKER_DB=true python scripts/migrate_sqlite_to_postgres.py --verify

Safety Features:
    - Creates timestamped backup before any changes
    - Preserves original SQLite database
    - Provides verification step
    - Can be re-run safely (idempotent)
"""

import os
import sys
import argparse
import logging
import shutil
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("migrate_sqlite_to_postgres")

# Migration backup location
BACKUP_DIR = "data/backups"
MIGRATION_BACKUP = os.path.join(BACKUP_DIR, "sqlite_migration_backup.json")


def export_from_sqlite():
    """
    Export all data from SQLite database to JSON.
    Creates a timestamped backup and a standard migration backup file.
    """
    logger.info("=" * 60)
    logger.info("STEP 1: EXPORTING DATA FROM SQLite")
    logger.info("=" * 60)

    # Force SQLite mode
    os.environ['USE_DOCKER_DB'] = 'false'
    os.environ['IS_LOCAL'] = 'true'

    # Check if SQLite database exists
    sqlite_path = os.path.join('instance', 'users.db')
    if not os.path.exists(sqlite_path):
        # Also check root directory
        sqlite_path = 'users.db'
        if not os.path.exists(sqlite_path):
            logger.error("SQLite database not found!")
            logger.error("Checked: instance/users.db and users.db")
            logger.error("")
            logger.error("If you haven't created a database yet, skip this step")
            logger.error("and proceed directly to starting Docker PostgreSQL.")
            sys.exit(1)

    logger.info(f"Found SQLite database: {sqlite_path}")
    logger.info(f"File size: {os.path.getsize(sqlite_path) / 1024:.1f} KB")
    logger.info("")

    # Import and run export
    from scripts.export_all_data import export_all_data

    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamped_backup = os.path.join(BACKUP_DIR, f"sqlite_migration_{timestamp}.json")

    logger.info("Exporting data from SQLite...")
    export_all_data(timestamped_backup, environment='local')

    # Also create the standard migration backup (overwrite if exists)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    shutil.copy(timestamped_backup, MIGRATION_BACKUP)

    logger.info("")
    logger.info("=" * 60)
    logger.info("EXPORT COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Timestamped backup: {timestamped_backup}")
    logger.info(f"Migration backup:   {MIGRATION_BACKUP}")
    logger.info("")
    logger.info("NEXT STEPS:")
    logger.info("")
    logger.info("1. Start Docker PostgreSQL:")
    logger.info("   Windows:    .\\scripts\\docker-db.ps1 start")
    logger.info("   Linux/Mac:  ./scripts/docker-db.sh start")
    logger.info("")
    logger.info("2. Initialize PostgreSQL schema:")
    logger.info("   Windows:    $env:USE_DOCKER_DB='true'; python migrate_db.py")
    logger.info("   Linux/Mac:  USE_DOCKER_DB=true python migrate_db.py")
    logger.info("")
    logger.info("3. Import data to PostgreSQL:")
    logger.info("   Windows:    $env:USE_DOCKER_DB='true'; python scripts/migrate_sqlite_to_postgres.py --import")
    logger.info("   Linux/Mac:  USE_DOCKER_DB=true python scripts/migrate_sqlite_to_postgres.py --import")


def import_to_postgres():
    """
    Import data from migration backup to PostgreSQL.
    """
    logger.info("=" * 60)
    logger.info("STEP 4: IMPORTING DATA TO PostgreSQL")
    logger.info("=" * 60)

    # Check migration backup exists
    if not os.path.exists(MIGRATION_BACKUP):
        logger.error(f"Migration backup not found: {MIGRATION_BACKUP}")
        logger.error("")
        logger.error("Please run the export step first:")
        logger.error("  python scripts/migrate_sqlite_to_postgres.py --export")
        sys.exit(1)

    # Force PostgreSQL mode
    use_docker = os.environ.get('USE_DOCKER_DB', 'false').lower()
    if use_docker != 'true':
        logger.warning("USE_DOCKER_DB is not set to 'true'")
        logger.warning("Setting USE_DOCKER_DB=true for this import")
        os.environ['USE_DOCKER_DB'] = 'true'

    # Verify PostgreSQL is running
    logger.info("Checking PostgreSQL connection...")
    try:
        from main import create_app
        from model import db

        app = create_app()
        with app.app_context():
            db_url = str(db.engine.url)
            if 'postgresql' not in db_url and 'postgres' not in db_url:
                logger.error("Not connected to PostgreSQL!")
                logger.error(f"Current database: {db_url}")
                logger.error("")
                logger.error("Make sure:")
                logger.error("1. Docker PostgreSQL is running")
                logger.error("2. USE_DOCKER_DB=true is set")
                sys.exit(1)

            # Test connection
            db.session.execute(db.text("SELECT 1"))
            logger.info("PostgreSQL connection OK")
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        logger.error("")
        logger.error("Make sure Docker PostgreSQL is running:")
        logger.error("  Windows:    .\\scripts\\docker-db.ps1 start")
        logger.error("  Linux/Mac:  ./scripts/docker-db.sh start")
        sys.exit(1)

    # Run import
    logger.info("")
    logger.info("Importing data from migration backup...")
    from scripts.import_all_data import import_all_data

    stats = import_all_data(MIGRATION_BACKUP, dry_run=False)

    logger.info("")
    logger.info("=" * 60)
    logger.info("IMPORT COMPLETE")
    logger.info("=" * 60)
    logger.info("")
    logger.info("NEXT STEP: Verify the migration")
    logger.info("  Windows:    $env:USE_DOCKER_DB='true'; python scripts/migrate_sqlite_to_postgres.py --verify")
    logger.info("  Linux/Mac:  USE_DOCKER_DB=true python scripts/migrate_sqlite_to_postgres.py --verify")


def verify_migration():
    """
    Verify data integrity after migration.
    Compares record counts between backup and PostgreSQL.
    """
    logger.info("=" * 60)
    logger.info("STEP 5: VERIFYING MIGRATION")
    logger.info("=" * 60)

    # Check USE_DOCKER_DB
    use_docker = os.environ.get('USE_DOCKER_DB', 'false').lower()
    if use_docker != 'true':
        os.environ['USE_DOCKER_DB'] = 'true'

    # Load backup metadata for comparison
    backup_counts = {}
    if os.path.exists(MIGRATION_BACKUP):
        import json
        with open(MIGRATION_BACKUP, 'r') as f:
            backup_data = json.load(f)
            backup_counts = backup_data.get("export_metadata", {}).get("tables", {})
        logger.info(f"Backup file: {MIGRATION_BACKUP}")
    else:
        logger.warning("Migration backup not found for comparison")

    # Get PostgreSQL counts
    from main import create_app
    from model import db, User, Tool, ToolAccess, EmailTemplate, UsageLog

    app = create_app()

    with app.app_context():
        db_url = str(db.engine.url)
        if '@' in db_url:
            masked_url = db_url.split('@')[0].rsplit(':', 1)[0] + ':****@' + db_url.split('@')[1]
        else:
            masked_url = db_url
        logger.info(f"Database: {masked_url}")
        logger.info("")

        postgres_counts = {
            "users": User.query.count(),
            "tools": Tool.query.count(),
            "tool_access": ToolAccess.query.count(),
            "email_templates": EmailTemplate.query.count(),
            "usage_logs": UsageLog.query.count()
        }

        logger.info("COMPARISON:")
        logger.info("-" * 40)
        logger.info(f"{'Table':<20} {'Backup':>8} {'PostgreSQL':>12}")
        logger.info("-" * 40)

        all_match = True
        for table in ["users", "tools", "tool_access", "email_templates", "usage_logs"]:
            backup_count = backup_counts.get(table, "N/A")
            pg_count = postgres_counts.get(table, 0)

            if isinstance(backup_count, int):
                if backup_count == pg_count:
                    status = "OK"
                elif pg_count >= backup_count:
                    status = "OK (more)"  # More records is fine (existing + imported)
                else:
                    status = "MISSING"
                    all_match = False
            else:
                status = "N/A"

            logger.info(f"{table:<20} {str(backup_count):>8} {pg_count:>12}  {status}")

        logger.info("-" * 40)
        logger.info("")

        if all_match:
            logger.info("VERIFICATION PASSED")
            logger.info("")
            logger.info("Migration completed successfully!")
            logger.info("")
            logger.info("You can now use PostgreSQL for development:")
            logger.info("  1. Ensure USE_DOCKER_DB=true is in your .env file")
            logger.info("  2. Start the application: python main.py")
            logger.info("")
            logger.info("To switch back to SQLite (not recommended):")
            logger.info("  Set USE_DOCKER_DB=false in .env")
        else:
            logger.warning("VERIFICATION FAILED - Some records may be missing")
            logger.warning("")
            logger.warning("This could happen if:")
            logger.warning("  - Import was interrupted")
            logger.warning("  - Some records had constraint violations")
            logger.warning("")
            logger.warning("Try re-running the import:")
            logger.warning("  python scripts/migrate_sqlite_to_postgres.py --import")


def show_status():
    """
    Show current migration status and environment.
    """
    logger.info("=" * 60)
    logger.info("MIGRATION STATUS")
    logger.info("=" * 60)

    # Check environment
    use_docker = os.environ.get('USE_DOCKER_DB', 'false')
    is_local = os.environ.get('IS_LOCAL', 'true')

    logger.info(f"USE_DOCKER_DB: {use_docker}")
    logger.info(f"IS_LOCAL: {is_local}")
    logger.info("")

    # Check SQLite
    sqlite_paths = ['instance/users.db', 'users.db']
    sqlite_found = False
    for path in sqlite_paths:
        if os.path.exists(path):
            size = os.path.getsize(path) / 1024
            logger.info(f"SQLite database: {path} ({size:.1f} KB)")
            sqlite_found = True
            break
    if not sqlite_found:
        logger.info("SQLite database: Not found")

    # Check backup
    if os.path.exists(MIGRATION_BACKUP):
        import json
        with open(MIGRATION_BACKUP, 'r') as f:
            backup_data = json.load(f)
            metadata = backup_data.get("export_metadata", {})
            logger.info(f"Migration backup: {MIGRATION_BACKUP}")
            logger.info(f"  Created: {metadata.get('timestamp', 'unknown')}")
            logger.info(f"  Source: {metadata.get('database_type', 'unknown')}")
    else:
        logger.info("Migration backup: Not found")

    logger.info("")

    # Check Docker PostgreSQL
    import subprocess
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=omnitool-postgres", "--format", "{{.Status}}"],
            capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip():
            logger.info(f"Docker PostgreSQL: Running ({result.stdout.strip()})")
        else:
            logger.info("Docker PostgreSQL: Not running")
    except Exception:
        logger.info("Docker PostgreSQL: Docker not available")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Migrate SQLite database to Docker PostgreSQL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Full Migration Workflow:

    1. Export from SQLite:
       python scripts/migrate_sqlite_to_postgres.py --export

    2. Start Docker PostgreSQL:
       Windows:    .\\scripts\\docker-db.ps1 start
       Linux/Mac:  ./scripts/docker-db.sh start

    3. Initialize PostgreSQL schema:
       Windows:    $env:USE_DOCKER_DB='true'; python migrate_db.py
       Linux/Mac:  USE_DOCKER_DB=true python migrate_db.py

    4. Import to PostgreSQL:
       Windows:    $env:USE_DOCKER_DB='true'; python scripts/migrate_sqlite_to_postgres.py --import
       Linux/Mac:  USE_DOCKER_DB=true python scripts/migrate_sqlite_to_postgres.py --import

    5. Verify migration:
       Windows:    $env:USE_DOCKER_DB='true'; python scripts/migrate_sqlite_to_postgres.py --verify
       Linux/Mac:  USE_DOCKER_DB=true python scripts/migrate_sqlite_to_postgres.py --verify
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--export',
        action='store_true',
        help='Export data from SQLite to JSON backup'
    )
    group.add_argument(
        '--import',
        dest='import_data',
        action='store_true',
        help='Import data from JSON backup to PostgreSQL'
    )
    group.add_argument(
        '--verify',
        action='store_true',
        help='Verify migration by comparing record counts'
    )
    group.add_argument(
        '--status',
        action='store_true',
        help='Show current migration status'
    )

    args = parser.parse_args()

    try:
        if args.export:
            export_from_sqlite()
        elif args.import_data:
            import_to_postgres()
        elif args.verify:
            verify_migration()
        elif args.status:
            show_status()
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
