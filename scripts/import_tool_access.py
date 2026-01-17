"""
Tool Access Import Script

Imports tool_access permissions from JSON export to target environment.
Supports merge mode (safe, additive) and overwrite mode (destructive).

Usage:
    # Import to local (merge mode - safe, default)
    python scripts/import_tool_access.py --source data/tool_access_exports/dev_tool_access.json

    # Dry-run to preview changes
    python scripts/import_tool_access.py --source data/tool_access_exports/dev_tool_access.json --dry-run

    # Import to staging (via Heroku)
    heroku run python scripts/import_tool_access.py \\
        --source data/tool_access_exports/dev_tool_access.json \\
        --mode merge \\
        -a omnitool-by-xdv-staging

    # Overwrite mode (dangerous - requires confirmation)
    python scripts/import_tool_access.py --source data/tool_access_exports/dev_tool_access.json --mode overwrite --confirm
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model import db, Tool, ToolAccess, User
from main import create_app

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("import_tool_access")


def load_export_file(source_path):
    """Load and validate export JSON file"""
    logger.info(f"Loading export file: {source_path}")

    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Export file not found: {source_path}")

    with open(source_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Validate structure
    required_keys = ['export_metadata', 'tool_access', 'tools']
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Invalid export file: missing '{key}' key")

    metadata = data['export_metadata']
    logger.info(f"Export metadata:")
    logger.info(f"  - Environment: {metadata.get('environment')}")
    logger.info(f"  - Timestamp: {metadata.get('timestamp')}")
    logger.info(f"  - Version: {metadata.get('version')}")
    logger.info(f"  - Total users: {metadata.get('total_users')}")
    logger.info(f"  - Total grants: {metadata.get('total_grants')}")
    logger.info(f"  - Total tools: {metadata.get('total_tools')}")

    return data


def import_tool_access(source_path, mode='merge', dry_run=False, confirmed=False, app=None):
    """
    Import tool_access permissions from JSON export

    Args:
        source_path: Path to JSON export file
        mode: 'merge' (additive, safe) or 'overwrite' (destructive)
        dry_run: Preview changes without committing
        confirmed: Required for overwrite mode
        app: Flask app instance (optional, uses current_app or creates new one)

    Returns:
        Dict with import statistics
    """
    if mode not in ['merge', 'overwrite']:
        raise ValueError(f"Invalid mode: {mode}. Must be 'merge' or 'overwrite'")

    if mode == 'overwrite' and not confirmed and not dry_run:
        logger.error("[WARNING]  OVERWRITE MODE requires explicit confirmation!")
        logger.error("   This will DELETE all existing tool_access records.")
        logger.error("   Use --confirm flag to proceed or --dry-run to preview.")
        raise ValueError("Overwrite mode requires confirmation")

    # Load export data
    import_data = load_export_file(source_path)

    # Use provided app or create new one
    if app is None:
        from flask import has_app_context, current_app
        if has_app_context():
            app = current_app._get_current_object()
        else:
            app = create_app()

    stats = {
        'grants_created': 0,
        'grants_skipped': 0,
        'grants_deleted': 0,
        'orphaned_users': [],
        'orphaned_tools': []
    }

    with app.app_context():
        try:
            # Verify database connectivity
            db.session.execute(db.text('SELECT 1'))
            current_db = db.engine.url.render_as_string(hide_password=True)
            logger.info(f"Connected to database: {current_db}")

            # Validate tools exist in target database
            logger.info("Validating tools in target database...")
            imported_tools = {t['name'] for t in import_data['tools']}
            existing_tools = {t.name for t in Tool.query.all()}
            missing_tools = imported_tools - existing_tools

            if missing_tools:
                logger.error(f"[ERROR] Tools in import not found in target database:")
                for tool_name in sorted(missing_tools):
                    logger.error(f"   - {tool_name}")
                logger.error(f"\nRun 'python sync_tools.py' first to create missing tools")
                raise ValueError(f"Missing tools: {missing_tools}")

            logger.info(f"[SUCCESS] All {len(imported_tools)} tools exist in target database")

            # Build user mapping (username, email) -> user_id
            logger.info("Building user mapping...")
            user_mapping = {}
            for user in User.query.all():
                user_mapping[(user.username, user.email)] = user.id

            logger.info(f"Found {len(user_mapping)} users in target database")

            # Handle overwrite mode
            if mode == 'overwrite':
                logger.warning("[WARNING]  OVERWRITE MODE: All existing grants will be deleted!")
                if not dry_run:
                    existing_count = ToolAccess.query.count()
                    ToolAccess.query.delete()
                    stats['grants_deleted'] = existing_count
                    logger.info(f"Deleted {existing_count} existing tool_access records")
                else:
                    logger.info(f"[DRY RUN] Would delete {ToolAccess.query.count()} existing records")

            # Process imports
            logger.info(f"\nProcessing {len(import_data['tool_access'])} grants from import...")

            for grant in import_data['tool_access']:
                username = grant['username']
                email = grant['email']
                tool_name = grant['tool_name']

                # Find user in target database
                user_key = (username, email)
                target_user_id = user_mapping.get(user_key)

                if not target_user_id:
                    stats['orphaned_users'].append(grant)
                    logger.debug(f"Skipping grant for non-existent user: {username} ({email}) -> {tool_name}")
                    continue

                # Check if tool exists (should always pass due to earlier validation)
                if tool_name not in existing_tools:
                    stats['orphaned_tools'].append(grant)
                    logger.debug(f"Skipping grant for non-existent tool: {username} -> {tool_name}")
                    continue

                # Check if grant already exists (idempotent)
                existing_grant = ToolAccess.query.filter_by(
                    user_id=target_user_id,
                    tool_name=tool_name
                ).first()

                if existing_grant:
                    stats['grants_skipped'] += 1
                    logger.debug(f"Skipping existing grant: {username} -> {tool_name}")
                    continue

                # Create new grant
                stats['grants_created'] += 1
                logger.info(f"Creating grant: {username} ({email}) -> {tool_name}")

                if not dry_run:
                    new_grant = ToolAccess(
                        user_id=target_user_id,
                        tool_name=tool_name
                    )
                    db.session.add(new_grant)

            # Commit transaction
            if not dry_run:
                logger.info("\nCommitting changes...")
                db.session.commit()
                logger.info("[SUCCESS] Transaction committed successfully")
            else:
                logger.info("\n[DRY RUN] No changes committed")

            # Print summary
            print("\n" + "=" * 60)
            print("IMPORT SUMMARY")
            print("=" * 60)
            print(f"Mode: {mode.upper()}")
            print(f"Dry Run: {'Yes' if dry_run else 'No'}")
            print(f"\nGrants created: {stats['grants_created']}")
            print(f"Grants skipped (already exist): {stats['grants_skipped']}")

            if mode == 'overwrite':
                print(f"Grants deleted: {stats['grants_deleted']}")

            if stats['orphaned_users']:
                print(f"\n[WARNING]  Orphaned users (not in target DB): {len(stats['orphaned_users'])}")
                for grant in stats['orphaned_users'][:10]:  # Show first 10
                    print(f"   - {grant['username']} ({grant['email']}) -> {grant['tool_name']}")
                if len(stats['orphaned_users']) > 10:
                    print(f"   ... and {len(stats['orphaned_users']) - 10} more")

            if stats['orphaned_tools']:
                print(f"\n[WARNING]  Orphaned tools (not in target DB): {len(stats['orphaned_tools'])}")
                for grant in stats['orphaned_tools'][:10]:
                    print(f"   - {grant['username']} -> {grant['tool_name']}")

            print("=" * 60)

            if dry_run:
                print("\n[INFO]  This was a dry run. No changes were made.")
                print("   Remove --dry-run flag to apply changes.")

            return stats

        except Exception as e:
            if not dry_run:
                db.session.rollback()
                logger.error(f"Transaction rolled back due to error: {str(e)}")
            raise


def main():
    """Main entry point for command-line usage"""
    parser = argparse.ArgumentParser(
        description='Import tool_access permissions from JSON export',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Merge mode (safe, default) - adds new grants, preserves existing
  python scripts/import_tool_access.py --source data/tool_access_exports/dev_tool_access.json

  # Dry-run to preview changes
  python scripts/import_tool_access.py --source data/tool_access_exports/dev_tool_access.json --dry-run

  # Overwrite mode (dangerous) - replaces all grants
  python scripts/import_tool_access.py --source data/tool_access_exports/dev_tool_access.json --mode overwrite --confirm

  # Import to Heroku staging
  heroku run python scripts/import_tool_access.py \\
      --source data/tool_access_exports/dev_tool_access.json \\
      --mode merge \\
      -a omnitool-by-xdv-staging
        """
    )

    parser.add_argument(
        '--source',
        required=True,
        help='Path to JSON export file'
    )

    parser.add_argument(
        '--mode',
        choices=['merge', 'overwrite'],
        default='merge',
        help='Import mode: merge (safe, additive) or overwrite (destructive). Default: merge'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without committing to database'
    )

    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Required flag for overwrite mode (confirms destructive action)'
    )

    args = parser.parse_args()

    try:
        # Additional safety check for overwrite mode
        if args.mode == 'overwrite' and not args.confirm and not args.dry_run:
            print("\n[WARNING]  ERROR: Overwrite mode requires explicit confirmation!")
            print("\nOverwrite mode will DELETE all existing tool_access records")
            print("and replace them with the import file contents.")
            print("\nTo proceed with overwrite:")
            print("  1. Run with --dry-run first to preview changes")
            print("  2. Then run with --confirm flag to apply changes")
            print("\nExample:")
            print(f"  python scripts/import_tool_access.py --source {args.source} --mode overwrite --dry-run")
            print(f"  python scripts/import_tool_access.py --source {args.source} --mode overwrite --confirm")
            sys.exit(1)

        stats = import_tool_access(
            source_path=args.source,
            mode=args.mode,
            dry_run=args.dry_run,
            confirmed=args.confirm
        )

        if not args.dry_run:
            print(f"\n[SUCCESS] Import successful!")
            print(f"\nNext steps:")
            print(f"  1. Verify grants in admin UI or database")
            print(f"  2. Test tool access with affected users")

        sys.exit(0)

    except Exception as e:
        logger.error(f"[ERROR] Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
