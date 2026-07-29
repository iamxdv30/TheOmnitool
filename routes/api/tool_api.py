"""
Tool API Endpoints

Handles tool-related JSON API endpoints:
- GET    /api/v1/tools/                  - List all tools
- GET    /api/v1/tools/categories        - List active tool categories
- GET    /api/v1/tools/plans             - List active subscription plans
- POST   /api/v1/tools/tax-calculator    - Execute tax calculation
- POST   /api/v1/tools/character-counter - Execute character counting
- POST   /api/v1/tools/usage             - Log usage for client-side tools
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
from services import get_tool_service, get_subscription_service

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


@tool_api_bp.route('/', methods=['GET'], strict_slashes=False)
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

    # Get user's accessible tool names
    user_tools_result = tool_service.get_user_tools(user_id)
    accessible_names = {
        t.name for t in (user_tools_result.data if user_tools_result.is_success else [])
    }

    is_admin = user_role in ['admin', 'super_admin', 'superadmin']

    # Resolve the user's subscription tier once for paid-tool gating
    user_tier = None if is_admin else get_subscription_service().get_active_tier(user_id)

    # Build response with access flags
    tools_with_access = []
    for tool in tools_result.data:
        has_access = is_admin or tool.name in accessible_names

        # Paid tools are also unlocked by a sufficient subscription tier
        if not has_access and tool.is_paid and tool.required_plan_tier is not None:
            has_access = user_tier is not None and user_tier >= tool.required_plan_tier

        tool_dict = tool.to_dict()
        tool_dict["hasAccess"] = has_access
        tools_with_access.append(tool_dict)

    return api_response({"tools": tools_with_access})


@tool_api_bp.route('/categories', methods=['GET'])
@require_auth
def list_categories():
    """
    List all active tool categories for filter pills.

    Returns:
        200: {"success": true, "data": {"categories": [{"id", "name", "slug", "icon", "color", "display_order"}, ...]}}
        401: Not authenticated
    """
    tool_service = get_tool_service()
    result = tool_service.get_categories()

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    return api_response({"categories": result.data})


@tool_api_bp.route('/plans', methods=['GET'])
@require_auth
def list_plans():
    """
    List all active subscription plans.

    Returns:
        200: {"success": true, "data": {"plans": [{"id", "name", "slug", "tier_level", "price_monthly", "price_yearly", "features"}, ...]}}
        401: Not authenticated
    """
    subscription_service = get_subscription_service()
    result = subscription_service.get_plans()

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    return api_response({"plans": result.data})


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
    # Check tool access - use the actual tool name from DB (title case)
    has_access, error = check_tool_access("Tax Calculator")

    if not has_access:
        return error

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

    tool_service.log_usage(session.get('user_id'), "Tax Calculator")
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

    tool_service.log_usage(session.get('user_id'), "Character Counter")
    logger.info(f"API Character count completed for user: {session.get('username')}")
    return api_response(result.data.to_dict())


@tool_api_bp.route('/usage', methods=['POST'])
@require_auth
@require_verified
def log_tool_usage():
    """
    Record a usage event for a tool that runs client-side (no server
    endpoint of its own), e.g. the Unix Timestamp Converter.

    Request Body:
        {"tool_name": "string"}  // exact Tool.name

    Returns:
        200: {"success": true, "data": {"logged": bool}}  // false = deduplicated
        400: Validation error
        401: Not authenticated
        403: No tool access or email not verified
        404: Unknown tool
    """
    data, error = get_json_body()
    if error:
        return error

    tool_name = (data.get('tool_name') or '').strip()
    if not tool_name:
        return api_error(
            "VALIDATION_ERROR",
            "tool_name is required.",
            status_code=400
        )

    has_access, error = check_tool_access(tool_name)
    if not has_access:
        return error

    result = get_tool_service().log_usage(session.get('user_id'), tool_name)

    if result.is_failure:
        return api_error(
            result.error.code.value,
            result.error.message,
            status_code=result.error.http_status
        )

    return api_response({"logged": result.data})


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
    has_access, error = check_tool_access("Email Templates")
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

    tool_service.log_usage(user_id, "Email Templates")
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
    has_access, error = check_tool_access("Email Templates")
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
    has_access, error = check_tool_access("Email Templates")
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
    has_access, error = check_tool_access("Email Templates")
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
