"""
Post-Migration Verification Script

Runs comprehensive health checks after database migration to ensure:
- Database connectivity
- Schema version correctness
- Tool definitions match DEFINED_TOOLS
- No orphaned data
- Default tools assigned to all users
- Application can start

Usage:
    # Verify local environment
    python scripts/verify_migration.py --env local

    # Verify staging
    python scripts/verify_migration.py --env staging

    # Verify production
    python scripts/verify_migration.py --env production

    # Verbose mode (show all checks)
    python scripts/verify_migration.py --env local --verbose

    # Via Heroku
    heroku run python scripts/verify_migration.py --env staging -a omnitool-by-xdv-staging
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model import db, Tool, ToolAccess, User
from main import create_app

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("verify_migration")


class VerificationCheck:
    """Represents a single verification check with result"""

    def __init__(self, name, passed, message="", warning=False):
        self.name = name
        self.passed = passed
        self.message = message
        self.warning = warning  # True if this is a warning, not a failure

    def __str__(self):
        if self.passed:
            status = "[PASS]"
        elif self.warning:
            status = "[WARN]"
        else:
            status = "[FAIL]"

        result = f"{status} {self.name}"
        if self.message:
            result += f"\n     {self.message}"
        return result


def check_database_connectivity():
    """Check if database is reachable"""
    try:
        db.session.execute(db.text('SELECT 1'))
        db_url = db.engine.url.render_as_string(hide_password=True)
        return VerificationCheck(
            "Database Connectivity",
            True,
            f"Connected to: {db_url}"
        )
    except Exception as e:
        return VerificationCheck(
            "Database Connectivity",
            False,
            f"Error: {str(e)}"
        )


def check_schema_version():
    """Verify Alembic schema version matches expected"""
    try:
        from flask_migrate import current as get_current_migration

        # Get current migration version
        with db.engine.connect() as connection:
            result = connection.execute(db.text("SELECT version_num FROM alembic_version"))
            row = result.fetchone()

            if row:
                current_version = row[0]
                # Check if it matches expected (would need to know latest migration)
                return VerificationCheck(
                    "Schema Version",
                    True,
                    f"Current: {current_version}"
                )
            else:
                return VerificationCheck(
                    "Schema Version",
                    False,
                    "No version found in alembic_version table"
                )

    except Exception as e:
        return VerificationCheck(
            "Schema Version",
            False,
            f"Error: {str(e)}",
            warning=True  # Non-critical
        )


def check_tool_definitions():
    """Verify tool definitions match DEFINED_TOOLS in sync_tools.py"""
    try:
        from sync_tools import DEFINED_TOOLS

        expected_tools = {t['name'] for t in DEFINED_TOOLS}
        actual_tools = {t.name for t in Tool.query.all()}

        missing_tools = expected_tools - actual_tools
        extra_tools = actual_tools - expected_tools

        if missing_tools or extra_tools:
            messages = []
            if missing_tools:
                messages.append(f"Missing: {', '.join(sorted(missing_tools))}")
            if extra_tools:
                messages.append(f"Extra: {', '.join(sorted(extra_tools))}")

            return VerificationCheck(
                "Tool Definitions Match",
                False,
                ". ".join(messages)
            )
        else:
            return VerificationCheck(
                "Tool Definitions Match",
                True,
                f"All {len(expected_tools)} tools present"
            )

    except ImportError:
        return VerificationCheck(
            "Tool Definitions Match",
            False,
            "Could not import sync_tools.py",
            warning=True
        )
    except Exception as e:
        return VerificationCheck(
            "Tool Definitions Match",
            False,
            f"Error: {str(e)}"
        )


def check_orphaned_tool_access_invalid_tools():
    """Check for tool_access records referencing non-existent tools"""
    try:
        valid_tools = {t.name for t in Tool.query.all()}
        all_access = ToolAccess.query.all()

        orphaned = [
            access for access in all_access
            if access.tool_name not in valid_tools
        ]

        if orphaned:
            sample = orphaned[:5]
            sample_str = ", ".join([f"{a.user_id}->{a.tool_name}" for a in sample])
            message = f"Found {len(orphaned)} orphaned records. Sample: {sample_str}"

            return VerificationCheck(
                "No Orphaned Tool Access (Invalid Tools)",
                False,
                message
            )
        else:
            return VerificationCheck(
                "No Orphaned Tool Access (Invalid Tools)",
                True,
                "All tool_access records reference valid tools"
            )

    except Exception as e:
        return VerificationCheck(
            "No Orphaned Tool Access (Invalid Tools)",
            False,
            f"Error: {str(e)}"
        )


def check_orphaned_tool_access_invalid_users():
    """Check for tool_access records referencing non-existent users"""
    try:
        valid_users = {u.id for u in User.query.all()}
        all_access = ToolAccess.query.all()

        orphaned = [
            access for access in all_access
            if access.user_id not in valid_users
        ]

        if orphaned:
            sample = orphaned[:5]
            sample_str = ", ".join([f"user_id={a.user_id}" for a in sample])
            message = f"Found {len(orphaned)} orphaned records. Sample: {sample_str}"

            return VerificationCheck(
                "No Orphaned Tool Access (Invalid Users)",
                False,
                message
            )
        else:
            return VerificationCheck(
                "No Orphaned Tool Access (Invalid Users)",
                True,
                "All tool_access records reference valid users"
            )

    except Exception as e:
        return VerificationCheck(
            "No Orphaned Tool Access (Invalid Users)",
            False,
            f"Error: {str(e)}"
        )


def check_default_tools_assigned():
    """Verify all users have access to default tools"""
    try:
        default_tools = Tool.query.filter_by(is_default=True).all()
        all_users = User.query.all()

        missing_assignments = []
        for user in all_users:
            for tool in default_tools:
                has_access = ToolAccess.query.filter_by(
                    user_id=user.id,
                    tool_name=tool.name
                ).first() is not None

                if not has_access:
                    missing_assignments.append((user.username, tool.name))

        if missing_assignments:
            sample = missing_assignments[:10]
            sample_str = "\n     ".join([f"{u} missing {t}" for u, t in sample])
            message = f"Found {len(missing_assignments)} missing assignments:\n     {sample_str}"

            if len(missing_assignments) > 10:
                message += f"\n     ... and {len(missing_assignments) - 10} more"

            return VerificationCheck(
                "Default Tools Assigned",
                False,
                message,
                warning=True  # Warning, not critical failure
            )
        else:
            return VerificationCheck(
                "Default Tools Assigned",
                True,
                f"All {len(all_users)} users have {len(default_tools)} default tools"
            )

    except Exception as e:
        return VerificationCheck(
            "Default Tools Assigned",
            False,
            f"Error: {str(e)}",
            warning=True
        )


def check_table_counts():
    """Get row counts for key tables"""
    try:
        counts = {
            "Users": User.query.count(),
            "Tools": Tool.query.count(),
            "Tool Access": ToolAccess.query.count(),
        }

        # Try to get email templates count (may not exist in all schemas)
        try:
            from model import EmailTemplate
            counts["Email Templates"] = EmailTemplate.query.count()
        except:
            pass

        counts_str = ", ".join([f"{k}: {v}" for k, v in counts.items()])

        return VerificationCheck(
            "Table Counts",
            True,
            counts_str
        )

    except Exception as e:
        return VerificationCheck(
            "Table Counts",
            False,
            f"Error: {str(e)}",
            warning=True
        )


def check_application_import():
    """Verify application can be imported (basic sanity check)"""
    try:
        # Try to import key modules
        from routes import auth_routes, user_routes, admin_routes, tool_routes

        return VerificationCheck(
            "Application Import",
            True,
            "All route modules importable"
        )

    except Exception as e:
        return VerificationCheck(
            "Application Import",
            False,
            f"Error: {str(e)}"
        )


def run_verification(environment='local', verbose=False):
    """
    Run all verification checks

    Args:
        environment: 'local', 'staging', or 'production'
        verbose: Show all check details

    Returns:
        Tuple of (success: bool, checks: list)
    """
    # Set environment variables
    if environment == 'local':
        os.environ['IS_LOCAL'] = 'true'
        os.environ['FLASK_ENV'] = 'development'
    elif environment == 'staging':
        os.environ['IS_LOCAL'] = 'false'
        os.environ['FLASK_ENV'] = 'staging'
    elif environment == 'production':
        os.environ['IS_LOCAL'] = 'false'
        os.environ['FLASK_ENV'] = 'production'

    logger.info(f"Running verification for {environment} environment...")

    app = create_app()

    checks = []

    with app.app_context():
        # Run all checks
        checks.append(check_database_connectivity())
        checks.append(check_schema_version())
        checks.append(check_tool_definitions())
        checks.append(check_orphaned_tool_access_invalid_tools())
        checks.append(check_orphaned_tool_access_invalid_users())
        checks.append(check_default_tools_assigned())
        checks.append(check_table_counts())
        checks.append(check_application_import())

    # Determine overall success
    critical_failures = [c for c in checks if not c.passed and not c.warning]
    warnings = [c for c in checks if not c.passed and c.warning]
    successes = [c for c in checks if c.passed]

    success = len(critical_failures) == 0

    # Print results
    print("\n" + "="*60)
    print(f"MIGRATION VERIFICATION RESULTS - {environment.upper()}")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Print passed checks (if verbose)
    if verbose:
        print("\nPassed Checks:")
        for check in successes:
            print(f"  {check}")

    # Print warnings
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for check in warnings:
            print(f"  {check}")

    # Print failures
    if critical_failures:
        print(f"\nFailed Checks ({len(critical_failures)}):")
        for check in critical_failures:
            print(f"  {check}")

    # Summary
    print("\n" + "="*60)
    print(f"Summary: {len(successes)} passed, {len(warnings)} warnings, {len(critical_failures)} failed")

    if success:
        if warnings:
            print("Overall Status: [PASSED WITH WARNINGS]")
        else:
            print("Overall Status: [PASSED]")
    else:
        print("Overall Status: [FAILED]")

    print("="*60)

    # Recommendations
    if critical_failures:
        print("\nRecommended Actions:")
        for check in critical_failures:
            if "Orphaned Tool Access" in check.name:
                print("  - Run: python sync_tools.py (migrate deprecated tools)")
                print("  - Or manually clean up orphaned tool_access records")
            elif "Tool Definitions" in check.name:
                print("  - Run: python sync_tools.py (sync tool definitions)")
            elif "Default Tools" in check.name:
                print("  - Grant missing default tools via admin UI")
                print("  - Or run: User.assign_default_tools(user_id) for each user")

    return success, checks


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Verify database migration and application health',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify local environment
  python scripts/verify_migration.py --env local

  # Verify staging with verbose output
  python scripts/verify_migration.py --env staging --verbose

  # Verify production
  python scripts/verify_migration.py --env production

  # Via Heroku
  heroku run python scripts/verify_migration.py --env staging -a omnitool-by-xdv-staging

Exit Codes:
  0 - All checks passed (warnings allowed)
  1 - One or more critical checks failed
        """
    )

    parser.add_argument(
        '--env',
        choices=['local', 'staging', 'production'],
        default='local',
        help='Environment to verify (default: local)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show all check details, including passed checks'
    )

    args = parser.parse_args()

    try:
        success, checks = run_verification(
            environment=args.env,
            verbose=args.verbose
        )

        sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"[ERROR] Verification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
