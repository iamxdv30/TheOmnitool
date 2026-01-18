"""
User Service Module

Handles user management business logic:
- User profile retrieval and updates
- Password changes
- User dashboard data
- User tool access

This service is used by both legacy HTML routes and new API routes.
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from model import User, Admin, SuperAdmin, db, ToolAccess, UserFactory
from config.auth_config import AuthConfig
from .base import BaseService, ServiceResult, ErrorCode

logger = logging.getLogger(__name__)


@dataclass
class UserProfileData:
    """Complete user profile data for display/editing."""
    id: int
    username: str
    email: str
    name: Optional[str]
    fname: Optional[str]
    lname: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    role: str
    email_verified: bool
    created_at: Optional[datetime]
    last_login: Optional[datetime]
    is_active: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "name": self.name,
            "fname": self.fname,
            "lname": self.lname,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip": self.zip_code,
            "role": self.role,
            "email_verified": self.email_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active,
        }


@dataclass
class DashboardData:
    """Data for user dashboard display."""
    user: UserProfileData
    tools: List[str]
    usage_stats: Optional[Dict[str, int]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user": self.user.to_dict(),
            "tools": self.tools,
            "usage_stats": self.usage_stats,
        }


class UserService(BaseService):
    """
    Service for user management operations.

    Handles profile management, password changes, and user data retrieval.
    """

    def __init__(self):
        super().__init__()

    def get_user_by_id(self, user_id: int) -> ServiceResult[UserProfileData]:
        """
        Get a user's complete profile by their ID.

        Args:
            user_id: The user's database ID

        Returns:
            ServiceResult with UserProfileData on success
        """
        user = User.query.get(user_id)

        if not user:
            return ServiceResult.failure(
                ErrorCode.RESOURCE_NOT_FOUND,
                "User not found."
            )

        return ServiceResult.success(self._user_to_profile_data(user))

    def get_user_by_username(self, username: str) -> ServiceResult[UserProfileData]:
        """
        Get a user's complete profile by their username.

        Args:
            username: The user's username

        Returns:
            ServiceResult with UserProfileData on success
        """
        user = User.query.filter_by(username=username).first()

        if not user:
            return ServiceResult.failure(
                ErrorCode.RESOURCE_NOT_FOUND,
                "User not found."
            )

        return ServiceResult.success(self._user_to_profile_data(user))

    def get_dashboard_data(self, user_id: int) -> ServiceResult[DashboardData]:
        """
        Get all data needed for the user dashboard.

        Args:
            user_id: The user's ID

        Returns:
            ServiceResult with DashboardData on success
        """
        user = User.query.get(user_id)

        if not user:
            return ServiceResult.failure(
                ErrorCode.RESOURCE_NOT_FOUND,
                "User not found."
            )

        # Get user's tools
        tools = self._get_user_tools(user_id)

        # Get usage stats (optional - could be expensive for large datasets)
        usage_stats = self._get_usage_stats(user_id)

        return ServiceResult.success(DashboardData(
            user=self._user_to_profile_data(user),
            tools=tools,
            usage_stats=usage_stats,
        ))

    def get_user_tools(self, user_id: int) -> ServiceResult[List[str]]:
        """
        Get list of tools a user has access to.

        Args:
            user_id: The user's ID

        Returns:
            ServiceResult with list of tool names
        """
        user = User.query.get(user_id)

        if not user:
            return ServiceResult.failure(
                ErrorCode.RESOURCE_NOT_FOUND,
                "User not found."
            )

        tools = self._get_user_tools(user_id)
        return ServiceResult.success(tools)

    def update_profile(
        self,
        user_id: int,
        fname: Optional[str] = None,
        lname: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        name: Optional[str] = None,
    ) -> ServiceResult[UserProfileData]:
        """
        Update a user's profile information.

        Args:
            user_id: The user's ID
            fname: First name (optional)
            lname: Last name (optional)
            address: Address (optional)
            city: City (optional)
            state: State (optional)
            zip_code: ZIP code (optional)
            name: Full name (optional)

        Returns:
            ServiceResult with updated UserProfileData on success
        """
        self._log_operation("update_profile", user_id=user_id)

        user = User.query.get(user_id)

        if not user:
            return ServiceResult.failure(
                ErrorCode.RESOURCE_NOT_FOUND,
                "User not found."
            )

        try:
            # Update fields if provided
            if fname is not None:
                user.fname = fname
            if lname is not None:
                user.lname = lname
            if address is not None:
                user.address = address
            if city is not None:
                user.city = city
            if state is not None:
                user.state = state
            if zip_code is not None:
                user.zip = zip_code
            if name is not None:
                user.name = name

            db.session.commit()

            self.logger.info(f"Profile updated for user ID: {user_id}")
            return ServiceResult.success(self._user_to_profile_data(user))

        except Exception as e:
            db.session.rollback()
            self._log_error("update_profile", e, user_id=user_id)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to update profile. Please try again."
            )

    def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
        confirm_password: str
    ) -> ServiceResult[bool]:
        """
        Change a user's password.

        Requires current password verification.

        Args:
            user_id: The user's ID
            current_password: Current password for verification
            new_password: New password
            confirm_password: New password confirmation

        Returns:
            ServiceResult with True on success
        """
        self._log_operation("change_password", user_id=user_id)

        # Validate inputs
        if not current_password:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                "Current password is required."
            )

        if not new_password or not confirm_password:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                "New password and confirmation are required."
            )

        if new_password != confirm_password:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                "New passwords do not match."
            )

        # Validate password strength
        is_valid, errors = AuthConfig.validate_password(new_password)
        if not is_valid:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                errors[0] if errors else "Password does not meet requirements.",
                details={"errors": errors}
            )

        # Find user
        user = User.query.get(user_id)

        if not user:
            return ServiceResult.failure(
                ErrorCode.RESOURCE_NOT_FOUND,
                "User not found."
            )

        # Verify current password
        if not User.check_password(user, current_password):
            self.logger.warning(f"Password change failed - incorrect current password for user ID: {user_id}")
            return ServiceResult.failure(
                ErrorCode.AUTH_INVALID_CREDENTIALS,
                "Current password is incorrect."
            )

        try:
            user.set_password(new_password)
            db.session.commit()

            self.logger.info(f"Password changed successfully for user ID: {user_id}")
            return ServiceResult.success(True)

        except Exception as e:
            db.session.rollback()
            self._log_error("change_password", e, user_id=user_id)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to change password. Please try again."
            )

    def update_email(
        self,
        user_id: int,
        new_email: str,
        current_password: str
    ) -> ServiceResult[bool]:
        """
        Update a user's email address.

        Requires password verification and will mark email as unverified.

        Args:
            user_id: The user's ID
            new_email: New email address
            current_password: Current password for verification

        Returns:
            ServiceResult with True on success (email marked unverified)
        """
        self._log_operation("update_email", user_id=user_id, new_email=new_email)

        if not new_email:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                "Email address is required."
            )

        if not current_password:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                "Current password is required to change email."
            )

        user = User.query.get(user_id)

        if not user:
            return ServiceResult.failure(
                ErrorCode.RESOURCE_NOT_FOUND,
                "User not found."
            )

        # Verify password
        if not User.check_password(user, current_password):
            return ServiceResult.failure(
                ErrorCode.AUTH_INVALID_CREDENTIALS,
                "Current password is incorrect."
            )

        # Check if email is already in use
        new_email_lower = new_email.lower()
        existing_user = User.query.filter_by(email=new_email_lower).first()
        if existing_user and existing_user.id != user_id:
            return ServiceResult.failure(
                ErrorCode.RESOURCE_ALREADY_EXISTS,
                "This email is already in use."
            )

        try:
            user.email = new_email_lower
            user.email_verified = False  # Require re-verification

            db.session.commit()

            self.logger.info(f"Email updated for user ID: {user_id} - requires verification")
            return ServiceResult.success(True)

        except Exception as e:
            db.session.rollback()
            self._log_error("update_email", e, user_id=user_id)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to update email. Please try again."
            )

    def _user_to_profile_data(self, user: User) -> UserProfileData:
        """Convert a User model to UserProfileData."""
        return UserProfileData(
            id=user.id,
            username=user.username,
            email=user.email,
            name=getattr(user, 'name', None),
            fname=getattr(user, 'fname', None),
            lname=getattr(user, 'lname', None),
            address=getattr(user, 'address', None),
            city=getattr(user, 'city', None),
            state=getattr(user, 'state', None),
            zip_code=getattr(user, 'zip', None),
            role=user.role,
            email_verified=getattr(user, 'email_verified', True),
            created_at=getattr(user, 'created_at', None),
            last_login=getattr(user, 'last_login', None),
            is_active=getattr(user, 'is_active', True),
        )

    def _get_user_tools(self, user_id: int) -> List[str]:
        """Get list of tool names for a user."""
        tool_access_list = ToolAccess.query.filter_by(user_id=user_id).all()
        return [access.tool_name for access in tool_access_list]

    def _get_usage_stats(self, user_id: int) -> Optional[Dict[str, int]]:
        """Get usage statistics for a user."""
        # This could be expensive - consider caching or lazy loading
        try:
            from model import UsageLog
            logs = UsageLog.query.filter_by(user_id=user_id).all()

            stats = {}
            for log in logs:
                tool_name = getattr(log, 'tool_name', 'unknown')
                stats[tool_name] = stats.get(tool_name, 0) + 1

            return stats if stats else None

        except Exception as e:
            self.logger.warning(f"Failed to get usage stats for user {user_id}: {e}")
            return None


# Singleton instance
_user_service: Optional[UserService] = None


def get_user_service() -> UserService:
    """Get the singleton UserService instance."""
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service
