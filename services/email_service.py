"""
Email Service Module

Centralizes all email sending operations:
- Email verification emails
- Password reset emails
- Contact form emails

This replaces the scattered email logic in auth_routes.py and contact_routes.py.
"""

import os
import logging
from typing import Optional
from dataclasses import dataclass

from flask import render_template, url_for
from flask_mail import Mail, Message

from .base import BaseService, ServiceResult, ErrorCode
from .token_service import get_token_service

logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """Email configuration loaded from environment."""
    mail_server: str
    mail_port: int
    mail_use_tls: bool
    mail_username: str
    mail_password: str
    mail_default_sender: str

    @classmethod
    def from_env(cls) -> 'EmailConfig':
        """Load configuration from environment variables."""
        return cls(
            mail_server=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
            mail_port=int(os.getenv("MAIL_PORT", "587")),
            mail_use_tls=os.getenv("MAIL_USE_TLS", "True").lower() == "true",
            mail_username=os.getenv("MAIL_USERNAME", ""),
            mail_password=os.getenv("MAIL_PASSWORD", ""),
            mail_default_sender=os.getenv("MAIL_DEFAULT_SENDER", ""),
        )


class EmailService(BaseService):
    """
    Service for sending emails.

    Provides methods for all email types used in the application.
    """

    def __init__(self, mail: Mail = None):
        """
        Initialize the email service.

        Args:
            mail: Flask-Mail instance. If None, must be set via set_mail()
        """
        super().__init__()
        self._mail = mail
        self._config = EmailConfig.from_env()
        self._token_service = get_token_service()

    def set_mail(self, mail: Mail):
        """Set the Flask-Mail instance (used during app initialization)."""
        self._mail = mail

    def _ensure_mail(self):
        """Ensure mail is configured."""
        if self._mail is None:
            raise RuntimeError(
                "EmailService.mail is not set. "
                "Call set_mail() with Flask-Mail instance first."
            )

    def send_verification_email(
        self,
        email: str,
        user_name: str
    ) -> ServiceResult[bool]:
        """
        Send email verification email to a new user.

        Args:
            email: User's email address
            user_name: User's display name

        Returns:
            ServiceResult with True if sent successfully
        """
        self._ensure_mail()
        self._log_operation("send_verification_email", email=email, name=user_name)

        try:
            # Generate verification token
            token = self._token_service.generate_email_verification_token(email)
            verification_link = url_for("auth.verify_email", token=token, _external=True)

            # Create message
            msg = Message(
                subject="Verify Your Email - OmniTools Registration",
                recipients=[email],
            )

            # Render HTML template
            msg.html = render_template(
                "email/registration_verfication.html",
                name=user_name,
                verification_link=verification_link,
            )

            # Plain text fallback
            msg.body = f"""
Hi {user_name},

Welcome to OmniTools! Please verify your email address by clicking this link:
{verification_link}

This link will expire in 1 hour for security.

If you didn't create an account, please ignore this email.

(c) 2024 OmniTools. All rights reserved.
"""

            self._mail.send(msg)
            self.logger.info(f"Verification email sent successfully to: {email}")
            return ServiceResult.success(True)

        except Exception as e:
            self._log_error("send_verification_email", e, email=email)
            return ServiceResult.failure(
                ErrorCode.EMAIL_SEND_FAILED,
                "Failed to send verification email. Please try again later."
            )

    def send_password_reset_email(
        self,
        email: str,
        user_name: str
    ) -> ServiceResult[bool]:
        """
        Send password reset email.

        Args:
            email: User's email address
            user_name: User's display name

        Returns:
            ServiceResult with True if sent successfully
        """
        self._ensure_mail()
        self._log_operation("send_password_reset_email", email=email)

        try:
            # Generate reset token
            token = self._token_service.generate_password_reset_token(email)
            reset_link = url_for("auth.reset_password", token=token, _external=True)

            # Create message
            msg = Message(
                subject="Password Reset Request - OmniTools",
                recipients=[email],
            )

            # HTML content
            msg.html = f"""
<h2>Password Reset Request</h2>
<p>Hello {user_name},</p>
<p>You requested a password reset. Click the link below to reset your password:</p>
<p><a href="{reset_link}">Reset Password</a></p>
<p>This link will expire in 1 hour for security.</p>
<p>If you didn't request this reset, please ignore this email.</p>
<p>&copy; 2026 OmniTools. All rights reserved.</p>
"""

            # Plain text fallback
            msg.body = f"""
Hello {user_name},

You requested a password reset. Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour for security.

If you didn't request this reset, please ignore this email.

(c) 2026 OmniTools. All rights reserved.
"""

            self._mail.send(msg)
            self.logger.info(f"Password reset email sent successfully to: {email}")
            return ServiceResult.success(True)

        except Exception as e:
            self._log_error("send_password_reset_email", e, email=email)
            return ServiceResult.failure(
                ErrorCode.EMAIL_SEND_FAILED,
                "Failed to send password reset email. Please try again later."
            )

    def send_contact_form_email(
        self,
        name: str,
        email: str,
        query_type: str,
        message: str
    ) -> ServiceResult[bool]:
        """
        Send contact form submission email.

        Args:
            name: Sender's name
            email: Sender's email
            query_type: Type of query (general, support, etc.)
            message: The message content

        Returns:
            ServiceResult with True if sent successfully
        """
        self._ensure_mail()
        self._log_operation("send_contact_form_email", from_email=email, query_type=query_type)

        try:
            # Format sender as "Name <default_sender>" for proper delivery
            formatted_sender = f"{name} <{self._config.mail_default_sender}>"
            recipient = os.getenv("MAIL_USERNAME", "info.omnitools@gmail.com")

            msg = Message(
                subject=f"New {query_type.capitalize()} Query from {name}",
                sender=formatted_sender,
                recipients=[recipient],
                body=f"Name: {name}\nEmail: {email}\nQuery Type: {query_type}\nMessage:\n{message}",
                reply_to=email,
            )

            self._mail.send(msg)
            self.logger.info(f"Contact form email sent from: {email}")
            return ServiceResult.success(True)

        except Exception as e:
            self._log_error("send_contact_form_email", e, email=email)
            return ServiceResult.failure(
                ErrorCode.EMAIL_SEND_FAILED,
                "Failed to send message. Please try again later."
            )

    def send_contact_verification_email(
        self,
        email: str,
        name: str
    ) -> ServiceResult[bool]:
        """
        Send verification email for contact form (not registration).

        This is different from registration verification - it's for
        verifying email before submitting contact form.

        Args:
            email: Email to verify
            name: User's name

        Returns:
            ServiceResult with True if sent successfully
        """
        self._ensure_mail()
        self._log_operation("send_contact_verification_email", email=email)

        try:
            # Generate token
            token = self._token_service.generate_email_verification_token(email)
            verification_link = url_for("contact.verify_email", token=token, _external=True)

            msg = Message(
                subject="Verify Your Email - OmniTools",
                sender=self._config.mail_default_sender,
                recipients=[email],
            )

            # Render HTML template
            msg.html = render_template(
                "email/email_verification.html",
                name=name,
                verification_link=verification_link,
            )

            # Plain text fallback
            msg.body = f"""
Hi {name},

Please verify your email for OmniTools by visiting this link:
{verification_link}

If you didn't request this verification, please ignore this email.

(c) 2024 OmniTools. All rights reserved.
"""

            self._mail.send(msg)
            self.logger.info(f"Contact verification email sent to: {email}")
            return ServiceResult.success(True)

        except Exception as e:
            self._log_error("send_contact_verification_email", e, email=email)
            return ServiceResult.failure(
                ErrorCode.EMAIL_SEND_FAILED,
                "Failed to send verification email. Please try again later."
            )


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get the singleton EmailService instance."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service


def init_email_service(mail: Mail) -> EmailService:
    """
    Initialize the email service with Flask-Mail.

    Call this during app initialization after Flask-Mail is configured.

    Args:
        mail: Configured Flask-Mail instance

    Returns:
        The initialized EmailService
    """
    global _email_service
    _email_service = EmailService(mail)
    return _email_service
