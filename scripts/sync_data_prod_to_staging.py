"""
Production to Staging Data Sync Script

Refreshes staging database with production data using Heroku Postgres follower pattern.
This ensures staging mirrors production for realistic testing.

IMPORTANT: This script requires Heroku CLI and appropriate permissions.

Usage:
    # Sync prod -> staging (Heroku follower method)
    python scripts/sync_data_prod_to_staging.py

    # Dry-run (shows what would happen)
    python scripts/sync_data_prod_to_staging.py --dry-run

    # Check current follower status
    python scripts/sync_data_prod_to_staging.py --check-status

Strategy:
    1. Backup current staging database
    2. Create follower database from production
    3. Wait for follower to sync (check lag)
    4. Unfollow (detach from production)
    5. Promote follower to staging's DATABASE_URL
    6. Verify data integrity

Note: This operation requires Heroku Postgres Standard or higher tier for follower support.
"""

import os
import sys
import subprocess
import time
import argparse
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("sync_data_prod_to_staging")

# Heroku app names
PRODUCTION_APP = "omnitool-by-xdv"
STAGING_APP = "omnitool-by-xdv-staging"


def run_command(command, check=True, capture_output=True):
    """
    Run a shell command and return the result

    Args:
        command: Command to run (string or list)
        check: Raise exception on non-zero exit
        capture_output: Capture stdout/stderr

    Returns:
        CompletedProcess object
    """
    if isinstance(command, str):
        command = command.split()

    logger.debug(f"Running: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            check=check,
            capture_output=capture_output,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(command)}")
        logger.error(f"Exit code: {e.returncode}")
        if e.stdout:
            logger.error(f"Stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"Stderr: {e.stderr}")
        raise
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {' '.join(command)}")
        raise


def check_heroku_cli():
    """Verify Heroku CLI is installed and authenticated"""
    try:
        result = run_command("heroku --version")
        logger.info(f"Heroku CLI: {result.stdout.strip()}")

        # Check authentication
        result = run_command("heroku auth:whoami")
        logger.info(f"Authenticated as: {result.stdout.strip()}")
        return True
    except Exception as e:
        logger.error(f"Heroku CLI check failed: {str(e)}")
        logger.error("Please install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli")
        logger.error("And authenticate: heroku login")
        return False


def backup_staging_database(dry_run=False):
    """Create backup of current staging database"""
    logger.info(f"[Step 1/6] Backing up staging database...")

    if dry_run:
        logger.info("[DRY RUN] Would create staging backup")
        return True

    try:
        run_command(f"heroku pg:backups:capture -a {STAGING_APP}")
        logger.info("[SUCCESS] Staging backup created")
        return True
    except Exception as e:
        logger.error(f"[ERROR] Failed to backup staging: {str(e)}")
        return False


def get_production_database_url():
    """Get production DATABASE_URL"""
    try:
        result = run_command(f"heroku config:get DATABASE_URL -a {PRODUCTION_APP}")
        db_url = result.stdout.strip()
        if db_url:
            logger.info("[SUCCESS] Retrieved production DATABASE_URL")
            return db_url
        else:
            raise ValueError("DATABASE_URL is empty")
    except Exception as e:
        logger.error(f"[ERROR] Failed to get production DATABASE_URL: {str(e)}")
        return None


def create_follower_database(dry_run=False):
    """
    Create a follower database from production

    Returns:
        Follower database name (e.g., "HEROKU_POSTGRESQL_PINK")
    """
    logger.info(f"[Step 2/6] Creating follower database from production...")

    if dry_run:
        logger.info("[DRY RUN] Would create follower database")
        logger.info(f"  Command: heroku addons:create heroku-postgresql:standard-0 \\")
        logger.info(f"    --follow DATABASE_URL \\")
        logger.info(f"    --app {STAGING_APP}")
        return "HEROKU_POSTGRESQL_PINK"  # Mock name for dry-run

    try:
        # Create follower addon
        # Note: This requires Standard tier or higher ($50+/month)
        result = run_command([
            "heroku", "addons:create", "heroku-postgresql:standard-0",
            "--follow", "DATABASE_URL",
            "--app", STAGING_APP
        ])

        # Extract follower name from output
        # Example output: "Creating heroku-postgresql:standard-0 on omnitool-by-xdv-staging... done, HEROKU_POSTGRESQL_PINK"
        output = result.stdout
        match = re.search(r'HEROKU_POSTGRESQL_\w+', output)

        if match:
            follower_name = match.group(0)
            logger.info(f"[SUCCESS] Created follower database: {follower_name}")
            return follower_name
        else:
            logger.error("Could not parse follower name from output")
            logger.error(f"Output: {output}")
            return None

    except Exception as e:
        logger.error(f"[ERROR] Failed to create follower: {str(e)}")
        logger.error("\nTroubleshooting:")
        logger.error("  1. Ensure staging app has a Postgres addon")
        logger.error("  2. Verify your Heroku plan supports followers (Standard tier+)")
        logger.error("  3. Check billing is up to date")
        return None


def wait_for_follower_sync(follower_name, timeout=3600, dry_run=False):
    """
    Wait for follower to sync with production

    Args:
        follower_name: Name of follower database
        timeout: Maximum wait time in seconds (default: 1 hour)
        dry_run: Simulation mode

    Returns:
        True if synced, False otherwise
    """
    logger.info(f"[Step 3/6] Waiting for follower to sync with production...")

    if dry_run:
        logger.info("[DRY RUN] Would wait for follower sync")
        logger.info("  Typically takes 1-5 minutes for small databases")
        return True

    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            # Check follower status
            result = run_command(f"heroku pg:info {follower_name} -a {STAGING_APP}")
            output = result.stdout

            # Look for "Behind By" indicator
            # Example: "Behind By: 0 commits" means synced
            if "Behind By: 0" in output or "Behind By: 0 commits" in output:
                logger.info("[SUCCESS] Follower is synced with production")
                return True

            # Extract lag info if available
            lag_match = re.search(r'Behind By:\s*(\d+)', output)
            if lag_match:
                lag = lag_match.group(1)
                logger.info(f"Follower lag: {lag} commits behind...")
            else:
                logger.info("Checking follower status...")

            time.sleep(10)  # Check every 10 seconds

        except Exception as e:
            logger.warning(f"Error checking follower status: {str(e)}")
            time.sleep(10)

    logger.error(f"[ERROR] Follower did not sync within {timeout} seconds")
    return False


def unfollow_database(follower_name, dry_run=False):
    """Detach follower from production (stop replication)"""
    logger.info(f"[Step 4/6] Unfollowing (detaching from production)...")

    if dry_run:
        logger.info("[DRY RUN] Would unfollow database")
        logger.info(f"  Command: heroku pg:unfollow {follower_name} -a {STAGING_APP}")
        return True

    try:
        run_command(f"heroku pg:unfollow {follower_name} -a {STAGING_APP}")
        logger.info("[SUCCESS] Follower detached from production")
        return True
    except Exception as e:
        logger.error(f"[ERROR] Failed to unfollow: {str(e)}")
        return False


def promote_follower_to_primary(follower_name, dry_run=False):
    """Promote follower to DATABASE_URL (staging's primary database)"""
    logger.info(f"[Step 5/6] Promoting follower to primary database...")

    if dry_run:
        logger.info("[DRY RUN] Would promote follower to DATABASE_URL")
        logger.info(f"  Command: heroku pg:promote {follower_name} -a {STAGING_APP}")
        logger.info("  This will:")
        logger.info("    - Update DATABASE_URL to point to follower")
        logger.info("    - Restart staging app")
        logger.info("    - Old database becomes accessible via color name")
        return True

    try:
        run_command(f"heroku pg:promote {follower_name} -a {STAGING_APP}")
        logger.info("[SUCCESS] Follower promoted to DATABASE_URL")
        logger.info("Staging app will restart automatically")
        return True
    except Exception as e:
        logger.error(f"[ERROR] Failed to promote follower: {str(e)}")
        return False


def verify_data_integrity(dry_run=False):
    """Verify staging database has expected data"""
    logger.info(f"[Step 6/6] Verifying data integrity...")

    if dry_run:
        logger.info("[DRY RUN] Would verify data integrity")
        logger.info("  Checks:")
        logger.info("    - Database connectivity")
        logger.info("    - Row counts for key tables")
        logger.info("    - Sample data query")
        return True

    try:
        # Run basic verification queries
        queries = [
            ("Users", "SELECT COUNT(*) FROM users"),
            ("Tools", "SELECT COUNT(*) FROM tools"),
            ("Tool Access", "SELECT COUNT(*) FROM tool_access"),
            ("Email Templates", "SELECT COUNT(*) FROM email_templates")
        ]

        logger.info("Running verification queries...")
        for name, query in queries:
            result = run_command(
                f'heroku pg:psql -a {STAGING_APP} -c "{query}"',
                check=False
            )
            if result.returncode == 0:
                logger.info(f"  {name}: {result.stdout.strip()}")
            else:
                logger.warning(f"  {name}: Query failed")

        logger.info("[SUCCESS] Data integrity verification complete")
        return True

    except Exception as e:
        logger.error(f"[ERROR] Verification failed: {str(e)}")
        return False


def check_follower_status():
    """Check current follower databases"""
    logger.info("Checking for existing follower databases...")

    try:
        result = run_command(f"heroku pg:info -a {STAGING_APP}")
        output = result.stdout

        if "Following" in output:
            logger.info("Found follower database(s):")
            logger.info(output)
        else:
            logger.info("No active followers found")

        return True
    except Exception as e:
        logger.error(f"Failed to check status: {str(e)}")
        return False


def sync_prod_to_staging(dry_run=False):
    """
    Main synchronization workflow

    Returns:
        True if successful, False otherwise
    """
    logger.info("="*60)
    logger.info("PRODUCTION -> STAGING DATA SYNC")
    logger.info("="*60)
    logger.info(f"Production app: {PRODUCTION_APP}")
    logger.info(f"Staging app: {STAGING_APP}")

    if dry_run:
        logger.info("[DRY RUN MODE] No changes will be made")

    logger.info("="*60)

    # Step 0: Prerequisites
    if not check_heroku_cli():
        return False

    # Step 1: Backup staging
    if not backup_staging_database(dry_run):
        logger.error("Backup failed. Aborting sync.")
        return False

    # Step 2: Create follower
    follower_name = create_follower_database(dry_run)
    if not follower_name:
        logger.error("Failed to create follower. Aborting sync.")
        return False

    # Step 3: Wait for sync
    if not wait_for_follower_sync(follower_name, dry_run=dry_run):
        logger.error("Follower sync failed. Aborting sync.")
        logger.error(f"You may need to manually destroy the follower: heroku addons:destroy {follower_name} -a {STAGING_APP}")
        return False

    # Step 4: Unfollow
    if not unfollow_database(follower_name, dry_run):
        logger.error("Failed to unfollow. Aborting sync.")
        return False

    # Step 5: Promote
    if not promote_follower_to_primary(follower_name, dry_run):
        logger.error("Failed to promote follower. Aborting sync.")
        return False

    # Step 6: Verify
    if not verify_data_integrity(dry_run):
        logger.warning("Verification had warnings, but sync completed")

    logger.info("="*60)
    logger.info("[SUCCESS] Production data synced to staging!")
    logger.info("="*60)
    logger.info("\nNext steps:")
    logger.info("  1. Verify staging app is running: heroku open -a omnitool-by-xdv-staging")
    logger.info("  2. Check staging logs: heroku logs --tail -a omnitool-by-xdv-staging")
    logger.info("  3. Run migrations: heroku run python migrate_db.py -a omnitool-by-xdv-staging")
    logger.info("  4. Import tool access: heroku run python scripts/import_tool_access.py ...")

    return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Sync production data to staging using Heroku follower',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync prod -> staging
  python scripts/sync_data_prod_to_staging.py

  # Dry-run (preview what would happen)
  python scripts/sync_data_prod_to_staging.py --dry-run

  # Check follower status
  python scripts/sync_data_prod_to_staging.py --check-status

Requirements:
  - Heroku CLI installed and authenticated
  - Production and staging apps exist
  - Staging app has Postgres Standard tier or higher (for follower support)
  - HEROKU_API_KEY set in environment (for CI/CD)

Cost:
  - Heroku Postgres Standard-0: ~$50/month
  - Follower database: Same as primary (may incur additional cost during sync)
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview actions without making changes'
    )

    parser.add_argument(
        '--check-status',
        action='store_true',
        help='Check current follower database status'
    )

    args = parser.parse_args()

    try:
        if args.check_status:
            success = check_follower_status()
        else:
            success = sync_prod_to_staging(dry_run=args.dry_run)

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.info("\n[INTERRUPTED] Sync cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"[ERROR] Sync failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
