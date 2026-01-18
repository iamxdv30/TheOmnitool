# Services Package
# Business logic layer following the Service Layer pattern
# This separates HTTP concerns (routes) from business logic (services)

from .base import ServiceResult, ServiceError, ErrorCode, BaseService
from .token_service import TokenService, get_token_service
from .email_service import EmailService, get_email_service, init_email_service
from .auth_service import AuthService, get_auth_service, UserProfile, LoginResult, RegistrationResult
from .user_service import UserService, get_user_service, UserProfileData, DashboardData
from .tool_service import ToolService, get_tool_service, ToolInfo, EmailTemplateData

__all__ = [
    # Base classes and utilities
    'ServiceResult',
    'ServiceError',
    'ErrorCode',
    'BaseService',

    # Token Service
    'TokenService',
    'get_token_service',

    # Email Service
    'EmailService',
    'get_email_service',
    'init_email_service',

    # Auth Service
    'AuthService',
    'get_auth_service',
    'UserProfile',
    'LoginResult',
    'RegistrationResult',

    # User Service
    'UserService',
    'get_user_service',
    'UserProfileData',
    'DashboardData',

    # Tool Service
    'ToolService',
    'get_tool_service',
    'ToolInfo',
    'EmailTemplateData',
]
