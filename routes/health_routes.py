"""
Health Check Routes
Provides endpoints for monitoring application and database health
"""
from flask import Blueprint, jsonify, current_app
from utils.db_safety import DatabaseSafety
import logging

health = Blueprint('health', __name__)
logger = logging.getLogger(__name__)


@health.route('/health', methods=['GET'])
def health_check():
    """
    Comprehensive health check endpoint
    Returns database status and application health

    Used by:
    - Monitoring systems
    - Load balancers
    - CI/CD pipelines (smoke tests)
    - Developers for diagnostics
    """
    try:
        # Get database health status
        db_health = DatabaseSafety.get_health_status()

        # Determine HTTP status code
        if db_health['overall_health'] == 'healthy':
            status_code = 200
        elif db_health['overall_health'] == 'degraded':
            status_code = 200  # Still operational, just no users yet
        else:
            status_code = 503  # Service unavailable

        # Build response
        response = {
            'status': db_health['overall_health'],
            'database': {
                'exists': db_health['database_exists'],
                'schema_valid': db_health['schema_valid'],
                'missing_tables': db_health.get('missing_tables', []),
                'table_counts': db_health.get('table_counts', {})
            },
            'checks': {
                'database_exists': '✓' if db_health['database_exists'] else '✗',
                'schema_valid': '✓' if db_health['schema_valid'] else '✗',
                'has_users': '✓' if db_health.get('has_users') else '✗',
                'has_tools': '✓' if db_health.get('has_tools') else '✗'
            },
            'message': get_health_message(db_health)
        }

        logger.info(f"Health check: {db_health['overall_health']}")
        return jsonify(response), status_code

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Health check failed: {str(e)}',
            'database': {'error': str(e)}
        }), 500


@health.route('/health/ping', methods=['GET'])
def ping():
    """
    Simple ping endpoint for basic uptime monitoring
    Returns 200 if application is running
    """
    return jsonify({'status': 'ok', 'message': 'pong'}), 200


@health.route('/health/database', methods=['GET'])
def database_health():
    """
    Detailed database health check
    Returns comprehensive database statistics
    """
    try:
        db_health = DatabaseSafety.get_health_status()

        return jsonify({
            'overall_health': db_health['overall_health'],
            'database_exists': db_health['database_exists'],
            'schema_valid': db_health['schema_valid'],
            'missing_tables': db_health.get('missing_tables', []),
            'table_counts': db_health.get('table_counts', {}),
            'has_users': db_health.get('has_users', False),
            'has_tools': db_health.get('has_tools', False)
        }), 200

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return jsonify({'error': str(e)}), 500


def get_health_message(health_status):
    """Generate human-readable health message"""
    if health_status['overall_health'] == 'healthy':
        return "All systems operational"

    if health_status['overall_health'] == 'degraded':
        if not health_status.get('has_users'):
            return "Database initialized, awaiting first user registration"
        return "System operational with minor issues"

    if not health_status.get('database_exists'):
        return "Database file does not exist - run migrate_db.py"

    if not health_status.get('schema_valid'):
        missing = ', '.join(health_status.get('missing_tables', []))
        return f"Database schema invalid - missing tables: {missing}"

    return "Database health check failed"
