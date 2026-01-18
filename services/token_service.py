"""
Token Service Module

Handles secure token generation and verification for:
- Email verification tokens
- Password reset tokens
- CSRF tokens (for API)

Centralizes the token logic that was previously scattered across routes.
"""

import os
import logging
from typing import Optional
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from .base import BaseService, ServiceResult, ErrorCode

logger = logging.getLogger(__name__)


class TokenService(BaseService):
    """
    Service for generating and verifying secure tokens.

    Uses itsdangerous URLSafeTimedSerializer for time-limited tokens.
    """

    # Default token expiration times (in seconds)
    EMAIL_VERIFICATION_EXPIRY = 3600  # 1 hour
    PASSWORD_RESET_EXPIRY = 3600  # 1 hour
    CSRF_EXPIRY = 86400  # 24 hours

    def __init__(self):
        super().__init__()
        self._token_secret_key = os.getenv("TOKEN_SECRET_KEY")
        self._security_salt = os.getenv("SECURITY_PASSWORD_SALT")
        self._validate_config()

    def _validate_config(self):
        """Validate that required environment variables are set."""
        if not self._token_secret_key:
            raise ValueError(
                "TOKEN_SECRET_KEY is not set. Please set it in environment variables."
            )
        if not self._security_salt:
            raise ValueError(
                "SECURITY_PASSWORD_SALT is not set. Please set it in environment variables."
            )

    def _get_serializer(self) -> URLSafeTimedSerializer:
        """Get the URL-safe timed serializer."""
        return URLSafeTimedSerializer(self._token_secret_key)

    def generate_email_verification_token(self, email: str) -> str:
        """
        Generate a secure token for email verification.

        Args:
            email: The email address to encode in the token

        Returns:
            A URL-safe token string
        """
        serializer = self._get_serializer()
        token = serializer.dumps(email, salt=self._security_salt)
        self._log_operation("generate_email_verification_token", email=email)
        return token

    def verify_email_verification_token(
        self,
        token: str,
        max_age: int = None
    ) -> ServiceResult[str]:
        """
        Verify an email verification token and extract the email.

        Args:
            token: The token to verify
            max_age: Maximum token age in seconds (default: EMAIL_VERIFICATION_EXPIRY)

        Returns:
            ServiceResult containing the email if valid, or an error
        """
        if max_age is None:
            max_age = self.EMAIL_VERIFICATION_EXPIRY

        serializer = self._get_serializer()

        try:
            email = serializer.loads(
                token,
                salt=self._security_salt,
                max_age=max_age
            )
            self._log_operation("verify_email_verification_token", email=email, status="success")
            return ServiceResult.success(email)

        except SignatureExpired:
            self.logger.warning("Email verification token expired")
            return ServiceResult.failure(
                ErrorCode.TOKEN_EXPIRED,
                "The verification link has expired. Please request a new one."
            )

        except BadSignature:
            self.logger.warning("Invalid email verification token signature")
            return ServiceResult.failure(
                ErrorCode.TOKEN_INVALID,
                "Invalid verification link. Please request a new one."
            )

        except Exception as e:
            self._log_error("verify_email_verification_token", e)
            return ServiceResult.failure(
                ErrorCode.TOKEN_INVALID,
                "Failed to verify token. Please request a new one."
            )

    def generate_password_reset_token(self, email: str) -> str:
        """
        Generate a secure token for password reset.

        NOTE: For backward compatibility, uses the same salt as email verification.
        This maintains compatibility with existing tokens during the transition period.
        In a future release, this should use a separate salt for additional security.

        Args:
            email: The email address to encode in the token

        Returns:
            A URL-safe token string
        """
        serializer = self._get_serializer()
        # Use same salt as email verification for backward compatibility
        # TODO: In future, use separate salt: f"{self._security_salt}_password_reset"
        token = serializer.dumps(email, salt=self._security_salt)
        self._log_operation("generate_password_reset_token", email=email)
        return token

    def verify_password_reset_token(
        self,
        token: str,
        max_age: int = None
    ) -> ServiceResult[str]:
        """
        Verify a password reset token and extract the email.

        NOTE: Uses same salt as email verification for backward compatibility.

        Args:
            token: The token to verify
            max_age: Maximum token age in seconds (default: PASSWORD_RESET_EXPIRY)

        Returns:
            ServiceResult containing the email if valid, or an error
        """
        if max_age is None:
            max_age = self.PASSWORD_RESET_EXPIRY

        serializer = self._get_serializer()
        # Use same salt as email verification for backward compatibility
        # TODO: In future, use separate salt: f"{self._security_salt}_password_reset"

        try:
            email = serializer.loads(
                token,
                salt=self._security_salt,
                max_age=max_age
            )
            self._log_operation("verify_password_reset_token", email=email, status="success")
            return ServiceResult.success(email)

        except SignatureExpired:
            self.logger.warning("Password reset token expired")
            return ServiceResult.failure(
                ErrorCode.TOKEN_EXPIRED,
                "The password reset link has expired. Please request a new one."
            )

        except BadSignature:
            self.logger.warning("Invalid password reset token signature")
            return ServiceResult.failure(
                ErrorCode.TOKEN_INVALID,
                "Invalid password reset link. Please request a new one."
            )

        except Exception as e:
            self._log_error("verify_password_reset_token", e)
            return ServiceResult.failure(
                ErrorCode.TOKEN_INVALID,
                "Failed to verify token. Please request a new one."
            )

    def generate_csrf_token(self, session_id: str) -> str:
        """
        Generate a CSRF token for API protection.

        Args:
            session_id: The session identifier to bind the token to

        Returns:
            A URL-safe CSRF token string
        """
        serializer = self._get_serializer()
        csrf_salt = f"{self._security_salt}_csrf"
        token = serializer.dumps(session_id, salt=csrf_salt)
        self._log_operation("generate_csrf_token", session_bound=True)
        return token

    def verify_csrf_token(
        self,
        token: str,
        expected_session_id: str,
        max_age: int = None
    ) -> ServiceResult[bool]:
        """
        Verify a CSRF token.

        Args:
            token: The CSRF token to verify
            expected_session_id: The session ID the token should be bound to
            max_age: Maximum token age in seconds (default: CSRF_EXPIRY)

        Returns:
            ServiceResult with True if valid, or an error
        """
        if max_age is None:
            max_age = self.CSRF_EXPIRY

        serializer = self._get_serializer()
        csrf_salt = f"{self._security_salt}_csrf"

        try:
            session_id = serializer.loads(
                token,
                salt=csrf_salt,
                max_age=max_age
            )

            if session_id != expected_session_id:
                self.logger.warning("CSRF token session mismatch")
                return ServiceResult.failure(
                    ErrorCode.TOKEN_INVALID,
                    "Invalid CSRF token."
                )

            return ServiceResult.success(True)

        except SignatureExpired:
            self.logger.warning("CSRF token expired")
            return ServiceResult.failure(
                ErrorCode.TOKEN_EXPIRED,
                "CSRF token expired. Please refresh the page."
            )

        except BadSignature:
            self.logger.warning("Invalid CSRF token signature")
            return ServiceResult.failure(
                ErrorCode.TOKEN_INVALID,
                "Invalid CSRF token."
            )

        except Exception as e:
            self._log_error("verify_csrf_token", e)
            return ServiceResult.failure(
                ErrorCode.TOKEN_INVALID,
                "Failed to verify CSRF token."
            )


# Singleton instance for convenience
_token_service: Optional[TokenService] = None


def get_token_service() -> TokenService:
    """Get the singleton TokenService instance."""
    global _token_service
    if _token_service is None:
        _token_service = TokenService()
    return _token_service
