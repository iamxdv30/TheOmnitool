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
from datetime import datetime, timezone

from model import User, Tool, ToolAccess, ToolFavorite, ToolCategory, EmailTemplate, UsageLog, db
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
    display_name: Optional[str] = None
    icon: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    category_slug: Optional[str] = None
    category_color: Optional[str] = None
    category_icon: Optional[str] = None
    is_paid: bool = False
    required_plan_id: Optional[int] = None
    required_plan_name: Optional[str] = None
    required_plan_tier: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        category = None
        if self.category_id is not None:
            category = {
                "id": self.category_id,
                "name": self.category_name,
                "slug": self.category_slug,
                "color": self.category_color,
                "icon": self.category_icon,
            }

        required_plan = None
        if self.required_plan_id is not None:
            required_plan = {
                "id": self.required_plan_id,
                "name": self.required_plan_name,
                "tier_level": self.required_plan_tier,
            }

        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name or self.name.replace('-', ' ').title(),
            "description": self.description,
            "route": self.route,
            "is_default": self.is_default,
            "is_active": self.is_active,
            "icon": self.icon,
            "category": category,
            "is_paid": self.is_paid,
            "required_plan": required_plan,
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

    def get_user_tools(self, user_id: int) -> ServiceResult[List[ToolInfo]]:
        """
        Get list of tools a user has access to.

        Args:
            user_id: The user's ID

        Returns:
            ServiceResult with list of ToolInfo objects
        """
        try:
            # Get tool access records for the user
            access_list = ToolAccess.query.filter_by(user_id=user_id).all()
            tool_names = {access.tool_name for access in access_list}
            
            # Get full tool objects
            active_tools = Tool.query.filter_by(is_active=True).all()
            tools = [
                tool for tool in active_tools
                if tool.is_default or tool.name in tool_names
            ]
            
            tool_list = [self._tool_to_info(tool) for tool in tools]
            return ServiceResult.success(tool_list)

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
            if User.user_has_tool_access(user_id, tool_name):
                return ServiceResult.success(True)

            # Paid tools: access can also be granted by an active subscription
            # whose plan tier meets the tool's required tier.
            tool = Tool.query.filter_by(name=tool_name).first()
            if tool is not None and tool.is_paid and tool.required_plan_id is not None:
                from .subscription_service import get_subscription_service
                user_tier = get_subscription_service().get_active_tier(user_id)
                required_tier = tool.required_plan.tier_level if tool.required_plan else None
                if user_tier is not None and required_tier is not None and user_tier >= required_tier:
                    return ServiceResult.success(True)

            return ServiceResult.success(False)

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

    # ==================== Favorites ====================

    def get_user_favorites(self, user_id: int) -> ServiceResult[List[int]]:
        """
        Get list of tool IDs the user has favorited.

        Args:
            user_id: The user's ID

        Returns:
            ServiceResult with list of tool_id integers
        """
        try:
            favorites = ToolFavorite.query.filter_by(user_id=user_id).all()
            tool_ids = [fav.tool_id for fav in favorites]
            return ServiceResult.success(tool_ids)

        except Exception as e:
            self._log_error("get_user_favorites", e, user_id=user_id)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to retrieve favorites."
            )

    def add_favorite(self, user_id: int, tool_id: int) -> ServiceResult[bool]:
        """
        Add a tool to user's favorites.

        Args:
            user_id: The user's ID
            tool_id: The tool's ID

        Returns:
            ServiceResult with True on success
        """
        self._log_operation("add_favorite", user_id=user_id, tool_id=tool_id)

        # Verify tool exists
        tool = Tool.query.get(tool_id)
        if not tool:
            return ServiceResult.failure(
                ErrorCode.RESOURCE_NOT_FOUND,
                "Tool not found."
            )

        # Check if already favorited
        existing = ToolFavorite.query.filter_by(
            user_id=user_id, tool_id=tool_id
        ).first()
        if existing:
            return ServiceResult.failure(
                ErrorCode.RESOURCE_ALREADY_EXISTS,
                "Tool is already in favorites."
            )

        try:
            favorite = ToolFavorite(user_id=user_id, tool_id=tool_id)
            db.session.add(favorite)
            db.session.commit()

            self.logger.info(f"Favorite added: user_id={user_id}, tool_id={tool_id}")
            return ServiceResult.success(True)

        except Exception as e:
            db.session.rollback()
            self._log_error("add_favorite", e, user_id=user_id, tool_id=tool_id)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to add favorite."
            )

    def remove_favorite(self, user_id: int, tool_id: int) -> ServiceResult[bool]:
        """
        Remove a tool from user's favorites.

        Args:
            user_id: The user's ID
            tool_id: The tool's ID

        Returns:
            ServiceResult with True on success
        """
        self._log_operation("remove_favorite", user_id=user_id, tool_id=tool_id)

        try:
            favorite = ToolFavorite.query.filter_by(
                user_id=user_id, tool_id=tool_id
            ).first()

            if not favorite:
                return ServiceResult.failure(
                    ErrorCode.RESOURCE_NOT_FOUND,
                    "Favorite not found."
                )

            db.session.delete(favorite)
            db.session.commit()

            self.logger.info(f"Favorite removed: user_id={user_id}, tool_id={tool_id}")
            return ServiceResult.success(True)

        except Exception as e:
            db.session.rollback()
            self._log_error("remove_favorite", e, user_id=user_id, tool_id=tool_id)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to remove favorite."
            )

    # ==================== Usage History ====================

    #: Repeated uses of the same tool within this window are not re-logged,
    #: so per-keystroke or recalculation requests don't flood the history.
    USAGE_LOG_DEDUP_SECONDS = 60

    def log_usage(self, user_id: int, tool_name: str) -> ServiceResult[bool]:
        """
        Record a tool usage event for the user's history.

        Failures are reported in the result but must never block the tool
        operation itself — callers should ignore the outcome.

        Args:
            user_id: The user's ID
            tool_name: Exact Tool.name (e.g. "Tax Calculator")

        Returns:
            ServiceResult with True if a log entry was written (False when
            deduplicated), or error
        """
        try:
            tool = Tool.query.filter_by(name=tool_name).first()
            if not tool or not getattr(tool, "is_active", True):
                return ServiceResult.failure(
                    ErrorCode.NOT_FOUND,
                    f"Unknown tool: {tool_name}"
                )

            latest = (
                UsageLog.query
                .filter_by(user_id=user_id, tool_name=tool_name)
                .order_by(UsageLog.timestamp.desc(), UsageLog.id.desc())
                .first()
            )
            if latest and latest.timestamp:
                ts = latest.timestamp
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                age = (datetime.now(timezone.utc) - ts).total_seconds()
                if 0 <= age < self.USAGE_LOG_DEDUP_SECONDS:
                    return ServiceResult.success(False)

            db.session.add(UsageLog(user_id=user_id, tool_name=tool_name))
            db.session.commit()
            return ServiceResult.success(True)

        except Exception as e:
            db.session.rollback()
            self._log_error("log_usage", e, user_id=user_id, tool_name=tool_name)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to record tool usage."
            )

    def get_usage_history(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> ServiceResult[Dict[str, Any]]:
        """
        Get recent usage log entries for a user (most recent first).

        Args:
            user_id: The user's ID
            limit: Max entries to return (clamped to 1-100)
            offset: Number of entries to skip

        Returns:
            ServiceResult with {"history": [...], "total": int, "limit": int, "offset": int}
        """
        try:
            limit = max(1, min(int(limit), 100))
            offset = max(0, int(offset))
        except (TypeError, ValueError):
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                "limit and offset must be integers."
            )

        try:
            query = (
                UsageLog.query
                .filter_by(user_id=user_id)
                .order_by(UsageLog.timestamp.desc(), UsageLog.id.desc())
            )
            total = query.count()
            logs = query.offset(offset).limit(limit).all()

            def _to_utc_iso(ts):
                # Timestamps are stored naive-UTC; stamp the offset so JS
                # clients don't misparse them as local time.
                if ts is None:
                    return None
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                return ts.isoformat()

            history = [{
                "tool_name": log.tool_name,
                "timestamp": _to_utc_iso(log.timestamp),
            } for log in logs]

            return ServiceResult.success({
                "history": history,
                "total": total,
                "limit": limit,
                "offset": offset,
            })

        except Exception as e:
            self._log_error("get_usage_history", e, user_id=user_id)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to retrieve usage history."
            )

    # ==================== Categories ====================

    def get_categories(self) -> ServiceResult[List[Dict[str, Any]]]:
        """
        Get all active tool categories ordered for display.

        Returns:
            ServiceResult with list of category dicts
        """
        try:
            categories = (
                ToolCategory.query
                .filter_by(is_active=True)
                .order_by(ToolCategory.display_order.asc(), ToolCategory.name.asc())
                .all()
            )
            category_list = [{
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "icon": c.icon,
                "color": c.color,
                "display_order": c.display_order,
            } for c in categories]

            return ServiceResult.success(category_list)

        except Exception as e:
            self._log_error("get_categories", e)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to retrieve categories."
            )

    # ==================== Helper Methods ====================

    def _tool_to_info(self, tool: Tool) -> ToolInfo:
        """Convert Tool model to ToolInfo dataclass."""
        category = getattr(tool, 'category', None)
        required_plan = getattr(tool, 'required_plan', None)
        return ToolInfo(
            id=tool.id,
            name=tool.name,
            display_name=getattr(tool, 'display_name', None) or tool.name.replace('-', ' ').title(),
            description=getattr(tool, 'description', None),
            route=getattr(tool, 'route', None),
            is_default=getattr(tool, 'is_default', False),
            is_active=getattr(tool, 'is_active', True),
            icon=getattr(tool, 'icon', None),
            category_id=category.id if category else None,
            category_name=category.name if category else None,
            category_slug=category.slug if category else None,
            category_color=category.color if category else None,
            category_icon=category.icon if category else None,
            is_paid=bool(getattr(tool, 'is_paid', False)),
            required_plan_id=required_plan.id if required_plan else None,
            required_plan_name=required_plan.name if required_plan else None,
            required_plan_tier=required_plan.tier_level if required_plan else None,
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
