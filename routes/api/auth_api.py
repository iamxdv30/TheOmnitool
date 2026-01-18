"""
Authentication API Endpoints

Handles all authentication-related JSON API endpoints:
- POST /api/v1/auth/login
- POST /api/v1/auth/logout
- POST /api/v1/auth/register
- GET  /api/v1/auth/status
- GET  /api/v1/auth/csrf
- POST /api/v1/auth/forgot-password
- POST /api/v1/auth/reset-password
- POST /api/v1/auth/resend-verification
"""

from flask import Blueprint, session, request
import logging

from . import api_response, api_error, get_json_body, require_auth
from services import get_auth_service

logger = logging.getLogger(__name__)

auth_api_bp = Blueprint('auth_api', __name__, url_prefix='/auth')


@auth_api_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and create session.

    Request Body:
        {
            "username": "string",
            "password": "string",
            "recaptcha_token": "string" (optional if disabled)
        }

    Returns:
        200: {"success": true, "data": {"user": UserProfile, "redirect_route": "..."}}
        400: Validation error
        401: Invalid credentials
        403: Email not verified (AUTH_UNVERIFIED)
    """
    data, error = get_json_body()
    if error:
        return error

    username = data.get('username', '').strip()
    password = data.get('password', '')
    recaptcha_token = data.get('recaptcha_token')

    auth_service = get_auth_service()
    result = auth_service.login(
        username=username,
        password=password,
        recaptcha_response=recaptcha_token,
        client_ip=request.remote_addr
    )

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status,
            details=result.error.details
        )

    # Set session data
    login_result = result.data
    user = login_result.user

    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    session['email'] = user.email
    session.permanent = False  # Expire on browser close

    logger.info(f"API Login successful for user: {user.username}")

    return api_response({
        "user": user.to_dict(),
        "redirect_route": login_result.redirect_route
    })


@auth_api_bp.route('/logout', methods=['POST'])
def logout():
    """
    End user session.

    Returns:
        200: {"success": true, "data": null}
    """
    username = session.get('username', 'unknown')
    session.clear()
    logger.info(f"API Logout successful for user: {username}")
    return api_response(None)


@auth_api_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user account.

    Request Body:
        {
            "name": "string",
            "username": "string",
            "email": "string",
            "password": "string",
            "confirm_password": "string",
            "recaptcha_token": "string" (optional if disabled)
        }

    Returns:
        201: {"success": true, "data": RegistrationResult}
        400: Validation error
        409: Username/email already exists
    """
    data, error = get_json_body()
    if error:
        return error

    name = data.get('name', '').strip()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    recaptcha_token = data.get('recaptcha_token')

    auth_service = get_auth_service()
    result = auth_service.register(
        name=name,
        username=username,
        email=email,
        password=password,
        confirm_password=confirm_password,
        recaptcha_response=recaptcha_token,
        client_ip=request.remote_addr
    )

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status,
            details=result.error.details
        )

    logger.info(f"API Registration successful for user: {username}")
    return api_response(result.data.to_dict(), status_code=201)


@auth_api_bp.route('/status', methods=['GET'])
def auth_status():
    """
    Get current authentication status.

    Returns:
        200: {
            "success": true,
            "data": {
                "isAuthenticated": boolean,
                "user": UserProfile | null
            }
        }
    """
    user_id = session.get('user_id')

    if not user_id:
        return api_response({
            "isAuthenticated": False,
            "user": None
        })

    auth_service = get_auth_service()
    result = auth_service.get_user_by_id(user_id)

    if result.is_failure:
        # User not found - clear invalid session
        session.clear()
        return api_response({
            "isAuthenticated": False,
            "user": None
        })

    return api_response({
        "isAuthenticated": True,
        "user": result.data.to_dict()
    })


@auth_api_bp.route('/csrf', methods=['GET'])
def get_csrf_token():
    """
    Get CSRF token for form submissions.

    The token is stored in the session and should be included
    in the X-CSRFToken header for all mutating requests.

    Returns:
        200: {"success": true, "data": {"csrfToken": "string"}}
    """
    import secrets

    # Generate token if not exists
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)

    return api_response({
        "csrfToken": session['csrf_token']
    })


@auth_api_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Request password reset email.

    For security, always returns success even if email doesn't exist.

    Request Body:
        {
            "email": "string",
            "recaptcha_token": "string" (optional if disabled)
        }

    Returns:
        200: {"success": true, "data": {"message": "..."}}
    """
    data, error = get_json_body()
    if error:
        return error

    email = data.get('email', '').strip().lower()

    if not email:
        return api_error(
            "VALIDATION_ERROR",
            "Email address is required.",
            status_code=400
        )

    auth_service = get_auth_service()
    auth_service.request_password_reset(email)

    # Always return success for security
    return api_response({
        "message": "If an account with that email exists, a password reset link has been sent."
    })


@auth_api_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset password using token from email.

    Request Body:
        {
            "token": "string",
            "new_password": "string",
            "confirm_password": "string"
        }

    Returns:
        200: {"success": true, "data": {"message": "..."}}
        400: Token invalid/expired or validation error
    """
    data, error = get_json_body()
    if error:
        return error

    token = data.get('token', '').strip()
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    if not token:
        return api_error(
            "VALIDATION_ERROR",
            "Reset token is required.",
            status_code=400
        )

    auth_service = get_auth_service()
    result = auth_service.reset_password(
        token=token,
        new_password=new_password,
        confirm_password=confirm_password
    )

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status,
            details=result.error.details
        )

    logger.info("API Password reset successful")
    return api_response({
        "message": "Your password has been reset successfully. You can now log in."
    })


@auth_api_bp.route('/validate-reset-token', methods=['POST'])
def validate_reset_token():
    """
    Validate a password reset token without using it.

    Request Body:
        {
            "token": "string"
        }

    Returns:
        200: {"success": true, "data": {"valid": true, "email": "..."}}
        400: Token invalid or expired
    """
    data, error = get_json_body()
    if error:
        return error

    token = data.get('token', '').strip()

    if not token:
        return api_error(
            "VALIDATION_ERROR",
            "Token is required.",
            status_code=400
        )

    auth_service = get_auth_service()
    result = auth_service.validate_reset_token(token)

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    # Mask email for privacy
    email = result.data
    masked_email = email[0] + '***' + email[email.index('@'):]

    return api_response({
        "valid": True,
        "email": masked_email
    })


@auth_api_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """
    Resend email verification link.

    Request Body:
        {
            "email": "string",
            "recaptcha_token": "string" (optional if disabled)
        }

    Returns:
        200: {"success": true, "data": {"message": "..."}}
        400: Validation error
        404: User not found
    """
    data, error = get_json_body()
    if error:
        return error

    email = data.get('email', '').strip().lower()

    if not email:
        return api_error(
            "VALIDATION_ERROR",
            "Email address is required.",
            status_code=400
        )

    auth_service = get_auth_service()
    result = auth_service.resend_verification_email(email)

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    logger.info(f"API Verification email resent to: {email}")
    return api_response({
        "message": "Verification email has been sent. Please check your inbox."
    })
