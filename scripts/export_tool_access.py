"""
Tool Access Export Script

Exports tool_access permissions to version-controlled JSON for sync across environments.
Captures the exact permission state including user context for auditing.

Usage:
    # Export from local development
    python scripts/export_tool_access.py --env local

    # Export from local with custom output path
    python scripts/export_tool_access.py --env local --output data/tool_access_exports/dev_tool_access.json

    # Export from staging (requires HEROKU_API_KEY)
    python scripts/export_tool_access.py --env staging

    # Export from production (requires HEROKU_API_KEY)
    python scripts/export_tool_access.py --env production
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime, timezone

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model import db, Tool, ToolAccess, User
from main import create_app

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("export_tool_access")


def get_app_version():
    """Get the current application version from CLAUDE.md or a version file"""
    try:
        claude_md_path = os.path.join(os.path.dirname(__file__), '..', 'CLAUDE.md')
        with open(claude_md_path, 'r') as f:
            content = f.read()
            # Look for version in CLAUDE.md
            if 'Current version:' in content:
                for line in content.split('\n'):
                    if 'Current version:' in line:
                        version = line.split('Current version:')[1].strip()
                        return version
        return "1.4.3"  # Fallback version
    except Exception:
        return "1.4.3"


def export_tool_access(environment='local', output_path=None, app=None):
    """
    Export tool_access permissions to JSON file

    Args:
        environment: 'local', 'staging', or 'production'
        output_path: Custom output path (optional)
        app: Flask app instance (optional, uses current_app or creates new one)

    Returns:
        Path to the created export file
    """
    # Set environment variables based on target (only if not using provided app)
    if app is None:
        if environment == 'local':
            os.environ['IS_LOCAL'] = 'true'
            os.environ['FLASK_ENV'] = 'development'
        elif environment == 'staging':
            os.environ['IS_LOCAL'] = 'false'
            os.environ['FLASK_ENV'] = 'staging'
        elif environment == 'production':
            os.environ['IS_LOCAL'] = 'false'
            os.environ['FLASK_ENV'] = 'production'
        else:
            raise ValueError(f"Invalid environment: {environment}. Must be 'local', 'staging', or 'production'")

    # Determine output path
    if output_path is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'tool_access_exports')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{environment}_tool_access.json')

    logger.info(f"Exporting tool access from {environment} environment...")

    # Use provided app or create new one
    if app is None:
        from flask import has_app_context, current_app
        if has_app_context():
            app = current_app._get_current_object()
        else:
            app = create_app()

    with app.app_context():
        try:
            # Verify database connectivity
            db.session.execute(db.text('SELECT 1'))
            current_db = db.engine.url.render_as_string(hide_password=True)
            logger.info(f"Connected to database: {current_db}")

            # Query tool access with user context
            logger.info("Querying tool_access records with user context...")
            tool_access_query = db.session.query(
                ToolAccess.user_id,
                ToolAccess.tool_name,
                User.username,
                User.email
            ).join(User, ToolAccess.user_id == User.id).all()

            tool_access_list = []
            for row in tool_access_query:
                tool_access_list.append({
                    "user_id": row.user_id,
                    "username": row.username,
                    "email": row.email,
                    "tool_name": row.tool_name
                })

            logger.info(f"Found {len(tool_access_list)} tool access grants")

            # Query tool definitions
            logger.info("Querying tool definitions...")
            tools_query = Tool.query.all()
            tools_list = []
            for tool in tools_query:
                tools_list.append({
                    "name": tool.name,
                    "description": tool.description,
                    "route": tool.route,
                    "is_default": tool.is_default,
                    "is_active": getattr(tool, 'is_active', True)
                })

            logger.info(f"Found {len(tools_list)} tool definitions")

            # Get user count
            user_count = User.query.count()

            # Build export data
            export_data = {
                "export_metadata": {
                    "environment": environment,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "version": get_app_version(),
                    "total_users": user_count,
                    "total_grants": len(tool_access_list),
                    "total_tools": len(tools_list)
                },
                "tool_access": sorted(tool_access_list, key=lambda x: (x['username'], x['tool_name'])),
                "tools": sorted(tools_list, key=lambda x: x['name'])
            }

            # Write JSON (pretty-printed for git diff)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, sort_keys=True, ensure_ascii=False)

            logger.info(f"[SUCCESS] Successfully exported {len(tool_access_list)} grants to {output_path}")
            logger.info(f"Export summary:")
            logger.info(f"  - Total users: {user_count}")
            logger.info(f"  - Total tools: {len(tools_list)}")
            logger.info(f"  - Total grants: {len(tool_access_list)}")

            # Show grant distribution
            tool_grant_counts = {}
            for grant in tool_access_list:
                tool_name = grant['tool_name']
                tool_grant_counts[tool_name] = tool_grant_counts.get(tool_name, 0) + 1

            logger.info(f"Grant distribution by tool:")
            for tool_name in sorted(tool_grant_counts.keys()):
                logger.info(f"  - {tool_name}: {tool_grant_counts[tool_name]} users")

            return output_path

        except Exception as e:
            logger.error(f"Failed to export tool access: {str(e)}")
            raise


def main():
    """Main entry point for command-line usage"""
    parser = argparse.ArgumentParser(
        description='Export tool_access permissions to JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export from local development
  python scripts/export_tool_access.py --env local

  # Export from staging
  python scripts/export_tool_access.py --env staging

  # Export with custom output path
  python scripts/export_tool_access.py --env local --output custom_export.json
        """
    )

    parser.add_argument(
        '--env',
        choices=['local', 'staging', 'production'],
        default='local',
        help='Environment to export from (default: local)'
    )

    parser.add_argument(
        '--output',
        help='Custom output file path (optional)'
    )

    args = parser.parse_args()

    try:
        output_path = export_tool_access(
            environment=args.env,
            output_path=args.output
        )

        print(f"\n[SUCCESS] Export successful!")
        print(f"File: {output_path}")
        print(f"\nNext steps:")
        print(f"  1. Review the export: cat {output_path}")
        print(f"  2. Commit to git: git add {output_path}")
        print(f"  3. Commit message: git commit -m 'feat(tools): Update tool access permissions'")

        sys.exit(0)

    except Exception as e:
        logger.error(f"[ERROR] Export failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
