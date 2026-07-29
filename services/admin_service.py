"""
Admin Service Module

Backs the admin/superadmin control panel (user management, role changes,
tool-access grants, tool catalog CRUD). Wraps the existing Admin/SuperAdmin
model methods (model/users.py) with validation and DB-error handling so the
API layer stays thin.

The backend stores the SuperAdmin role as the polymorphic identity
"super_admin" (see model/users.py), while the frontend's role union uses
"superadmin" (no underscore). This module is the boundary that translates
between the two spellings.
"""

import math
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

from model import User, Admin, SuperAdmin, Tool, ToolAccess, db
from .base import BaseService, ServiceResult, ErrorCode

logger = logging.getLogger(__name__)

BACKEND_TO_FRONTEND_ROLE = {"super_admin": "superadmin"}
FRONTEND_TO_BACKEND_ROLE = {"superadmin": "super_admin"}


def to_frontend_role(role: str) -> str:
    return BACKEND_TO_FRONTEND_ROLE.get(role, role)


def to_backend_role(role: str) -> str:
    return FRONTEND_TO_BACKEND_ROLE.get(role, role)


@dataclass
class AdminUserData:
    """User record shaped for the admin panel (User + granted tool names)."""
    id: int
    username: str
    email: str
    role: str
    email_verified: bool
    created_at: Optional[datetime] = None
    fname: Optional[str] = None
    lname: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    last_login: Optional[datetime] = None
    tools: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "email_verified": self.email_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "fname": self.fname,
            "lname": self.lname,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip": self.zip,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "tools": self.tools,
        }


class AdminService(BaseService):
    """User management, role changes, and tool-access/catalog administration."""

    def _actor(self, actor_role: str):
        """Return the model instance whose method set matches the caller's role."""
        return SuperAdmin() if actor_role == "super_admin" else Admin()

    def _to_admin_user_data(self, user: User, tools: List[str]) -> AdminUserData:
        return AdminUserData(
            id=user.id,
            username=user.username,
            email=user.email,
            role=to_frontend_role(user.role),
            email_verified=user.email_verified,
            created_at=user.created_at,
            fname=user.fname,
            lname=user.lname,
            address=user.address,
            city=user.city,
            state=user.state,
            zip=user.zip,
            last_login=user.last_login,
            tools=tools,
        )

    def list_users(
        self, page: int = 1, per_page: int = 10, search: Optional[str] = None
    ) -> ServiceResult[Dict[str, Any]]:
        try:
            query = User.query
            if search:
                like = f"%{search.strip()}%"
                query = query.filter(
                    db.or_(
                        User.username.ilike(like),
                        User.email.ilike(like),
                        User.fname.ilike(like),
                        User.lname.ilike(like),
                    )
                )
            query = query.order_by(User.id.asc())

            total = query.count()
            total_pages = max(1, math.ceil(total / per_page)) if per_page else 1
            page = max(1, min(page, total_pages))
            users = query.offset((page - 1) * per_page).limit(per_page).all()

            user_ids = [u.id for u in users]
            tools_by_user: Dict[int, List[str]] = {}
            if user_ids:
                for row in ToolAccess.query.filter(ToolAccess.user_id.in_(user_ids)).all():
                    tools_by_user.setdefault(row.user_id, []).append(row.tool_name)

            data = [
                self._to_admin_user_data(u, tools_by_user.get(u.id, [])).to_dict()
                for u in users
            ]
            return ServiceResult.success({
                "users": data,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
            })
        except Exception as e:
            return self._handle_db_error("list_users", e)

    def create_user(self, actor_role: str, data: Dict[str, Any]) -> ServiceResult[Dict[str, Any]]:
        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""
        role = data.get("role") or "user"

        if role not in ("user", "admin"):
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR, "role must be 'user' or 'admin'."
            )
        if role == "admin" and actor_role != "super_admin":
            return ServiceResult.failure(
                ErrorCode.PERMISSION_DENIED, "Only SuperAdmins can create Admin users."
            )
        if not username or not email or not password:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR, "username, email, and password are required."
            )
        if len(password) < 8:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR, "Password must be at least 8 characters."
            )
        if User.query.filter_by(username=username).first():
            return ServiceResult.failure(
                ErrorCode.RESOURCE_ALREADY_EXISTS, "Username already exists."
            )
        if User.query.filter_by(email=email).first():
            return ServiceResult.failure(
                ErrorCode.RESOURCE_ALREADY_EXISTS, "Email already registered."
            )

        user_data = {
            "username": username,
            "email": email,
            "password": password,
            "fname": data.get("fname") or "",
            "lname": data.get("lname") or "",
            "address": data.get("address") or "",
            "city": data.get("city") or "",
            "state": data.get("state") or "",
            "zip": data.get("zip") or "",
            "role": role,
        }

        try:
            new_user = self._actor(actor_role).create_user(user_data)
            return ServiceResult.success(self._to_admin_user_data(new_user, []).to_dict())
        except Exception as e:
            db.session.rollback()
            return self._handle_db_error("create_user", e)

    def update_user(
        self, actor_role: str, user_id: int, data: Dict[str, Any]
    ) -> ServiceResult[Dict[str, Any]]:
        target = User.query.get(user_id)
        if not target:
            return ServiceResult.failure(ErrorCode.RESOURCE_NOT_FOUND, "User not found.")
        if actor_role != "super_admin" and target.role != "user":
            return ServiceResult.failure(
                ErrorCode.PERMISSION_DENIED, "Admins can only edit regular users."
            )

        allowed_fields = ("fname", "lname", "address", "city", "state", "zip", "password")
        user_data = {k: v for k, v in data.items() if k in allowed_fields and v is not None}

        if "password" in user_data and len(user_data["password"]) < 8:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR, "Password must be at least 8 characters."
            )

        try:
            self._actor(actor_role).update_user(user_id, user_data)
        except Exception as e:
            db.session.rollback()
            return self._handle_db_error("update_user", e)

        updated = User.query.get(user_id)
        tools = [row.tool_name for row in ToolAccess.query.filter_by(user_id=user_id).all()]
        return ServiceResult.success(self._to_admin_user_data(updated, tools).to_dict())

    def delete_user(self, actor_role: str, user_id: int) -> ServiceResult[None]:
        target = User.query.get(user_id)
        if not target:
            return ServiceResult.failure(ErrorCode.RESOURCE_NOT_FOUND, "User not found.")
        if actor_role != "super_admin" and target.role != "user":
            return ServiceResult.failure(
                ErrorCode.PERMISSION_DENIED, "Admins can only delete regular users."
            )

        try:
            self._actor(actor_role).delete_user(user_id)
        except Exception as e:
            db.session.rollback()
            return self._handle_db_error("delete_user", e)

        return ServiceResult.success(None)

    def change_role(self, user_id: int, new_role: str) -> ServiceResult[Dict[str, Any]]:
        """SuperAdmin-only: promote/demote a user between user/admin/superadmin."""
        backend_role = to_backend_role(new_role)
        if backend_role not in ("user", "admin", "super_admin"):
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR, "role must be 'user', 'admin', or 'superadmin'."
            )

        target = User.query.get(user_id)
        if not target:
            return ServiceResult.failure(ErrorCode.RESOURCE_NOT_FOUND, "User not found.")

        # change_user_role swaps polymorphic subclass by deleting and
        # re-inserting the row (joined-table inheritance), so the row gets a
        # new id - look the user back up by username, which is preserved.
        username = target.username

        try:
            SuperAdmin().change_user_role(user_id, backend_role)
        except Exception as e:
            db.session.rollback()
            return self._handle_db_error("change_role", e)

        updated = User.query.filter_by(username=username).first()
        if not updated:
            return ServiceResult.failure(
                ErrorCode.INTERNAL_ERROR, "Role changed but user could not be reloaded."
            )
        tools = [row.tool_name for row in ToolAccess.query.filter_by(user_id=updated.id).all()]
        return ServiceResult.success(self._to_admin_user_data(updated, tools).to_dict())

    def grant_tool_access(
        self, actor_role: str, user_id: int, tool_name: str
    ) -> ServiceResult[None]:
        if not User.query.get(user_id):
            return ServiceResult.failure(ErrorCode.RESOURCE_NOT_FOUND, "User not found.")
        if ToolAccess.query.filter_by(user_id=user_id, tool_name=tool_name).first():
            return ServiceResult.success(None)

        try:
            self._actor(actor_role).grant_tool_access(user_id, tool_name)
        except Exception as e:
            db.session.rollback()
            return self._handle_db_error("grant_tool_access", e)

        return ServiceResult.success(None)

    def revoke_tool_access(
        self, actor_role: str, user_id: int, tool_name: str
    ) -> ServiceResult[None]:
        if not User.query.get(user_id):
            return ServiceResult.failure(ErrorCode.RESOURCE_NOT_FOUND, "User not found.")

        try:
            self._actor(actor_role).revoke_tool_access(user_id, tool_name)
        except Exception as e:
            db.session.rollback()
            return self._handle_db_error("revoke_tool_access", e)

        return ServiceResult.success(None)

    # ==================== Tool catalog (SuperAdmin only) ====================

    def list_tools(self) -> ServiceResult[List[Dict[str, Any]]]:
        try:
            tools = Tool.query.order_by(Tool.id.asc()).all()
            return ServiceResult.success([self._tool_to_dict(t) for t in tools])
        except Exception as e:
            return self._handle_db_error("list_tools", e)

    @staticmethod
    def _tool_to_dict(tool: Tool) -> Dict[str, Any]:
        return {
            "id": tool.id,
            "name": tool.name,
            "display_name": tool.display_name or tool.name,
            "description": tool.description,
            "route": tool.route,
            "is_default": tool.is_default,
        }

    def create_tool(self, data: Dict[str, Any]) -> ServiceResult[Dict[str, Any]]:
        name = (data.get("name") or "").strip()
        route = (data.get("route") or "").strip()
        if not name or not route:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR, "name and route are required."
            )
        if Tool.query.filter_by(name=name).first():
            return ServiceResult.failure(
                ErrorCode.RESOURCE_ALREADY_EXISTS, "A tool with this name already exists."
            )

        try:
            tool = Tool(
                name=name,
                description=data.get("description") or "",
                route=route,
                is_default=bool(data.get("is_default", False)),
            )
            tool.display_name = data.get("display_name") or name
            db.session.add(tool)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return self._handle_db_error("create_tool", e)

        return ServiceResult.success(self._tool_to_dict(tool))

    def update_tool(self, tool_id: int, data: Dict[str, Any]) -> ServiceResult[Dict[str, Any]]:
        tool = Tool.query.get(tool_id)
        if not tool:
            return ServiceResult.failure(ErrorCode.RESOURCE_NOT_FOUND, "Tool not found.")

        try:
            if "display_name" in data:
                tool.display_name = data["display_name"]
            if "description" in data:
                tool.description = data["description"]
            if "route" in data:
                tool.route = data["route"]
            if "is_default" in data:
                tool.is_default = bool(data["is_default"])
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return self._handle_db_error("update_tool", e)

        return ServiceResult.success(self._tool_to_dict(tool))

    def delete_tool(self, tool_id: int) -> ServiceResult[None]:
        tool = Tool.query.get(tool_id)
        if not tool:
            return ServiceResult.failure(ErrorCode.RESOURCE_NOT_FOUND, "Tool not found.")

        try:
            ToolAccess.query.filter_by(tool_name=tool.name).delete()
            db.session.delete(tool)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return self._handle_db_error("delete_tool", e)

        return ServiceResult.success(None)


_admin_service_instance: Optional[AdminService] = None


def get_admin_service() -> AdminService:
    global _admin_service_instance
    if _admin_service_instance is None:
        _admin_service_instance = AdminService()
    return _admin_service_instance
