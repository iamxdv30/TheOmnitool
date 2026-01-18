"""
Authentication Service Module

Centralizes all authentication business logic:
- User login/logout
- User registration
- Email verification
- Password reset
- ReCAPTCHA verification
- Session management

This is the core service that routes/auth_routes.py and routes/api/auth_api.py
will use. Routes handle HTTP concerns, this service handles business logic.
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import text

from model import User, db, UserFactory
from config.auth_config import AuthConfig
from .base import BaseService, ServiceResult, ErrorCode
from .token_service import get_token_service, TokenService
from .email_service import get_email_service, EmailService

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """Represents user profile data for API responses."""
    id: int
    username: str
    email: str
    name: Optional[str]
    role: str
    email_verified: bool
    created_at: Optional[datetime]
    last_login: Optional[datetime]
    tools: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "email_verified": self.email_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "tools": self.tools,
        }


@dataclass
class LoginResult:
    """Result of a successful login."""
    user: UserProfile
    redirect_route: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user": self.user.to_dict(),
            "redirect_route": self.redirect_route,
        }


@dataclass
class RegistrationResult:
    """Result of a successful registration."""
    user_id: int
    email: str
    name: str
    verification_email_sent: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "name": self.name,
            "verification_email_sent": self.verification_email_sent,
        }


class AuthService(BaseService):
    """
    Authentication service handling all auth-related business logic.

    This service is stateless and thread-safe. It can be used by both
    legacy HTML routes and new API routes.
    """

    def __init__(
        self,
        token_service: TokenService = None,
        email_service: EmailService = None
    ):
        """
        Initialize the auth service.

        Args:
            token_service: TokenService instance (uses singleton if not provided)
            email_service: EmailService instance (uses singleton if not provided)
        """
        super().__init__()
        self._token_service = token_service or get_token_service()
        self._email_service = email_service or get_email_service()

    def verify_recaptcha(
        self,
        recaptcha_response: str,
        remote_ip: Optional[str] = None
    ) -> ServiceResult[bool]:
        """
        Verify reCAPTCHA response with Google's servers.

        Args:
            recaptcha_response: The g-recaptcha-response from the form
            remote_ip: Optional client IP for additional verification

        Returns:
            ServiceResult with True if verified, or error
        """
        # Skip if captcha is disabled
        if not AuthConfig.is_captcha_enabled():
            self.logger.info("Captcha verification skipped - captcha disabled")
            return ServiceResult.success(True)

        if not recaptcha_response:
            self.logger.warning("Captcha verification failed - no response token provided")
            return ServiceResult.failure(
                ErrorCode.RECAPTCHA_FAILED,
                "Please complete the captcha verification."
            )

        try:
            data = {
                "secret": AuthConfig.RECAPTCHA_SECRET_KEY,
                "response": recaptcha_response,
            }
            if remote_ip:
                data["remoteip"] = remote_ip

            self.logger.info("Sending captcha verification request to Google")
            response = requests.post(
                AuthConfig.RECAPTCHA_VERIFY_URL,
                data=data,
                timeout=5
            )
            result = response.json()

            if result.get("success", False):
                self.logger.info("Captcha verification successful")
                return ServiceResult.success(True)
            else:
                error_codes = result.get("error-codes", [])
                self.logger.warning(f"Captcha verification failed - Google errors: {error_codes}")
                return ServiceResult.failure(
                    ErrorCode.RECAPTCHA_FAILED,
                    "Captcha verification failed. Please try again."
                )

        except Exception as e:
            self._log_error("verify_recaptcha", e)
            return ServiceResult.failure(
                ErrorCode.RECAPTCHA_FAILED,
                "Captcha verification failed. Please try again."
            )

    def check_email_verified(self, user: User) -> bool:
        """
        Ultra-strict email verification check.

        Directly queries the database to ensure data integrity.

        Args:
            user: The User object to check

        Returns:
            True if email is verified, False otherwise
        """
        try:
            result = db.session.execute(
                text("SELECT email_verified FROM users WHERE id = :user_id"),
                {"user_id": user.id}
            ).fetchone()

            if result is None:
                self.logger.error(f"User {user.username} not found in database - BLOCKING")
                return False

            db_email_verified = bool(result[0])

            self.logger.info(
                f"Email verification status for {user.username}: {db_email_verified}"
            )

            # Sync the user object with database state
            if hasattr(user, 'email_verified'):
                user.email_verified = db_email_verified

            return db_email_verified

        except Exception as e:
            self.logger.error(
                f"Database verification check failed for {user.username}: {e}"
            )
            return False

    def login(
        self,
        username: str,
        password: str,
        recaptcha_response: Optional[str] = None,
        client_ip: Optional[str] = None
    ) -> ServiceResult[LoginResult]:
        """
        Authenticate a user.

        Args:
            username: Username to authenticate
            password: Password to verify
            recaptcha_response: Optional reCAPTCHA response
            client_ip: Optional client IP for logging and reCAPTCHA

        Returns:
            ServiceResult with LoginResult on success, or error
        """
        self._log_operation("login", username=username, client_ip=client_ip)

        # Validate required fields
        if not username:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                "Username is required."
            )

        if not password:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                "Password is required."
            )

        # Verify captcha if enabled
        if AuthConfig.is_captcha_enabled():
            captcha_result = self.verify_recaptcha(recaptcha_response, client_ip)
            if captcha_result.is_failure:
                return captcha_result

        # Find user
        user = User.query.filter_by(username=username).first()

        if not user:
            self.logger.warning(f"Login failed - user not found: '{username}'")
            return ServiceResult.failure(
                ErrorCode.AUTH_INVALID_CREDENTIALS,
                "Invalid username or password."
            )

        # Verify password
        if not User.check_password(user, password):
            self.logger.warning(f"Login failed for '{username}' - invalid password")
            return ServiceResult.failure(
                ErrorCode.AUTH_INVALID_CREDENTIALS,
                "Invalid username or password."
            )

        # Check email verification
        if not self.check_email_verified(user):
            self.logger.warning(f"Login blocked for '{username}' - email not verified")
            return ServiceResult.failure(
                ErrorCode.AUTH_UNVERIFIED,
                "Your email address must be verified before you can log in.",
                details={"email": user.email, "name": getattr(user, 'name', user.username)}
            )

        # Update last login
        if hasattr(user, 'last_login'):
            user.last_login = datetime.utcnow()
            db.session.commit()

        # Get user's tools
        tools = []
        if hasattr(user, 'tool_access'):
            tools = [access.tool_name for access in user.tool_access]

        # Determine redirect based on role
        redirect_routes = {
            "super_admin": "admin.superadmin_dashboard",
            "admin": "admin.admin_dashboard",
        }
        redirect_route = redirect_routes.get(user.role, "user.user_dashboard")

        # Build user profile
        profile = UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            name=getattr(user, 'name', None),
            role=user.role,
            email_verified=True,  # We've verified above
            created_at=getattr(user, 'created_at', None),
            last_login=getattr(user, 'last_login', None),
            tools=tools,
        )

        self.logger.info(f"LOGIN SUCCESS: User '{username}' authenticated")
        return ServiceResult.success(LoginResult(user=profile, redirect_route=redirect_route))

    def register(
        self,
        name: str,
        username: str,
        email: str,
        password: str,
        confirm_password: str,
        recaptcha_response: Optional[str] = None,
        client_ip: Optional[str] = None
    ) -> ServiceResult[RegistrationResult]:
        """
        Register a new user.

        Args:
            name: User's full name
            username: Desired username
            email: User's email address
            password: Desired password
            confirm_password: Password confirmation
            recaptcha_response: Optional reCAPTCHA response
            client_ip: Optional client IP for logging

        Returns:
            ServiceResult with RegistrationResult on success, or error
        """
        self._log_operation("register", username=username, email=email)

        # Validate required fields
        if not all([name, username, email, password, confirm_password]):
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                "All fields are required."
            )

        # Validate passwords match
        if password != confirm_password:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                "Passwords do not match."
            )

        # Validate password strength
        is_valid, errors = AuthConfig.validate_password(password)
        if not is_valid:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                errors[0] if errors else "Password does not meet requirements.",
                details={"errors": errors}
            )

        # Verify captcha if enabled
        if AuthConfig.is_captcha_enabled():
            captcha_result = self.verify_recaptcha(recaptcha_response, client_ip)
            if captcha_result.is_failure:
                return captcha_result

        # Check for existing username
        if User.query.filter_by(username=username).first():
            self.logger.warning(f"Registration failed - username '{username}' already exists")
            return ServiceResult.failure(
                ErrorCode.RESOURCE_ALREADY_EXISTS,
                "Username already exists. Please choose a different username."
            )

        # Check for existing email
        if User.query.filter_by(email=email.lower()).first():
            self.logger.warning(f"Registration failed - email '{email}' already registered")
            return ServiceResult.failure(
                ErrorCode.RESOURCE_ALREADY_EXISTS,
                "Email already registered. Please use a different email or try logging in."
            )

        try:
            # Parse name
            fname, lname = self._parse_full_name(name)

            # Create user
            new_user = UserFactory.create_user(
                name=name,
                username=username,
                email=email.lower(),
                password=password,
                role='user',
                email_verified=False
            )

            db.session.add(new_user)
            db.session.commit()

            self.logger.info(f"User created - ID: {new_user.id}")

            # Assign default tools
            if hasattr(User, 'assign_default_tools'):
                User.assign_default_tools(new_user.id)
                self.logger.info(f"Default tools assigned to user: {new_user.id}")

            # Send verification email
            email_result = self._email_service.send_verification_email(email, fname)
            verification_sent = email_result.is_success

            if not verification_sent:
                self.logger.error(f"Failed to send verification email to: {email}")

            self.logger.info(f"REGISTRATION SUCCESS: User '{username}' ({email}) registered")

            return ServiceResult.success(RegistrationResult(
                user_id=new_user.id,
                email=email,
                name=fname,
                verification_email_sent=verification_sent,
            ))

        except Exception as e:
            db.session.rollback()
            self._log_error("register", e, username=username, email=email)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "An error occurred during registration. Please try again."
            )

    def verify_email(self, token: str) -> ServiceResult[UserProfile]:
        """
        Verify a user's email address using the verification token.

        Args:
            token: The verification token from the email link

        Returns:
            ServiceResult with UserProfile on success (for auto-login)
        """
        self._log_operation("verify_email", token_present=bool(token))

        # Verify the token
        token_result = self._token_service.verify_email_verification_token(token)
        if token_result.is_failure:
            return ServiceResult.from_error(token_result.error)

        email = token_result.data

        # Find the user
        user = User.query.filter_by(email=email).first()
        if not user:
            self.logger.error(f"User not found for email verification: '{email}'")
            return ServiceResult.failure(
                ErrorCode.RESOURCE_NOT_FOUND,
                "User account not found. Please register again."
            )

        try:
            # Mark email as verified
            user.email_verified = True

            # Also update directly in database as safety measure
            db.session.execute(
                text("UPDATE users SET email_verified = 1 WHERE id = :user_id"),
                {"user_id": user.id}
            )

            # Update last login (since we're auto-logging in)
            if hasattr(user, 'last_login'):
                user.last_login = datetime.utcnow()

            db.session.commit()

            # Get user's tools
            tools = []
            if hasattr(user, 'tool_access'):
                tools = [access.tool_name for access in user.tool_access]

            profile = UserProfile(
                id=user.id,
                username=user.username,
                email=user.email,
                name=getattr(user, 'name', None),
                role=user.role,
                email_verified=True,
                created_at=getattr(user, 'created_at', None),
                last_login=getattr(user, 'last_login', None),
                tools=tools,
            )

            self.logger.info(f"EMAIL VERIFICATION SUCCESS: User '{user.username}' verified")
            return ServiceResult.success(profile)

        except Exception as e:
            db.session.rollback()
            self._log_error("verify_email", e, email=email)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "An error occurred during email verification. Please try again."
            )

    def resend_verification_email(self, email: str) -> ServiceResult[bool]:
        """
        Resend verification email to a user.

        Args:
            email: The email address to send to

        Returns:
            ServiceResult with True on success
        """
        self._log_operation("resend_verification_email", email=email)

        if not email:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                "Email address is required."
            )

        user = User.query.filter_by(email=email).first()

        if not user:
            self.logger.error(f"User not found for resend verification: {email}")
            return ServiceResult.failure(
                ErrorCode.RESOURCE_NOT_FOUND,
                "User account not found. Please register again."
            )

        # Check if already verified
        if hasattr(user, 'email_verified') and user.email_verified:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                "Your email is already verified. You can log in now."
            )

        # Send verification email
        fname = getattr(user, 'name', email.split('@')[0])
        email_result = self._email_service.send_verification_email(email, fname)

        if email_result.is_failure:
            return email_result

        self.logger.info(f"Verification email resent to: {email}")
        return ServiceResult.success(True)

    def request_password_reset(self, email: str) -> ServiceResult[bool]:
        """
        Request a password reset email.

        For security, always returns success even if email doesn't exist.

        Args:
            email: The email address

        Returns:
            ServiceResult with True (always succeeds from caller's perspective)
        """
        self._log_operation("request_password_reset", email=email)

        user = User.query.filter_by(email=email).first()

        if user:
            # Get user's name
            user_name = "User"
            if hasattr(user, 'name') and user.name:
                user_name = user.name
            elif hasattr(user, 'fname') and hasattr(user, 'lname'):
                user_name = f"{user.fname} {user.lname}"

            # Send reset email
            email_result = self._email_service.send_password_reset_email(email, user_name)

            if email_result.is_failure:
                self.logger.error(f"Failed to send password reset email to: {email}")
        else:
            self.logger.info(f"Password reset requested for non-existent user: {email}")

        # Always return success for security (don't reveal if email exists)
        return ServiceResult.success(True)

    def reset_password(
        self,
        token: str,
        new_password: str,
        confirm_password: str
    ) -> ServiceResult[bool]:
        """
        Reset a user's password using a reset token.

        Args:
            token: The password reset token
            new_password: The new password
            confirm_password: Password confirmation

        Returns:
            ServiceResult with True on success
        """
        self._log_operation("reset_password", token_present=bool(token))

        # Validate inputs
        if not new_password or not confirm_password:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                "Both password fields are required."
            )

        if new_password != confirm_password:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                "Passwords do not match."
            )

        # Validate password strength
        is_valid, errors = AuthConfig.validate_password(new_password)
        if not is_valid:
            return ServiceResult.failure(
                ErrorCode.VALIDATION_ERROR,
                errors[0] if errors else "Password does not meet requirements.",
                details={"errors": errors}
            )

        # Verify token
        token_result = self._token_service.verify_password_reset_token(token)
        if token_result.is_failure:
            return ServiceResult.from_error(token_result.error)

        email = token_result.data

        # Find and update user
        user = User.query.filter_by(email=email).first()
        if not user:
            self.logger.error(f"User not found during password reset: '{email}'")
            return ServiceResult.failure(
                ErrorCode.RESOURCE_NOT_FOUND,
                "User account not found."
            )

        try:
            user.set_password(new_password)
            db.session.commit()

            self.logger.info(f"PASSWORD RESET SUCCESS: Password updated for user '{user.username}'")
            return ServiceResult.success(True)

        except Exception as e:
            db.session.rollback()
            self._log_error("reset_password", e, email=email)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "An error occurred while resetting your password. Please try again."
            )

    def validate_reset_token(self, token: str) -> ServiceResult[str]:
        """
        Validate a password reset token without using it.

        Args:
            token: The token to validate

        Returns:
            ServiceResult with the email if valid
        """
        return self._token_service.verify_password_reset_token(token)

    def get_user_by_id(self, user_id: int) -> ServiceResult[UserProfile]:
        """
        Get a user's profile by their ID.

        Args:
            user_id: The user's ID

        Returns:
            ServiceResult with UserProfile on success
        """
        user = User.query.get(user_id)

        if not user:
            return ServiceResult.failure(
                ErrorCode.RESOURCE_NOT_FOUND,
                "User not found."
            )

        tools = []
        if hasattr(user, 'tool_access'):
            tools = [access.tool_name for access in user.tool_access]

        profile = UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            name=getattr(user, 'name', None),
            role=user.role,
            email_verified=getattr(user, 'email_verified', True),
            created_at=getattr(user, 'created_at', None),
            last_login=getattr(user, 'last_login', None),
            tools=tools,
        )

        return ServiceResult.success(profile)

    def _parse_full_name(self, full_name: str) -> tuple:
        """
        Parse full name into first and last name.

        Args:
            full_name: The full name to parse

        Returns:
            Tuple of (first_name, last_name)
        """
        if not full_name or not full_name.strip():
            return "User", "Name"

        name_parts = full_name.strip().split()
        if len(name_parts) == 1:
            return name_parts[0], "User"
        elif len(name_parts) == 2:
            return name_parts[0], name_parts[1]
        else:
            return name_parts[0], " ".join(name_parts[1:])


# Singleton instance
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Get the singleton AuthService instance."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
