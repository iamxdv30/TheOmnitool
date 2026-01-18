"""
API Blueprint Package

This package contains all JSON API endpoints for the Next.js frontend integration.
All endpoints follow the standard response envelope format:

Success:
    {"success": true, "data": {...}}

Error:
    {"success": false, "error": {"code": "ERROR_CODE", "message": "..."}}

API Version: v1
Base URL: /api/v1
"""

from flask import Blueprint, jsonify, request
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Create the main API blueprint with /api/v1 prefix
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


def api_response(data=None, status_code=200):
    """
    Create a standardized API success response.

    Args:
        data: Response data (dict, list, or object with to_dict method)
        status_code: HTTP status code (default 200)

    Returns:
        Flask JSON response
    """
    response = {"success": True}

    if data is not None:
        if hasattr(data, 'to_dict'):
            response["data"] = data.to_dict()
        elif isinstance(data, list):
            response["data"] = [
                item.to_dict() if hasattr(item, 'to_dict') else item
                for item in data
            ]
        else:
            response["data"] = data
    else:
        response["data"] = None

    return jsonify(response), status_code


def api_error(code, message, status_code=400, details=None):
    """
    Create a standardized API error response.

    Args:
        code: Error code string (e.g., "VALIDATION_ERROR")
        message: Human-readable error message
        status_code: HTTP status code
        details: Optional additional error details

    Returns:
        Flask JSON response
    """
    error = {
        "code": code,
        "message": message
    }
    if details:
        error["details"] = details

    response = {
        "success": False,
        "error": error
    }

    return jsonify(response), status_code


def require_auth(f):
    """
    Decorator to require authentication for API endpoints.
    Returns 401 if no valid session exists.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session

        if 'user_id' not in session:
            logger.warning(f"Unauthorized API access attempt: {request.path}")
            return api_error(
                "AUTH_REQUIRED",
                "Authentication required. Please log in.",
                status_code=401
            )

        return f(*args, **kwargs)
    return decorated_function


def require_verified(f):
    """
    Decorator to require email verification for API endpoints.
    Returns 403 AUTH_UNVERIFIED if email is not verified.
    Must be used after require_auth.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        from services import get_auth_service
        from model import User

        user_id = session.get('user_id')
        if not user_id:
            return api_error(
                "AUTH_REQUIRED",
                "Authentication required. Please log in.",
                status_code=401
            )

        user = User.query.get(user_id)
        if not user:
            return api_error(
                "AUTH_REQUIRED",
                "User not found. Please log in again.",
                status_code=401
            )

        auth_service = get_auth_service()
        if not auth_service.check_email_verified(user):
            return api_error(
                "AUTH_UNVERIFIED",
                "Email verification required.",
                status_code=403,
                details={"email": user.email}
            )

        return f(*args, **kwargs)
    return decorated_function


def require_role(*roles):
    """
    Decorator to require specific role(s) for API endpoints.
    Returns 403 if user doesn't have required role.
    Must be used after require_auth.

    Usage:
        @require_role('admin', 'super_admin')
        def admin_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import session

            user_role = session.get('role')
            if user_role not in roles:
                logger.warning(
                    f"Permission denied: user role '{user_role}' "
                    f"attempted to access {request.path} (requires {roles})"
                )
                return api_error(
                    "PERMISSION_DENIED",
                    "You don't have permission to access this resource.",
                    status_code=403
                )

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_json_body():
    """
    Get JSON body from request with error handling.

    Returns:
        Tuple of (data, error_response)
        - If successful: (dict, None)
        - If error: (None, Flask response)
    """
    if not request.is_json:
        return None, api_error(
            "VALIDATION_ERROR",
            "Request must be JSON (Content-Type: application/json)",
            status_code=400
        )

    try:
        data = request.get_json()
        if data is None:
            return None, api_error(
                "VALIDATION_ERROR",
                "Invalid or empty JSON body",
                status_code=400
            )
        return data, None
    except Exception as e:
        logger.error(f"JSON parsing error: {e}")
        return None, api_error(
            "VALIDATION_ERROR",
            "Invalid JSON format",
            status_code=400
        )


def validate_with_schema(schema_class, data):
    """
    Validate request data using a marshmallow schema.

    Args:
        schema_class: Marshmallow schema class
        data: Dictionary of request data

    Returns:
        Tuple of (validated_data, error_response)
        - If valid: (dict, None)
        - If invalid: (None, Flask error response)
    """
    from .schemas import validate_request

    validated, errors = validate_request(schema_class, data)

    if errors:
        # Format errors into a user-friendly message
        error_messages = []
        for field, messages in errors.items():
            if isinstance(messages, list):
                error_messages.extend([f"{field}: {msg}" for msg in messages])
            else:
                error_messages.append(f"{field}: {messages}")

        return None, api_error(
            "VALIDATION_ERROR",
            error_messages[0] if len(error_messages) == 1 else "Validation failed.",
            status_code=400,
            details={"errors": errors}
        )

    return validated, None


def get_validated_json(schema_class):
    """
    Get and validate JSON body from request in one step.

    Args:
        schema_class: Marshmallow schema class for validation

    Returns:
        Tuple of (validated_data, error_response)
        - If successful: (dict, None)
        - If error: (None, Flask error response)
    """
    data, error = get_json_body()
    if error:
        return None, error

    return validate_with_schema(schema_class, data)


# Import and register sub-blueprints after defining utilities
# This avoids circular imports
_routes_registered = False


def register_api_routes():
    """Register all API sub-routes. Called after blueprint creation."""
    global _routes_registered

    # Prevent re-registration in test environments
    if _routes_registered:
        return

    from .auth_api import auth_api_bp
    from .user_api import user_api_bp
    from .tool_api import tool_api_bp

    api_bp.register_blueprint(auth_api_bp)
    api_bp.register_blueprint(user_api_bp)
    api_bp.register_blueprint(tool_api_bp)

    _routes_registered = True
    logger.info("API routes registered: /api/v1/auth, /api/v1/user, /api/v1/tools")


# Health check endpoint for the API
@api_bp.route('/health', methods=['GET'])
def api_health():
    """API health check endpoint."""
    return api_response({"status": "healthy", "version": "v1"})
