"""
Tool Service Module

Handles tool-related business logic:
- Tool access management (grant/revoke)
- Tool execution (tax calculations, character counting)
- Email template CRUD
- Tool listing and availability

This service separates tool business logic from HTTP/route concerns.
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from model import User, Tool, ToolAccess, EmailTemplate, db
from .base import BaseService, ServiceResult, ErrorCode

logger = logging.getLogger(__name__)


@dataclass
class ToolInfo:
    """Information about a tool."""
    id: int
    name: str
    description: Optional[str]
    route: Optional[str]
    is_default: bool
    is_active: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "route": self.route,
            "is_default": self.is_default,
            "is_active": self.is_active,
        }


@dataclass
class EmailTemplateData:
    """Email template data."""
    id: int
    user_id: int
    title: str
    content: str
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class CharacterCountResult:
    """Result of character counting operation."""
    total_characters: int
    char_limit: int
    excess_characters: int
    excess_message: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_characters": self.total_characters,
            "char_limit": self.char_limit,
            "excess_characters": self.excess_characters,
            "excess_message": self.excess_message,
        }


class ToolService(BaseService):
    """
    Service for tool-related operations.

    Handles tool access, tool execution, and email template management.
    """

    # Standard tool URL mappings
    TOOL_ROUTES = {
        "Tax Calculator": "tool.unified_tax_calculator",
        "Unified Tax Calculator": "tool.unified_tax_calculator",
        "Canada Tax Calculator": "tool.unified_tax_calculator",
        "Character Counter": "tool.char_counter",
        "Unix Timestamp Converter": "tool.convert",
        "Email Templates": "tool.email_templates",
    }

    def __init__(self):
        super().__init__()

    # ==================== Tool Access Management ====================

    def get_all_tools(self, include_inactive: bool = False) -> ServiceResult[List[ToolInfo]]:
        """
        Get all tools in the system.

        Args:
            include_inactive: Whether to include inactive tools

        Returns:
            ServiceResult with list of ToolInfo
        """
        try:
            query = Tool.query
            if not include_inactive:
                query = query.filter_by(is_active=True)

            tools = query.all()
            tool_list = [self._tool_to_info(t) for t in tools]
            return ServiceResult.success(tool_list)

        except Exception as e:
            self._log_error("get_all_tools", e)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to retrieve tools."
            )

    def get_user_tools(self, user_id: int) -> ServiceResult[List[str]]:
        """
        Get list of tool names a user has access to.

        Args:
            user_id: The user's ID

        Returns:
            ServiceResult with list of tool names
        """
        try:
            access_list = ToolAccess.query.filter_by(user_id=user_id).all()
            tool_names = [access.tool_name for access in access_list]
            return ServiceResult.success(tool_names)

        except Exception as e:
            self._log_error("get_user_tools", e, user_id=user_id)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to retrieve user tools."
            )

    def check_tool_access(
        self,
        user_id: int,
        tool_name: str,
        user_role: Optional[str] = None
    ) -> ServiceResult[bool]:
        """
        Check if a user has access to a specific tool.

        Admins and super_admins have access to all tools.

        Args:
            user_id: The user's ID
            tool_name: Name of the tool
            user_role: User's role (optional - will be fetched if not provided)

        Returns:
            ServiceResult with True if user has access
        """
        # Admins have access to all tools
        if user_role in ["admin", "super_admin", "superadmin"]:
            return ServiceResult.success(True)

        try:
            has_access = ToolAccess.query.filter_by(
                user_id=user_id,
                tool_name=tool_name
            ).first() is not None

            return ServiceResult.success(has_access)

        except Exception as e:
            self._log_error("check_tool_access", e, user_id=user_id, tool_name=tool_name)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to check tool access."
            )

    def grant_tool_access(
        self,
        user_id: int,
        tool_name: str,
        admin_role: str
    ) -> ServiceResult[bool]:
        """
        Grant tool access to a user.

        Args:
            user_id: ID of user to grant access to
            tool_name: Name of the tool
            admin_role: Role of the admin granting access

        Returns:
            ServiceResult with True on success
        """
        self._log_operation("grant_tool_access", user_id=user_id, tool_name=tool_name)

        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            return ServiceResult.failure(
                ErrorCode.RESOURCE_NOT_FOUND,
                "User not found."
            )

        # Verify tool exists
        tool = Tool.query.filter_by(name=tool_name).first()
        if not tool:
            return ServiceResult.failure(
                ErrorCode.RESOURCE_NOT_FOUND,
                f"Tool '{tool_name}' not found."
            )

        # Check if default tool (only super_admin can grant default tools)
        if tool.is_default and admin_role != "super_admin":
            return ServiceResult.failure(
                ErrorCode.PERMISSION_DENIED,
                "Only super admins can grant access to default tools."
            )

        # Check if already has access
        existing = ToolAccess.query.filter_by(user_id=user_id, tool_name=tool_name).first()
        if existing:
            return ServiceResult.failure(
                ErrorCode.RESOURCE_ALREADY_EXISTS,
                f"User already has access to {tool_name}."
            )

        try:
            new_access = ToolAccess(user_id=user_id, tool_name=tool_name)
            db.session.add(new_access)
            db.session.commit()

            self.logger.info(f"Tool access granted: user_id={user_id}, tool={tool_name}")
            return ServiceResult.success(True)

        except Exception as e:
            db.session.rollback()
            self._log_error("grant_tool_access", e, user_id=user_id, tool_name=tool_name)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to grant tool access."
            )

    def revoke_tool_access(
        self,
        user_id: int,
        tool_name: str
    ) -> ServiceResult[bool]:
        """
        Revoke tool access from a user.

        Args:
            user_id: ID of user to revoke access from
            tool_name: Name of the tool

        Returns:
            ServiceResult with True on success
        """
        self._log_operation("revoke_tool_access", user_id=user_id, tool_name=tool_name)

        try:
            access = ToolAccess.query.filter_by(
                user_id=user_id,
                tool_name=tool_name
            ).first()

            if not access:
                return ServiceResult.failure(
                    ErrorCode.RESOURCE_NOT_FOUND,
                    f"User doesn't have access to {tool_name}."
                )

            db.session.delete(access)
            db.session.commit()

            self.logger.info(f"Tool access revoked: user_id={user_id}, tool={tool_name}")
            return ServiceResult.success(True)

        except Exception as e:
            db.session.rollback()
            self._log_error("revoke_tool_access", e, user_id=user_id, tool_name=tool_name)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to revoke tool access."
            )

    def get_tool_route(self, tool_name: str) -> Optional[str]:
        """
        Get the Flask route for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Flask route string or None if not found
        """
        return self.TOOL_ROUTES.get(tool_name)

    # ==================== Tool Execution ====================

    def count_characters(
        self,
        text: str,
        char_limit: int = 3532
    ) -> ServiceResult[CharacterCountResult]:
        """
        Count characters in text and check against limit.

        Args:
            text: Text to count
            char_limit: Character limit (default 3532)

        Returns:
            ServiceResult with CharacterCountResult
        """
        try:
            # Import the actual counter function
            from Tools.char_counter import count_characters as do_count

            result = do_count(text, char_limit)

            return ServiceResult.success(CharacterCountResult(
                total_characters=result["total_characters"],
                char_limit=char_limit,
                excess_characters=result.get("excess_characters", 0),
                excess_message=result.get("excess_message", ""),
            ))

        except Exception as e:
            self._log_error("count_characters", e)
            return ServiceResult.failure(
                ErrorCode.INTERNAL_ERROR,
                "Failed to count characters."
            )

    def calculate_tax(
        self,
        calculator_type: str,
        data: Dict[str, Any]
    ) -> ServiceResult[Dict[str, Any]]:
        """
        Perform tax calculation.

        Args:
            calculator_type: Type of calculation ("us", "canada", "vat")
            data: Calculation input data

        Returns:
            ServiceResult with calculation result
        """
        try:
            from Tools.tax_calculator import tax_calculator as calculate, calculate_vat

            if calculator_type == "vat":
                vat_data = {
                    "vat_rate": data.get("vat_rate", 0),
                    "items": data.get("items", []),
                    "discounts": data.get("discounts", []),
                    "shipping_cost": data.get("shipping_cost", 0),
                    "shipping_taxable": data.get("shipping_taxable", True),
                    "is_sales_before_tax": data.get("options", {}).get("is_sales_before_tax", False),
                    "discount_is_taxable": data.get("options", {}).get("discount_is_taxable", True)
                }
                result = calculate_vat(vat_data)

            elif calculator_type == "canada":
                gst_rate = data.get("gst_rate", 0)
                pst_rate = data.get("pst_rate", 0)
                total_tax_rate = float(gst_rate) + float(pst_rate)

                sales_tax_data = {
                    "items": [],
                    "discounts": data.get("discounts", []),
                    "shipping_cost": data.get("shipping_cost", 0),
                    "shipping_taxable": data.get("shipping_taxable", False),
                    "shipping_tax_rate": total_tax_rate,
                    "is_sales_before_tax": data.get("options", {}).get("is_sales_before_tax", False),
                    "discount_is_taxable": data.get("options", {}).get("discount_is_taxable", True)
                }

                for item in data.get("items", []):
                    sales_tax_data["items"].append({
                        "price": item.get("price", 0),
                        "tax_rate": total_tax_rate
                    })

                result = calculate(sales_tax_data)

            elif calculator_type == "us":
                sales_tax_data = {
                    "items": [],
                    "discounts": data.get("discounts", []),
                    "shipping_cost": data.get("shipping_cost", 0),
                    "shipping_taxable": data.get("shipping_taxable", False),
                    "shipping_tax_rate": data.get("shipping_tax_rate", 0),
                    "is_sales_before_tax": data.get("options", {}).get("is_sales_before_tax", False),
                    "discount_is_taxable": data.get("options", {}).get("discount_is_taxable", True)
                }

                for item in data.get("items", []):
                    sales_tax_data["items"].append({
                        "price": item.get("price", 0),
                        "tax_rate": item.get("tax_rate", 0)
                    })

                result = calculate(sales_tax_data)

            else:
                return ServiceResult.failure(
                    ErrorCode.VALIDATION_ERROR,
                    f"Invalid calculator type: {calculator_type}"
                )

            return ServiceResult.success(result)

        except ValueError as e:
            self._log_error("calculate_tax", e, calculator_type=calculator_type)
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                str(e)
            )

        except Exception as e:
            self._log_error("calculate_tax", e, calculator_type=calculator_type)
            return ServiceResult.failure(
                ErrorCode.INTERNAL_ERROR,
                "Failed to calculate tax."
            )

    # ==================== Email Templates ====================

    def get_user_email_templates(
        self,
        user_id: int
    ) -> ServiceResult[List[EmailTemplateData]]:
        """
        Get all email templates for a user.

        Args:
            user_id: The user's ID

        Returns:
            ServiceResult with list of EmailTemplateData
        """
        try:
            templates = EmailTemplate.query.filter_by(user_id=user_id).all()
            template_list = [self._template_to_data(t) for t in templates]
            return ServiceResult.success(template_list)

        except Exception as e:
            self._log_error("get_user_email_templates", e, user_id=user_id)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to retrieve email templates."
            )

    def create_email_template(
        self,
        user_id: int,
        title: str,
        content: str
    ) -> ServiceResult[EmailTemplateData]:
        """
        Create a new email template.

        Args:
            user_id: Owner user ID
            title: Template title
            content: Template content

        Returns:
            ServiceResult with created EmailTemplateData
        """
        self._log_operation("create_email_template", user_id=user_id, title=title)

        if not title or not content:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                "Both title and content are required."
            )

        try:
            template = EmailTemplate(
                user_id=user_id,
                title=title,
                content=content
            )
            db.session.add(template)
            db.session.commit()

            self.logger.info(f"Email template created: id={template.id}, user_id={user_id}")
            return ServiceResult.success(self._template_to_data(template))

        except Exception as e:
            db.session.rollback()
            self._log_error("create_email_template", e, user_id=user_id)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to create email template."
            )

    def update_email_template(
        self,
        template_id: int,
        user_id: int,
        title: str,
        content: str
    ) -> ServiceResult[EmailTemplateData]:
        """
        Update an email template.

        Args:
            template_id: Template ID to update
            user_id: User ID (for ownership verification)
            title: New title
            content: New content

        Returns:
            ServiceResult with updated EmailTemplateData
        """
        self._log_operation("update_email_template", template_id=template_id, user_id=user_id)

        if not title or not content:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                "Both title and content are required."
            )

        template = EmailTemplate.query.get(template_id)

        if not template:
            return ServiceResult.failure(
                ErrorCode.RESOURCE_NOT_FOUND,
                "Template not found."
            )

        if template.user_id != user_id:
            return ServiceResult.failure(
                ErrorCode.PERMISSION_DENIED,
                "You don't have permission to modify this template."
            )

        try:
            template.title = title
            template.content = content
            db.session.commit()

            self.logger.info(f"Email template updated: id={template_id}")
            return ServiceResult.success(self._template_to_data(template))

        except Exception as e:
            db.session.rollback()
            self._log_error("update_email_template", e, template_id=template_id)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to update email template."
            )

    def delete_email_template(
        self,
        template_id: int,
        user_id: int
    ) -> ServiceResult[bool]:
        """
        Delete an email template.

        Args:
            template_id: Template ID to delete
            user_id: User ID (for ownership verification)

        Returns:
            ServiceResult with True on success
        """
        self._log_operation("delete_email_template", template_id=template_id, user_id=user_id)

        template = EmailTemplate.query.get(template_id)

        if not template:
            return ServiceResult.failure(
                ErrorCode.RESOURCE_NOT_FOUND,
                "Template not found."
            )

        if template.user_id != user_id:
            return ServiceResult.failure(
                ErrorCode.PERMISSION_DENIED,
                "You don't have permission to delete this template."
            )

        try:
            db.session.delete(template)
            db.session.commit()

            self.logger.info(f"Email template deleted: id={template_id}")
            return ServiceResult.success(True)

        except Exception as e:
            db.session.rollback()
            self._log_error("delete_email_template", e, template_id=template_id)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to delete email template."
            )

    # ==================== Helper Methods ====================

    def _tool_to_info(self, tool: Tool) -> ToolInfo:
        """Convert Tool model to ToolInfo dataclass."""
        return ToolInfo(
            id=tool.id,
            name=tool.name,
            description=getattr(tool, 'description', None),
            route=getattr(tool, 'route', None),
            is_default=getattr(tool, 'is_default', False),
            is_active=getattr(tool, 'is_active', True),
        )

    def _template_to_data(self, template: EmailTemplate) -> EmailTemplateData:
        """Convert EmailTemplate model to EmailTemplateData dataclass."""
        return EmailTemplateData(
            id=template.id,
            user_id=template.user_id,
            title=template.title,
            content=template.content,
            created_at=getattr(template, 'created_at', None),
        )


# Singleton instance
_tool_service: Optional[ToolService] = None


def get_tool_service() -> ToolService:
    """Get the singleton ToolService instance."""
    global _tool_service
    if _tool_service is None:
        _tool_service = ToolService()
    return _tool_service
