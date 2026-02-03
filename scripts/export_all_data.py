"""
Comprehensive Data Export Script

Exports ALL database tables to JSON for database-agnostic backup/restore.
Works with both SQLite and PostgreSQL.

Usage:
    python scripts/export_all_data.py
    python scripts/export_all_data.py --output data/backups/my_backup.json
    python scripts/export_all_data.py --env staging

Tables Exported:
    - users (including hashed passwords)
    - admins (junction table)
    - super_admins (junction table)
    - tools
    - tool_access
    - usage_logs
    - email_templates
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("export_all_data")


def serialize_value(obj):
    """JSON serializer for special types"""
    if obj is None:
        return None
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.decode('utf-8', errors='replace')
    raise TypeError(f"Type {type(obj)} not serializable")


def get_safe_value(obj, attr, default=None):
    """Safely get attribute value with fallback"""
    try:
        value = getattr(obj, attr, default)
        # Handle datetime
        if isinstance(value, datetime):
            return value.isoformat()
        return value
    except Exception:
        return default


def export_all_data(output_path, environment='local'):
    """
    Export all database tables to JSON.

    Args:
        output_path: Path to output JSON file
        environment: 'local', 'staging', or 'production'

    Returns:
        Path to created backup file
    """
    # Import here to avoid circular imports
    from main import create_app
    from model import db, User, Admin, SuperAdmin, Tool, ToolAccess, UsageLog, EmailTemplate

    # Configure environment
    if environment == 'local':
        os.environ.setdefault('IS_LOCAL', 'true')
    else:
        os.environ['IS_LOCAL'] = 'false'

    app = create_app()

    with app.app_context():
        logger.info("Starting comprehensive data export...")

        # Get database info
        db_url = str(db.engine.url)
        is_postgresql = 'postgresql' in db_url or 'postgres' in db_url

        # Mask password in URL for logging
        if '@' in db_url:
            masked_url = db_url.split('@')[0].rsplit(':', 1)[0] + ':****@' + db_url.split('@')[1]
        else:
            masked_url = db_url

        logger.info(f"Source database: {masked_url}")
        logger.info(f"Database type: {'PostgreSQL' if is_postgresql else 'SQLite'}")

        # Initialize export structure
        export_data = {
            "export_metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "environment": environment,
                "database_type": "PostgreSQL" if is_postgresql else "SQLite",
                "version": app.config.get('VERSION', 'unknown'),
                "tables": {}
            },
            "users": [],
            "admins": [],
            "super_admins": [],
            "tools": [],
            "tool_access": [],
            "usage_logs": [],
            "email_templates": []
        }

        # Export Users
        logger.info("Exporting users...")
        try:
            users = User.query.all()
            for user in users:
                export_data["users"].append({
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "name": get_safe_value(user, 'name'),
                    "fname": get_safe_value(user, 'fname'),
                    "lname": get_safe_value(user, 'lname'),
                    "address": get_safe_value(user, 'address'),
                    "city": get_safe_value(user, 'city'),
                    "state": get_safe_value(user, 'state'),
                    "zip": get_safe_value(user, 'zip'),
                    "password": user.password,  # Already hashed
                    "role": user.role,
                    "email_verified": get_safe_value(user, 'email_verified', False),
                    "email_verification_token": get_safe_value(user, 'email_verification_token'),
                    "email_verification_sent_at": get_safe_value(user, 'email_verification_sent_at'),
                    "oauth_provider": get_safe_value(user, 'oauth_provider'),
                    "oauth_id": get_safe_value(user, 'oauth_id'),
                    "requires_password_setup": get_safe_value(user, 'requires_password_setup', False),
                    "created_at": get_safe_value(user, 'created_at'),
                    "updated_at": get_safe_value(user, 'updated_at'),
                    "last_login": get_safe_value(user, 'last_login'),
                    "is_active": get_safe_value(user, 'is_active', True)
                })
            export_data["export_metadata"]["tables"]["users"] = len(users)
            logger.info(f"  Exported {len(users)} users")
        except Exception as e:
            logger.error(f"  Failed to export users: {e}")
            export_data["export_metadata"]["tables"]["users"] = 0

        # Export Admins (junction table)
        logger.info("Exporting admins...")
        try:
            admins = Admin.query.all()
            for admin in admins:
                export_data["admins"].append({
                    "id": admin.id,
                    "admin_level": get_safe_value(admin, 'admin_level', 1)
                })
            export_data["export_metadata"]["tables"]["admins"] = len(admins)
            logger.info(f"  Exported {len(admins)} admins")
        except Exception as e:
            logger.error(f"  Failed to export admins: {e}")
            export_data["export_metadata"]["tables"]["admins"] = 0

        # Export SuperAdmins (junction table)
        logger.info("Exporting super_admins...")
        try:
            super_admins = SuperAdmin.query.all()
            for sa in super_admins:
                export_data["super_admins"].append({
                    "id": sa.id
                })
            export_data["export_metadata"]["tables"]["super_admins"] = len(super_admins)
            logger.info(f"  Exported {len(super_admins)} super_admins")
        except Exception as e:
            logger.error(f"  Failed to export super_admins: {e}")
            export_data["export_metadata"]["tables"]["super_admins"] = 0

        # Export Tools
        logger.info("Exporting tools...")
        try:
            tools = Tool.query.all()
            for tool in tools:
                export_data["tools"].append({
                    "id": tool.id,
                    "name": tool.name,
                    "description": get_safe_value(tool, 'description'),
                    "route": tool.route,
                    "is_default": get_safe_value(tool, 'is_default', False),
                    "is_active": get_safe_value(tool, 'is_active', True),
                    "created_at": get_safe_value(tool, 'created_at')
                })
            export_data["export_metadata"]["tables"]["tools"] = len(tools)
            logger.info(f"  Exported {len(tools)} tools")
        except Exception as e:
            logger.error(f"  Failed to export tools: {e}")
            export_data["export_metadata"]["tables"]["tools"] = 0

        # Export ToolAccess
        logger.info("Exporting tool_access...")
        try:
            tool_accesses = ToolAccess.query.all()
            for ta in tool_accesses:
                export_data["tool_access"].append({
                    "id": ta.id,
                    "user_id": ta.user_id,
                    "tool_name": ta.tool_name
                })
            export_data["export_metadata"]["tables"]["tool_access"] = len(tool_accesses)
            logger.info(f"  Exported {len(tool_accesses)} tool_access records")
        except Exception as e:
            logger.error(f"  Failed to export tool_access: {e}")
            export_data["export_metadata"]["tables"]["tool_access"] = 0

        # Export UsageLogs
        logger.info("Exporting usage_logs...")
        try:
            usage_logs = UsageLog.query.all()
            for log in usage_logs:
                export_data["usage_logs"].append({
                    "id": log.id,
                    "user_id": log.user_id,
                    "tool_name": log.tool_name,
                    "timestamp": get_safe_value(log, 'timestamp')
                })
            export_data["export_metadata"]["tables"]["usage_logs"] = len(usage_logs)
            logger.info(f"  Exported {len(usage_logs)} usage_logs")
        except Exception as e:
            logger.error(f"  Failed to export usage_logs: {e}")
            export_data["export_metadata"]["tables"]["usage_logs"] = 0

        # Export EmailTemplates
        logger.info("Exporting email_templates...")
        try:
            templates = EmailTemplate.query.all()
            for template in templates:
                export_data["email_templates"].append({
                    "id": template.id,
                    "user_id": template.user_id,
                    "title": template.title,
                    "content": template.content
                })
            export_data["export_metadata"]["tables"]["email_templates"] = len(templates)
            logger.info(f"  Exported {len(templates)} email_templates")
        except Exception as e:
            logger.error(f"  Failed to export email_templates: {e}")
            export_data["export_metadata"]["tables"]["email_templates"] = 0

        # Create output directory if needed
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Write JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        # Calculate file size
        file_size = os.path.getsize(output_path)
        size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} bytes"

        logger.info("")
        logger.info("=" * 50)
        logger.info("EXPORT COMPLETE")
        logger.info("=" * 50)
        logger.info(f"Output file: {output_path}")
        logger.info(f"File size: {size_str}")
        logger.info("")
        logger.info("Summary:")
        for table, count in export_data["export_metadata"]["tables"].items():
            logger.info(f"  {table}: {count} records")

        return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Export all database tables to JSON backup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Export local database (default)
    python scripts/export_all_data.py

    # Export to specific file
    python scripts/export_all_data.py --output data/backups/my_backup.json

    # Export staging database (run on Heroku)
    heroku run python scripts/export_all_data.py --env staging -a omnitool-by-xdv-staging
        """
    )
    parser.add_argument(
        '--output', '-o',
        default=f"data/backups/full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        help='Output file path (default: timestamped file in data/backups/)'
    )
    parser.add_argument(
        '--env', '-e',
        choices=['local', 'staging', 'production'],
        default='local',
        help='Environment to export from (default: local)'
    )

    args = parser.parse_args()

    try:
        export_all_data(args.output, args.env)
    except Exception as e:
        logger.error(f"Export failed: {e}")
        sys.exit(1)
