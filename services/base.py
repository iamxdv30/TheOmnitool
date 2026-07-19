"""
Base Service Module

Provides foundational classes and utilities for the service layer:
- ServiceResult: A Result type for returning success/failure with data
- ServiceError: Standardized error representation
- Error codes matching the API specification
"""

from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional, Any, Dict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ErrorCode(str, Enum):
    """
    Standardized error codes matching the API specification.
    These codes are used in API responses and for error handling.
    """
    # Authentication errors
    AUTH_REQUIRED = "AUTH_REQUIRED"
    AUTH_UNVERIFIED = "AUTH_UNVERIFIED"
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_RATE_LIMITED = "AUTH_RATE_LIMITED"

    # Permission errors
    PERMISSION_DENIED = "PERMISSION_DENIED"

    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RECAPTCHA_FAILED = "RECAPTCHA_FAILED"

    # Token errors
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"

    # Resource errors
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"

    # General errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    EMAIL_SEND_FAILED = "EMAIL_SEND_FAILED"
    DATABASE_ERROR = "DATABASE_ERROR"


@dataclass
class ServiceError:
    """
    Represents an error from a service operation.

    Attributes:
        code: ErrorCode enum value for programmatic handling
        message: Human-readable error message
        details: Optional dict with additional error context
    """
    code: ErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        result = {
            "code": self.code.value,
            "message": self.message
        }
        if self.details:
            result["details"] = self.details
        return result

    @property
    def http_status(self) -> int:
        """Return the appropriate HTTP status code for this error."""
        status_map = {
            ErrorCode.AUTH_REQUIRED: 401,
            ErrorCode.AUTH_INVALID_CREDENTIALS: 401,
            ErrorCode.AUTH_UNVERIFIED: 403,
            ErrorCode.AUTH_RATE_LIMITED: 429,
            ErrorCode.PERMISSION_DENIED: 403,
            ErrorCode.VALIDATION_ERROR: 400,
            ErrorCode.RECAPTCHA_FAILED: 400,
            ErrorCode.TOKEN_EXPIRED: 400,
            ErrorCode.TOKEN_INVALID: 400,
            ErrorCode.RESOURCE_NOT_FOUND: 404,
            ErrorCode.RESOURCE_ALREADY_EXISTS: 409,
            ErrorCode.EMAIL_SEND_FAILED: 500,
            ErrorCode.DATABASE_ERROR: 500,
            ErrorCode.INTERNAL_ERROR: 500,
        }
        return status_map.get(self.code, 500)


@dataclass
class ServiceResult(Generic[T]):
    """
    A Result type that encapsulates either success data or an error.

    This pattern:
    - Makes error handling explicit
    - Avoids throwing exceptions for expected failures
    - Provides type safety for return values

    Usage:
        # Success case
        result = ServiceResult.success(user)

        # Error case
        result = ServiceResult.failure(
            ErrorCode.AUTH_INVALID_CREDENTIALS,
            "Invalid username or password"
        )

        # Checking result
        if result.is_success:
            user = result.data
        else:
            error = result.error
    """
    _data: Optional[T] = None
    _error: Optional[ServiceError] = None

    @property
    def is_success(self) -> bool:
        """Returns True if the operation was successful."""
        return self._error is None

    @property
    def is_failure(self) -> bool:
        """Returns True if the operation failed."""
        return self._error is not None

    @property
    def data(self) -> Optional[T]:
        """Returns the success data. None if operation failed."""
        return self._data

    @property
    def error(self) -> Optional[ServiceError]:
        """Returns the error. None if operation succeeded."""
        return self._error

    @classmethod
    def success(cls, data: T = None) -> 'ServiceResult[T]':
        """Create a successful result with optional data."""
        return cls(_data=data, _error=None)

    @classmethod
    def failure(
        cls,
        code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> 'ServiceResult[T]':
        """Create a failure result with an error."""
        error = ServiceError(code=code, message=message, details=details)
        return cls(_data=None, _error=error)

    @classmethod
    def from_error(cls, error: ServiceError) -> 'ServiceResult[T]':
        """Create a failure result from an existing ServiceError."""
        return cls(_data=None, _error=error)

    def to_api_response(self) -> Dict[str, Any]:
        """
        Convert to the standard API response format.

        Success:
            {"success": true, "data": {...}}

        Error:
            {"success": false, "error": {"code": "...", "message": "..."}}
        """
        if self.is_success:
            response = {"success": True}
            if self._data is not None:
                # Handle different data types
                if hasattr(self._data, 'to_dict'):
                    response["data"] = self._data.to_dict()
                elif isinstance(self._data, dict):
                    response["data"] = self._data
                else:
                    response["data"] = self._data
            else:
                response["data"] = None
            return response
        else:
            return {
                "success": False,
                "error": self._error.to_dict()
            }


class BaseService:
    """
    Base class for all services.

    Provides common functionality:
    - Logging setup
    - Database session access
    - Common error handling patterns
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def _log_operation(self, operation: str, **context):
        """Log a service operation with context."""
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        self.logger.info(f"{operation}: {context_str}")

    def _log_error(self, operation: str, error: Exception, **context):
        """Log a service error with context."""
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        self.logger.error(f"{operation} failed: {error} | {context_str}")

    def _handle_db_error(self, operation: str, error: Exception) -> ServiceResult:
        """Handle database errors uniformly."""
        self._log_error(operation, error)
        return ServiceResult.failure(
            ErrorCode.DATABASE_ERROR,
            "A database error occurred. Please try again."
        )
