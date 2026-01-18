"""
User API Endpoints

Handles user-related JSON API endpoints:
- GET   /api/v1/user/profile
- PATCH /api/v1/user/profile
- PUT   /api/v1/user/password
- GET   /api/v1/user/tools
- GET   /api/v1/user/usage
"""

from flask import Blueprint, session
import logging

from . import (
    api_response, api_error, get_json_body,
    require_auth, require_verified
)
from services import get_user_service, get_tool_service

logger = logging.getLogger(__name__)

user_api_bp = Blueprint('user_api', __name__, url_prefix='/user')


@user_api_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """
    Get current user's profile.

    Returns:
        200: {"success": true, "data": UserProfileData}
        401: Not authenticated
    """
    user_id = session.get('user_id')

    user_service = get_user_service()
    result = user_service.get_user_by_id(user_id)

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    return api_response(result.data.to_dict())


@user_api_bp.route('/profile', methods=['PATCH'])
@require_auth
@require_verified
def update_profile():
    """
    Update current user's profile.

    Request Body (all fields optional):
        {
            "name": "string",
            "fname": "string",
            "lname": "string",
            "address": "string",
            "city": "string",
            "state": "string",
            "zip": "string"
        }

    Returns:
        200: {"success": true, "data": UserProfileData}
        400: Validation error
        401: Not authenticated
        403: Email not verified
    """
    data, error = get_json_body()
    if error:
        return error

    user_id = session.get('user_id')

    # Extract allowed fields
    allowed_fields = ['name', 'fname', 'lname', 'address', 'city', 'state', 'zip']
    update_data = {k: v for k, v in data.items() if k in allowed_fields and v is not None}

    # Map 'zip' to 'zip_code' for service
    if 'zip' in update_data:
        update_data['zip_code'] = update_data.pop('zip')

    if not update_data:
        return api_error(
            "VALIDATION_ERROR",
            "No valid fields to update.",
            status_code=400
        )

    user_service = get_user_service()
    result = user_service.update_profile(user_id, **update_data)

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    logger.info(f"API Profile updated for user ID: {user_id}")
    return api_response(result.data.to_dict())


@user_api_bp.route('/password', methods=['PUT'])
@require_auth
@require_verified
def change_password():
    """
    Change current user's password.

    Request Body:
        {
            "current_password": "string",
            "new_password": "string",
            "confirm_password": "string"
        }

    Returns:
        200: {"success": true, "data": {"message": "..."}}
        400: Validation error
        401: Not authenticated or invalid current password
        403: Email not verified
    """
    data, error = get_json_body()
    if error:
        return error

    user_id = session.get('user_id')

    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    user_service = get_user_service()
    result = user_service.change_password(
        user_id=user_id,
        current_password=current_password,
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

    logger.info(f"API Password changed for user ID: {user_id}")
    return api_response({
        "message": "Password changed successfully."
    })


@user_api_bp.route('/email', methods=['PUT'])
@require_auth
@require_verified
def update_email():
    """
    Update current user's email address.

    Requires current password and will mark email as unverified.

    Request Body:
        {
            "new_email": "string",
            "current_password": "string"
        }

    Returns:
        200: {"success": true, "data": {"message": "...", "requiresVerification": true}}
        400: Validation error
        401: Not authenticated or invalid password
        403: Email not verified
        409: Email already in use
    """
    data, error = get_json_body()
    if error:
        return error

    user_id = session.get('user_id')

    new_email = data.get('new_email', '').strip()
    current_password = data.get('current_password', '')

    user_service = get_user_service()
    result = user_service.update_email(
        user_id=user_id,
        new_email=new_email,
        current_password=current_password
    )

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    # Update session email
    session['email'] = new_email.lower()

    logger.info(f"API Email updated for user ID: {user_id}")
    return api_response({
        "message": "Email updated successfully. Please verify your new email address.",
        "requiresVerification": True
    })


@user_api_bp.route('/tools', methods=['GET'])
@require_auth
def get_user_tools():
    """
    Get list of tools the current user has access to.

    Returns:
        200: {"success": true, "data": {"tools": ["Tool1", "Tool2", ...]}}
        401: Not authenticated
    """
    user_id = session.get('user_id')

    tool_service = get_tool_service()
    result = tool_service.get_user_tools(user_id)

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    return api_response({
        "tools": result.data
    })


@user_api_bp.route('/usage', methods=['GET'])
@require_auth
def get_usage_stats():
    """
    Get current user's tool usage statistics.

    Returns:
        200: {"success": true, "data": {"usage": {"ToolName": count, ...}}}
        401: Not authenticated
    """
    user_id = session.get('user_id')

    user_service = get_user_service()
    result = user_service.get_dashboard_data(user_id)

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    return api_response({
        "usage": result.data.usage_stats or {}
    })


@user_api_bp.route('/dashboard', methods=['GET'])
@require_auth
def get_dashboard():
    """
    Get all dashboard data in a single request.

    Returns:
        200: {
            "success": true,
            "data": {
                "user": UserProfileData,
                "tools": ["Tool1", ...],
                "usage": {"ToolName": count, ...}
            }
        }
        401: Not authenticated
    """
    user_id = session.get('user_id')

    user_service = get_user_service()
    result = user_service.get_dashboard_data(user_id)

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    dashboard = result.data
    return api_response({
        "user": dashboard.user.to_dict(),
        "tools": dashboard.tools,
        "usage": dashboard.usage_stats or {}
    })
