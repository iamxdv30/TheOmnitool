"""
Admin API Endpoints

Handles the admin/superadmin control panel JSON API consumed by the Next.js
(admin) route group:
- GET    /api/v1/admin/users                    - List/search/paginate users
- POST   /api/v1/admin/users                    - Create a user
- PUT    /api/v1/admin/users/:id                - Update a user's profile
- DELETE /api/v1/admin/users/:id                - Delete a user
- POST   /api/v1/admin/change-role/:id          - Change a user's role (SuperAdmin only)
- POST   /api/v1/admin/grant-tool-access        - Grant tool access to a user
- POST   /api/v1/admin/revoke-tool-access       - Revoke tool access from a user
- GET    /api/v1/admin/tools                    - List the tool catalog
- POST   /api/v1/admin/tools                    - Create a tool (SuperAdmin only)
- PUT    /api/v1/admin/tools/:id                - Update a tool (SuperAdmin only)
- DELETE /api/v1/admin/tools/:id                - Delete a tool (SuperAdmin only)

All routes require an authenticated admin or superadmin session; the
superadmin-only routes are additionally gated with require_role('super_admin').
"""

from flask import Blueprint, session, request
import logging

from . import api_response, api_error, get_json_body, require_auth, require_role
from services import get_admin_service

logger = logging.getLogger(__name__)

admin_api_bp = Blueprint('admin_api', __name__, url_prefix='/admin')


def _result_response(result, status_code=200):
    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )
    return api_response(result.data, status_code=status_code)


@admin_api_bp.route('/users', methods=['GET'])
@require_auth
@require_role('admin', 'super_admin')
def list_users():
    """
    List/search/paginate users.

    Query Parameters:
        page: int (default 1)
        per_page: int (default 10)
        search: string (optional, matches username/email/first/last name)
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
    except ValueError:
        return api_error("VALIDATION_ERROR", "page and per_page must be integers.", status_code=400)

    search = request.args.get('search', '').strip() or None

    result = get_admin_service().list_users(page=page, per_page=per_page, search=search)
    return _result_response(result)


@admin_api_bp.route('/users', methods=['POST'])
@require_auth
@require_role('admin', 'super_admin')
def create_user():
    """
    Create a new user.

    Request Body:
        {"username", "email", "password", "fname"?, "lname"?, "role": "user"|"admin"}
    """
    data, error = get_json_body()
    if error:
        return error

    result = get_admin_service().create_user(session.get('role'), data)
    return _result_response(result, status_code=201)


@admin_api_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_auth
@require_role('admin', 'super_admin')
def update_user(user_id):
    """
    Update a user's profile fields (role changes go through /change-role/:id).

    Request Body:
        {"fname"?, "lname"?, "address"?, "city"?, "state"?, "zip"?, "password"?}
    """
    data, error = get_json_body()
    if error:
        return error

    result = get_admin_service().update_user(session.get('role'), user_id, data)
    return _result_response(result)


@admin_api_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_auth
@require_role('admin', 'super_admin')
def delete_user(user_id):
    """Delete a user."""
    result = get_admin_service().delete_user(session.get('role'), user_id)
    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )
    return '', 204


@admin_api_bp.route('/change-role/<int:user_id>', methods=['POST'])
@require_auth
@require_role('super_admin')
def change_role(user_id):
    """
    Change a user's role. SuperAdmin only.

    Request Body:
        {"role": "user"|"admin"|"superadmin"}
    """
    data, error = get_json_body()
    if error:
        return error

    new_role = data.get('role')
    if not new_role:
        return api_error("VALIDATION_ERROR", "role is required.", status_code=400)

    result = get_admin_service().change_role(user_id, new_role)
    return _result_response(result)


@admin_api_bp.route('/grant-tool-access', methods=['POST'])
@require_auth
@require_role('admin', 'super_admin')
def grant_tool_access():
    """
    Grant a user access to a tool.

    Request Body:
        {"user_id": int, "tool_name": "string"}
    """
    data, error = get_json_body()
    if error:
        return error

    user_id = data.get('user_id')
    tool_name = (data.get('tool_name') or '').strip()
    if not user_id or not tool_name:
        return api_error("VALIDATION_ERROR", "user_id and tool_name are required.", status_code=400)

    result = get_admin_service().grant_tool_access(session.get('role'), user_id, tool_name)
    return _result_response(result)


@admin_api_bp.route('/revoke-tool-access', methods=['POST'])
@require_auth
@require_role('admin', 'super_admin')
def revoke_tool_access():
    """
    Revoke a user's access to a tool.

    Request Body:
        {"user_id": int, "tool_name": "string"}
    """
    data, error = get_json_body()
    if error:
        return error

    user_id = data.get('user_id')
    tool_name = (data.get('tool_name') or '').strip()
    if not user_id or not tool_name:
        return api_error("VALIDATION_ERROR", "user_id and tool_name are required.", status_code=400)

    result = get_admin_service().revoke_tool_access(session.get('role'), user_id, tool_name)
    return _result_response(result)


# ==================== Tool catalog (SuperAdmin only for writes) ====================

@admin_api_bp.route('/tools', methods=['GET'])
@require_auth
@require_role('admin', 'super_admin')
def list_tools():
    """List the full tool catalog (used by ToolAccessDialog and Manage Tools)."""
    result = get_admin_service().list_tools()
    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )
    return api_response({"tools": result.data})


@admin_api_bp.route('/tools', methods=['POST'])
@require_auth
@require_role('super_admin')
def create_tool():
    """
    Create a tool.

    Request Body:
        {"name", "display_name", "description", "route", "is_default"}
    """
    data, error = get_json_body()
    if error:
        return error

    result = get_admin_service().create_tool(data)
    return _result_response(result, status_code=201)


@admin_api_bp.route('/tools/<int:tool_id>', methods=['PUT'])
@require_auth
@require_role('super_admin')
def update_tool(tool_id):
    """
    Update a tool.

    Request Body:
        {"display_name"?, "description"?, "route"?, "is_default"?}
    """
    data, error = get_json_body()
    if error:
        return error

    result = get_admin_service().update_tool(tool_id, data)
    return _result_response(result)


@admin_api_bp.route('/tools/<int:tool_id>', methods=['DELETE'])
@require_auth
@require_role('super_admin')
def delete_tool(tool_id):
    """Delete a tool. Also revokes any existing grants for it."""
    result = get_admin_service().delete_tool(tool_id)
    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )
    return '', 204
