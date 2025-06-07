# Import everything to maintain backward compatibility
from .base import db, PasswordHasher, BcryptPasswordHasher
from .users import User, Admin, SuperAdmin
from .tools import UsageLog, EmailTemplate, ToolAccess, Tool
from .auth import UserFactory

# This allows existing imports like "from model.model import User" to still work
__all__ = [
    'db',
    'PasswordHasher', 
    'BcryptPasswordHasher',
    'User', 
    'Admin', 
    'SuperAdmin',
    'UsageLog', 
    'EmailTemplate', 
    'ToolAccess', 
    'Tool',
    'UserFactory'
]