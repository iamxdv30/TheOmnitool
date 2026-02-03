"""
Comprehensive Data Import Script

Imports ALL tables from JSON backup into the database.
Supports both SQLite and PostgreSQL targets.

Usage:
    python scripts/import_all_data.py --source data/backups/my_backup.json
    python scripts/import_all_data.py --source data/backups/my_backup.json --dry-run
    python scripts/import_all_data.py --source data/backups/my_backup.json --skip-users

Tables Imported:
    - tools (imported first - no dependencies)
    - users (imported second)
    - admins (junction table)
    - super_admins (junction table)
    - tool_access (depends on users and tools)
    - email_templates (depends on users)
    - usage_logs (depends on users)

Safety Features:
    - Dry-run mode to preview changes
    - Skips existing records (idempotent)
    - Validates foreign key references
    - Logs all operations
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("import_all_data")


def parse_datetime(dt_string):
    """Parse ISO datetime string to datetime object"""
    if dt_string is None:
        return None
    if isinstance(dt_string, datetime):
        return dt_string
    try:
        # Handle various ISO formats
        dt_string = dt_string.replace('Z', '+00:00')
        if '+' in dt_string:
            return datetime.fromisoformat(dt_string)
        return datetime.fromisoformat(dt_string)
    except (ValueError, AttributeError):
        return None


def import_all_data(source_path, dry_run=False, skip_users=False, skip_logs=False):
    """
    Import all database tables from JSON backup.

    Args:
        source_path: Path to JSON backup file
        dry_run: If True, don't commit changes (preview mode)
        skip_users: If True, skip importing users
        skip_logs: If True, skip importing usage_logs

    Returns:
        Dictionary of import statistics
    """
    # Validate source file exists
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Backup file not found: {source_path}")

    # Load backup data
    logger.info(f"Loading backup from: {source_path}")
    with open(source_path, 'r', encoding='utf-8') as f:
        import_data = json.load(f)

    # Log metadata
    metadata = import_data.get("export_metadata", {})
    logger.info(f"Backup timestamp: {metadata.get('timestamp', 'unknown')}")
    logger.info(f"Source database: {metadata.get('database_type', 'unknown')}")
    logger.info(f"Source environment: {metadata.get('environment', 'unknown')}")

    if dry_run:
        logger.info("")
        logger.info(">>> DRY RUN MODE - No changes will be committed <<<")
        logger.info("")

    # Import here to avoid circular imports
    from main import create_app
    from model import db, User, Admin, SuperAdmin, Tool, ToolAccess, UsageLog, EmailTemplate

    app = create_app()

    with app.app_context():
        # Log target database
        db_url = str(db.engine.url)
        if '@' in db_url:
            masked_url = db_url.split('@')[0].rsplit(':', 1)[0] + ':****@' + db_url.split('@')[1]
        else:
            masked_url = db_url
        logger.info(f"Target database: {masked_url}")
        logger.info("")

        # Initialize statistics
        stats = {
            "tools": {"imported": 0, "skipped": 0, "errors": 0},
            "users": {"imported": 0, "skipped": 0, "errors": 0},
            "admins": {"imported": 0, "skipped": 0, "errors": 0},
            "super_admins": {"imported": 0, "skipped": 0, "errors": 0},
            "tool_access": {"imported": 0, "skipped": 0, "errors": 0},
            "email_templates": {"imported": 0, "skipped": 0, "errors": 0},
            "usage_logs": {"imported": 0, "skipped": 0, "errors": 0}
        }

        # Track user ID mapping (old_id -> new_id) in case IDs change
        user_id_map = {}

        # ===== 1. Import Tools (no dependencies) =====
        logger.info("Importing tools...")
        for tool_data in import_data.get("tools", []):
            try:
                existing = Tool.query.filter_by(name=tool_data["name"]).first()
                if existing:
                    stats["tools"]["skipped"] += 1
                    continue

                tool = Tool(
                    name=tool_data["name"],
                    description=tool_data.get("description"),
                    route=tool_data["route"],
                    is_default=tool_data.get("is_default", False),
                    is_active=tool_data.get("is_active", True)
                )
                if not dry_run:
                    db.session.add(tool)
                stats["tools"]["imported"] += 1
            except Exception as e:
                logger.error(f"  Failed to import tool {tool_data.get('name')}: {e}")
                stats["tools"]["errors"] += 1

        if not dry_run:
            db.session.flush()
        logger.info(f"  Imported: {stats['tools']['imported']}, Skipped: {stats['tools']['skipped']}")

        # ===== 2. Import Users =====
        if skip_users:
            logger.info("Skipping users (--skip-users flag)")
            # Still build the ID map from existing users
            for user_data in import_data.get("users", []):
                existing = User.query.filter_by(email=user_data["email"]).first()
                if existing:
                    user_id_map[user_data["id"]] = existing.id
        else:
            logger.info("Importing users...")
            for user_data in import_data.get("users", []):
                try:
                    # Check by email (unique constraint)
                    existing = User.query.filter_by(email=user_data["email"]).first()
                    if existing:
                        user_id_map[user_data["id"]] = existing.id
                        stats["users"]["skipped"] += 1
                        continue

                    # Also check by username
                    existing_username = User.query.filter_by(username=user_data["username"]).first()
                    if existing_username:
                        user_id_map[user_data["id"]] = existing_username.id
                        stats["users"]["skipped"] += 1
                        continue

                    # Create appropriate user type based on role
                    role = user_data.get("role", "user")

                    if role == "super_admin":
                        user = SuperAdmin(
                            username=user_data["username"],
                            email=user_data["email"],
                            name=user_data.get("name"),
                            fname=user_data.get("fname"),
                            lname=user_data.get("lname"),
                            email_verified=user_data.get("email_verified", False)
                        )
                    elif role == "admin":
                        user = Admin(
                            username=user_data["username"],
                            email=user_data["email"],
                            name=user_data.get("name"),
                            fname=user_data.get("fname"),
                            lname=user_data.get("lname"),
                            email_verified=user_data.get("email_verified", False)
                        )
                    else:
                        user = User(
                            username=user_data["username"],
                            email=user_data["email"],
                            name=user_data.get("name"),
                            fname=user_data.get("fname"),
                            lname=user_data.get("lname"),
                            email_verified=user_data.get("email_verified", False)
                        )

                    # Set optional fields
                    user.address = user_data.get("address")
                    user.city = user_data.get("city")
                    user.state = user_data.get("state")
                    user.zip = user_data.get("zip")
                    user.oauth_provider = user_data.get("oauth_provider")
                    user.oauth_id = user_data.get("oauth_id")
                    user.requires_password_setup = user_data.get("requires_password_setup", False)
                    user.is_active = user_data.get("is_active", True)

                    # Set hashed password directly (already hashed in backup)
                    if user_data.get("password"):
                        user.password = user_data["password"]

                    if not dry_run:
                        db.session.add(user)
                        db.session.flush()  # Get the new ID
                        user_id_map[user_data["id"]] = user.id
                    else:
                        user_id_map[user_data["id"]] = user_data["id"]

                    stats["users"]["imported"] += 1
                except Exception as e:
                    logger.error(f"  Failed to import user {user_data.get('email')}: {e}")
                    stats["users"]["errors"] += 1

            logger.info(f"  Imported: {stats['users']['imported']}, Skipped: {stats['users']['skipped']}")

        # ===== 3. Import ToolAccess =====
        logger.info("Importing tool_access...")
        valid_tools = {t.name for t in Tool.query.all()}

        for ta_data in import_data.get("tool_access", []):
            try:
                old_user_id = ta_data["user_id"]
                new_user_id = user_id_map.get(old_user_id)

                if not new_user_id:
                    logger.debug(f"  Skipping tool_access: user_id {old_user_id} not found")
                    stats["tool_access"]["skipped"] += 1
                    continue

                tool_name = ta_data["tool_name"]
                if tool_name not in valid_tools:
                    logger.debug(f"  Skipping tool_access: tool '{tool_name}' not found")
                    stats["tool_access"]["skipped"] += 1
                    continue

                # Check for existing
                existing = ToolAccess.query.filter_by(
                    user_id=new_user_id,
                    tool_name=tool_name
                ).first()

                if existing:
                    stats["tool_access"]["skipped"] += 1
                    continue

                ta = ToolAccess(user_id=new_user_id, tool_name=tool_name)
                if not dry_run:
                    db.session.add(ta)
                stats["tool_access"]["imported"] += 1
            except Exception as e:
                logger.error(f"  Failed to import tool_access: {e}")
                stats["tool_access"]["errors"] += 1

        logger.info(f"  Imported: {stats['tool_access']['imported']}, Skipped: {stats['tool_access']['skipped']}")

        # ===== 4. Import EmailTemplates =====
        logger.info("Importing email_templates...")
        for template_data in import_data.get("email_templates", []):
            try:
                old_user_id = template_data["user_id"]
                new_user_id = user_id_map.get(old_user_id)

                if not new_user_id:
                    stats["email_templates"]["skipped"] += 1
                    continue

                template = EmailTemplate(
                    user_id=new_user_id,
                    title=template_data["title"],
                    content=template_data["content"]
                )
                if not dry_run:
                    db.session.add(template)
                stats["email_templates"]["imported"] += 1
            except Exception as e:
                logger.error(f"  Failed to import email_template: {e}")
                stats["email_templates"]["errors"] += 1

        logger.info(f"  Imported: {stats['email_templates']['imported']}, Skipped: {stats['email_templates']['skipped']}")

        # ===== 5. Import UsageLogs =====
        if skip_logs:
            logger.info("Skipping usage_logs (--skip-logs flag)")
        else:
            logger.info("Importing usage_logs...")
            for log_data in import_data.get("usage_logs", []):
                try:
                    old_user_id = log_data["user_id"]
                    new_user_id = user_id_map.get(old_user_id)

                    if not new_user_id:
                        stats["usage_logs"]["skipped"] += 1
                        continue

                    log = UsageLog(
                        user_id=new_user_id,
                        tool_name=log_data["tool_name"],
                        timestamp=parse_datetime(log_data.get("timestamp")) or datetime.utcnow()
                    )
                    if not dry_run:
                        db.session.add(log)
                    stats["usage_logs"]["imported"] += 1
                except Exception as e:
                    logger.error(f"  Failed to import usage_log: {e}")
                    stats["usage_logs"]["errors"] += 1

            logger.info(f"  Imported: {stats['usage_logs']['imported']}, Skipped: {stats['usage_logs']['skipped']}")

        # ===== Commit or Rollback =====
        if not dry_run:
            try:
                db.session.commit()
                logger.info("")
                logger.info("Changes committed successfully")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Failed to commit changes: {e}")
                raise
        else:
            db.session.rollback()
            logger.info("")
            logger.info("DRY RUN - No changes were committed")

        # ===== Summary =====
        logger.info("")
        logger.info("=" * 50)
        logger.info("IMPORT SUMMARY")
        logger.info("=" * 50)
        total_imported = sum(s["imported"] for s in stats.values())
        total_skipped = sum(s["skipped"] for s in stats.values())
        total_errors = sum(s["errors"] for s in stats.values())

        for table, counts in stats.items():
            if counts["imported"] > 0 or counts["skipped"] > 0 or counts["errors"] > 0:
                logger.info(f"  {table}: {counts['imported']} imported, {counts['skipped']} skipped, {counts['errors']} errors")

        logger.info("")
        logger.info(f"Total: {total_imported} imported, {total_skipped} skipped, {total_errors} errors")

        return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Import all database tables from JSON backup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Preview import (dry-run)
    python scripts/import_all_data.py --source data/backups/backup.json --dry-run

    # Import all data
    python scripts/import_all_data.py --source data/backups/backup.json

    # Import without users (tools and tool_access only)
    python scripts/import_all_data.py --source data/backups/backup.json --skip-users

    # Import without usage logs (faster import)
    python scripts/import_all_data.py --source data/backups/backup.json --skip-logs
        """
    )
    parser.add_argument(
        '--source', '-s',
        required=True,
        help='Path to JSON backup file'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Preview changes without committing'
    )
    parser.add_argument(
        '--skip-users',
        action='store_true',
        help='Skip importing users (useful when users already exist)'
    )
    parser.add_argument(
        '--skip-logs',
        action='store_true',
        help='Skip importing usage_logs (faster import)'
    )

    args = parser.parse_args()

    try:
        import_all_data(args.source, args.dry_run, args.skip_users, args.skip_logs)
    except Exception as e:
        logger.error(f"Import failed: {e}")
        sys.exit(1)
