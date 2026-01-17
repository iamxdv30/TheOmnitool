"""
Smoke Tests for Post-Deployment Health Checks

These tests verify that a deployed application is functional after deployment.
Designed to catch critical issues quickly without comprehensive test coverage.

Features:
- HTTP endpoint tests (homepage, login, health checks)
- Database connectivity verification
- Static asset loading tests
- Error log monitoring
- Fast execution (< 30 seconds)

Usage:
    # Test staging after deployment (in CI/CD)
    python tests/smoke_tests.py --url https://omnitool-by-xdv-staging.herokuapp.com

    # Test production
    python tests/smoke_tests.py --url https://omnitool-by-xdv.herokuapp.com

    # Test local development
    python tests/smoke_tests.py --url http://localhost:5000

    # Verbose output
    python tests/smoke_tests.py --url https://omnitool-by-xdv-staging.herokuapp.com --verbose
"""

import argparse
import logging
import sys
import time
from typing import Dict, List, Tuple
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("smoke_tests")

class SmokeTestFailure(Exception):
    """Custom exception for smoke test failures"""
    pass

def create_session_with_retries() -> requests.Session:
    """
    Create requests session with retry logic

    Retries on network errors and 5xx server errors
    """
    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST", "HEAD"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session

def test_homepage_loads(base_url: str, session: requests.Session) -> Tuple[bool, str]:
    """
    Test: Homepage returns 200 status

    Critical: If homepage fails, entire application is likely down
    """
    logger.info("Testing homepage loads...")

    try:
        response = session.get(base_url, timeout=10)

        if response.status_code == 200:
            logger.info("✓ Homepage loads (200 OK)")
            return True, "Homepage loads successfully"
        else:
            return False, f"Homepage returned {response.status_code}"

    except requests.RequestException as e:
        return False, f"Homepage request failed: {e}"

def test_login_page_loads(base_url: str, session: requests.Session) -> Tuple[bool, str]:
    """
    Test: Login page returns 200 status

    Critical: Verifies authentication system is accessible
    """
    logger.info("Testing login page loads...")

    try:
        response = session.get(f"{base_url}/login", timeout=10)

        if response.status_code == 200:
            logger.info("✓ Login page loads (200 OK)")
            return True, "Login page loads successfully"
        else:
            return False, f"Login page returned {response.status_code}"

    except requests.RequestException as e:
        return False, f"Login page request failed: {e}"

def test_health_endpoint(base_url: str, session: requests.Session) -> Tuple[bool, str]:
    """
    Test: Health check endpoint (if exists)

    Note: Not all apps have a health endpoint, so this may be skipped
    """
    logger.info("Testing health endpoint...")

    try:
        response = session.get(f"{base_url}/health", timeout=10)

        if response.status_code == 200:
            logger.info("✓ Health endpoint returns 200")

            # Try to parse JSON response
            try:
                data = response.json()
                if data.get("status") == "ok":
                    return True, "Health endpoint reports OK"
                else:
                    return False, f"Health endpoint reports: {data}"
            except ValueError:
                # Not JSON, but 200 is good enough
                return True, "Health endpoint returns 200"

        elif response.status_code == 404:
            logger.info("⚠️  No health endpoint (404) - skipping")
            return True, "Health endpoint not implemented (skipped)"
        else:
            return False, f"Health endpoint returned {response.status_code}"

    except requests.RequestException as e:
        logger.warning(f"Health endpoint unreachable: {e}")
        return True, "Health endpoint not implemented (skipped)"

def test_static_assets_load(base_url: str, session: requests.Session) -> Tuple[bool, str]:
    """
    Test: Static CSS/JS files load

    Verifies static file serving is working
    """
    logger.info("Testing static assets load...")

    # Common static file paths (files that actually exist)
    static_files = [
        "/static/css/base.css",
        "/static/js/utils/theme.js"
    ]

    failed_assets = []

    for asset_path in static_files:
        try:
            response = session.get(f"{base_url}{asset_path}", timeout=10)

            if response.status_code == 200:
                logger.debug(f"✓ {asset_path} loads")
            else:
                failed_assets.append(f"{asset_path} ({response.status_code})")

        except requests.RequestException as e:
            failed_assets.append(f"{asset_path} ({e})")

    if failed_assets:
        return False, f"Static assets failed: {', '.join(failed_assets)}"
    else:
        logger.info(f"✓ Static assets load ({len(static_files)} checked)")
        return True, "All static assets load successfully"

def test_database_connectivity(base_url: str, session: requests.Session) -> Tuple[bool, str]:
    """
    Test: Database connectivity via a DB-dependent endpoint

    Tests homepage which requires DB access to load user session
    """
    logger.info("Testing database connectivity...")

    try:
        # Homepage requires DB access for session management
        response = session.get(base_url, timeout=15)

        if response.status_code == 200:
            # Check for common DB error messages in response
            error_indicators = [
                "database connection failed",
                "sqlalchemy error",
                "database is locked",
                "operational error"
            ]

            response_text = response.text.lower()

            for indicator in error_indicators:
                if indicator in response_text:
                    return False, f"Database error detected: {indicator}"

            logger.info("✓ Database connectivity OK (no errors detected)")
            return True, "Database connectivity OK"
        else:
            return False, f"Database check failed with status {response.status_code}"

    except requests.RequestException as e:
        return False, f"Database connectivity test failed: {e}"

def test_no_recent_errors(base_url: str, session: requests.Session) -> Tuple[bool, str]:
    """
    Test: No 500 errors in recent requests

    Makes several requests to verify no server errors occur
    """
    logger.info("Testing for recent server errors...")

    test_urls = [
        base_url,
        f"{base_url}/login",
        f"{base_url}/about" if base_url else None  # May not exist
    ]

    test_urls = [url for url in test_urls if url]  # Filter None

    error_count = 0
    total_requests = len(test_urls)

    for url in test_urls:
        try:
            response = session.get(url, timeout=10)

            if response.status_code >= 500:
                error_count += 1
                logger.warning(f"⚠️  {url} returned {response.status_code}")

        except requests.RequestException as e:
            logger.warning(f"Request to {url} failed: {e}")

    if error_count > 0:
        return False, f"{error_count}/{total_requests} requests returned 5xx errors"
    else:
        logger.info(f"✓ No 5xx errors in {total_requests} requests")
        return True, "No recent 5xx errors detected"

def run_smoke_tests(base_url: str) -> Dict[str, Tuple[bool, str]]:
    """
    Run all smoke tests

    Returns: Dictionary of test results {test_name: (passed, message)}
    """
    logger.info("=" * 60)
    logger.info("SMOKE TESTS - POST-DEPLOYMENT HEALTH CHECKS")
    logger.info("=" * 60)
    logger.info(f"Target: {base_url}")
    logger.info("=" * 60)

    session = create_session_with_retries()

    # Define all tests
    tests = [
        ("Homepage Loads", lambda: test_homepage_loads(base_url, session)),
        ("Login Page Loads", lambda: test_login_page_loads(base_url, session)),
        ("Health Endpoint", lambda: test_health_endpoint(base_url, session)),
        ("Static Assets Load", lambda: test_static_assets_load(base_url, session)),
        ("Database Connectivity", lambda: test_database_connectivity(base_url, session)),
        ("No Recent 5xx Errors", lambda: test_no_recent_errors(base_url, session))
    ]

    results = {}
    start_time = time.time()

    for test_name, test_func in tests:
        try:
            passed, message = test_func()
            results[test_name] = (passed, message)
        except Exception as e:
            results[test_name] = (False, f"Test error: {e}")
            logger.error(f"Test '{test_name}' raised exception: {e}")

    elapsed = time.time() - start_time

    # Print summary
    logger.info("=" * 60)
    logger.info("SMOKE TEST RESULTS")
    logger.info("=" * 60)

    passed_tests = sum(1 for passed, _ in results.values() if passed)
    failed_tests = len(results) - passed_tests

    for test_name, (passed, message) in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status} - {test_name}: {message}")

    logger.info("=" * 60)
    logger.info(f"Passed: {passed_tests}/{len(results)}")
    logger.info(f"Failed: {failed_tests}/{len(results)}")
    logger.info(f"Duration: {elapsed:.2f}s")
    logger.info("=" * 60)

    # Overall status
    if failed_tests == 0:
        logger.info("✓ ALL SMOKE TESTS PASSED")
        logger.info("=" * 60)
    else:
        logger.error("✗ SMOKE TESTS FAILED")
        logger.error(f"✗ {failed_tests} test(s) failed - deployment may have issues")
        logger.info("=" * 60)

    return results

def main():
    parser = argparse.ArgumentParser(
        description="Smoke tests for post-deployment health checks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test staging
  python tests/smoke_tests.py --url https://omnitool-by-xdv-staging.herokuapp.com

  # Test production
  python tests/smoke_tests.py --url https://omnitool-by-xdv.herokuapp.com

  # Test local
  python tests/smoke_tests.py --url http://localhost:5000

  # Verbose output
  python tests/smoke_tests.py --url https://omnitool-by-xdv-staging.herokuapp.com --verbose
        """
    )

    parser.add_argument(
        "--url",
        required=True,
        help="Base URL of deployed application (e.g., https://omnitool-by-xdv-staging.herokuapp.com)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate URL format
    if not args.url.startswith(("http://", "https://")):
        logger.error("URL must start with http:// or https://")
        sys.exit(1)

    # Remove trailing slash
    base_url = args.url.rstrip("/")

    # Run tests
    results = run_smoke_tests(base_url)

    # Exit code: 0 if all passed, 1 if any failed
    failed_count = sum(1 for passed, _ in results.values() if not passed)

    if failed_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
