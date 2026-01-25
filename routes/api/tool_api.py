"""
Tool API Endpoints

Handles tool-related JSON API endpoints:
- GET    /api/v1/tools/                  - List all tools
- POST   /api/v1/tools/tax-calculator    - Execute tax calculation
- POST   /api/v1/tools/character-counter - Execute character counting
- GET    /api/v1/tools/email-templates   - List email templates
- POST   /api/v1/tools/email-templates   - Create email template
- PUT    /api/v1/tools/email-templates/:id  - Update email template
- DELETE /api/v1/tools/email-templates/:id  - Delete email template
"""

from flask import Blueprint, session
import logging

from . import (
    api_response, api_error, get_json_body,
    require_auth, require_verified
)
from services import get_tool_service

logger = logging.getLogger(__name__)

tool_api_bp = Blueprint('tool_api', __name__, url_prefix='/tools')


def check_tool_access(tool_name):
    """
    Helper to check if current user has access to a tool.

    Returns:
        Tuple of (has_access: bool, error_response or None)
    """
    user_id = session.get('user_id')
    user_role = session.get('role')

    tool_service = get_tool_service()
    result = tool_service.check_tool_access(user_id, tool_name, user_role)

    if result.is_failure:
        return False, api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    if not result.data:
        return False, api_error(
            "PERMISSION_DENIED",
            f"You don't have access to {tool_name}.",
            status_code=403
        )

    return True, None


@tool_api_bp.route('/', methods=['GET'])
@require_auth
def list_tools():
    """
    List all available tools with access flags.

    Query Parameters:
        include_inactive: boolean (default false)

    Returns:
        200: {
            "success": true,
            "data": {
                "tools": [
                    {
                        "id": int,
                        "name": "string",
                        "description": "string",
                        "hasAccess": boolean
                    },
                    ...
                ]
            }
        }
        401: Not authenticated
    """
    from flask import request

    user_id = session.get('user_id')
    user_role = session.get('role')
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

    tool_service = get_tool_service()

    # Get all tools
    tools_result = tool_service.get_all_tools(include_inactive=include_inactive)
    if tools_result.is_failure:
        return api_error(
            tools_result.error.code.value,
            tools_result.error.message,
            status_code=tools_result.error.http_status
        )

    # Get user's accessible tools
    user_tools_result = tool_service.get_user_tools(user_id)
    user_tools = user_tools_result.data if user_tools_result.is_success else []

    # Build response with access flags
    tools_with_access = []
    for tool in tools_result.data:
        # Admins have access to all tools
        has_access = (
            user_role in ['admin', 'super_admin', 'superadmin'] or
            tool.name in user_tools
        )

        tools_with_access.append({
            "id": tool.id,
            "name": tool.name,
            "description": tool.description,
            "route": tool.route,
            "is_default": tool.is_default,
            "hasAccess": has_access
        })

    return api_response({"tools": tools_with_access})


@tool_api_bp.route('/tax-calculator', methods=['POST'])
@require_auth
@require_verified
def calculate_tax():
    """
    Execute tax calculation.

    Request Body:
        {
            "calculator_type": "us" | "canada" | "vat",
            "items": [{"price": float, "tax_rate": float}, ...],
            "discounts": [{"amount": float, "type": "fixed" | "percentage"}, ...],
            "shipping_cost": float,
            "shipping_taxable": boolean,
            "shipping_tax_rate": float,
            "gst_rate": float,  // Canada only
            "pst_rate": float,  // Canada only
            "vat_rate": float,  // VAT only
            "options": {
                "is_sales_before_tax": boolean,
                "discount_is_taxable": boolean
            }
        }

    Returns:
        200: {"success": true, "data": {calculation results}}
        400: Validation error
        401: Not authenticated
        403: No tool access or email not verified
    """
    # Check tool access - covers multiple tax calculator names
    tool_names = ["Tax Calculator", "Unified Tax Calculator", "Canada Tax Calculator"]
    has_access = False

    for tool_name in tool_names:
        access, error = check_tool_access(tool_name)
        if access:
            has_access = True
            break

    if not has_access:
        return api_error(
            "PERMISSION_DENIED",
            "You don't have access to the Tax Calculator.",
            status_code=403
        )

    data, error = get_json_body()
    if error:
        return error

    calculator_type = data.get('calculator_type', 'us').lower()
    if calculator_type not in ['us', 'canada', 'vat']:
        return api_error(
            "VALIDATION_ERROR",
            "Invalid calculator_type. Must be 'us', 'canada', or 'vat'.",
            status_code=400
        )

    tool_service = get_tool_service()
    result = tool_service.calculate_tax(calculator_type, data)

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    logger.info(f"API Tax calculation completed for user: {session.get('username')}")
    return api_response(result.data)


@tool_api_bp.route('/character-counter', methods=['POST'])
@require_auth
@require_verified
def count_characters():
    """
    Count characters in text.

    Request Body:
        {
            "text": "string",
            "char_limit": int (default 3532)
        }

    Returns:
        200: {
            "success": true,
            "data": {
                "total_characters": int,
                "char_limit": int,
                "excess_characters": int,
                "excess_message": "string"
            }
        }
        400: Validation error
        401: Not authenticated
        403: No tool access or email not verified
    """
    has_access, error = check_tool_access("Character Counter")
    if not has_access:
        return error

    data, error = get_json_body()
    if error:
        return error

    text = data.get('text', '')
    char_limit = data.get('char_limit', 3532)

    try:
        char_limit = int(char_limit)
        if char_limit < 0:
            raise ValueError("char_limit must be positive")
    except (ValueError, TypeError):
        return api_error(
            "VALIDATION_ERROR",
            "char_limit must be a positive integer.",
            status_code=400
        )

    tool_service = get_tool_service()
    result = tool_service.count_characters(text, char_limit)

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    logger.info(f"API Character count completed for user: {session.get('username')}")
    return api_response(result.data.to_dict())


# ==================== Email Templates CRUD ====================

@tool_api_bp.route('/email-templates', methods=['GET'])
@require_auth
@require_verified
def list_email_templates():
    """
    List current user's email templates.

    Returns:
        200: {
            "success": true,
            "data": {
                "templates": [EmailTemplateData, ...]
            }
        }
        401: Not authenticated
        403: No tool access or email not verified
    """
    has_access, error = check_tool_access("email-templates")
    if not has_access:
        return error

    user_id = session.get('user_id')

    tool_service = get_tool_service()
    result = tool_service.get_user_email_templates(user_id)

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    templates = [t.to_dict() for t in result.data]
    return api_response({"templates": templates})


@tool_api_bp.route('/email-templates', methods=['POST'])
@require_auth
@require_verified
def create_email_template():
    """
    Create a new email template.

    Request Body:
        {
            "title": "string",
            "content": "string"
        }

    Returns:
        201: {"success": true, "data": EmailTemplateData}
        400: Validation error
        401: Not authenticated
        403: No tool access or email not verified
    """
    has_access, error = check_tool_access("email-templates")
    if not has_access:
        return error

    data, error = get_json_body()
    if error:
        return error

    user_id = session.get('user_id')
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()

    tool_service = get_tool_service()
    result = tool_service.create_email_template(user_id, title, content)

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    logger.info(f"API Email template created for user: {session.get('username')}")
    return api_response(result.data.to_dict(), status_code=201)


@tool_api_bp.route('/email-templates/<int:template_id>', methods=['PUT'])
@require_auth
@require_verified
def update_email_template(template_id):
    """
    Update an email template.

    Path Parameters:
        template_id: int

    Request Body:
        {
            "title": "string",
            "content": "string"
        }

    Returns:
        200: {"success": true, "data": EmailTemplateData}
        400: Validation error
        401: Not authenticated
        403: No tool access, email not verified, or not template owner
        404: Template not found
    """
    has_access, error = check_tool_access("email-templates")
    if not has_access:
        return error

    data, error = get_json_body()
    if error:
        return error

    user_id = session.get('user_id')
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()

    tool_service = get_tool_service()
    result = tool_service.update_email_template(template_id, user_id, title, content)

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    logger.info(f"API Email template {template_id} updated for user: {session.get('username')}")
    return api_response(result.data.to_dict())


@tool_api_bp.route('/email-templates/<int:template_id>', methods=['DELETE'])
@require_auth
@require_verified
def delete_email_template(template_id):
    """
    Delete an email template.

    Path Parameters:
        template_id: int

    Returns:
        204: No content (success)
        401: Not authenticated
        403: No tool access, email not verified, or not template owner
        404: Template not found
    """
    has_access, error = check_tool_access("email-templates")
    if not has_access:
        return error

    user_id = session.get('user_id')

    tool_service = get_tool_service()
    result = tool_service.delete_email_template(template_id, user_id)

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    logger.info(f"API Email template {template_id} deleted for user: {session.get('username')}")
    return '', 204
