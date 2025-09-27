"""
Authentication Configuration Module
Centralizes authentication-related settings and validation rules
"""

import os
import re
from typing import Dict, List, Tuple

class AuthConfig:
    """Authentication Configuration and validation rules"""
    
    # Password policy configuration
    MIN_PASSWORD_LENGTH = int(os.getenv("MIN_PASSWORD_LENGTH", 8))
    PASSWORD_REQUIRE_UPPERCASE = os.getenv("PASSWORD_REQUIRE_UPPERCASE", 'true').lower() == "true"
    PASSWORD_REQUIRE_LOWERCASE = os.getenv("PASSWORD_REQUIRE_LOWERCASE", 'true').lower() == "true"
    PASSWORD_REQUIRE_SPECIAL = os.getenv("PASSWORD_REQUIRE_SPECIAL", 'true').lower() == "true"
    PASSWORD_REQUIRE_NUMBER = os.getenv("PASSWORD_REQUIRE_NUMBER", 'true').lower() == "true"

    # Special characters allowed in passwords
    SPECIAL_CHARACTERS = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # Captcha configuration
    RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY')
    RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
    RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

    # OAuth configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

    # Email verification settings
    EMAIL_VERIFICATION_EXPIRY = 3600  # 1 hour

    @classmethod
    def validate_password(cls, password: str) -> Tuple[bool, List[str]]:
        """ Validate password against policy requirements 
        
        Args:
            password: Password to validate
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if len(password) < cls.MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_PASSWORD_LENGTH} characters long.")

        if cls.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter.")

        if cls.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter.")

        if cls.PASSWORD_REQUIRE_SPECIAL and not re.search(f'[{re.escape(cls.SPECIAL_CHARACTERS)}]', password):
            errors.append(f"Password must contain at least one special character ({cls.SPECIAL_CHARACTERS[:10]}...)")

        if cls.PASSWORD_REQUIRE_NUMBER and not re.search(r'\d', password):
            errors.append("Password must contain at least one number.")

        return len(errors) == 0, errors
        

    @classmethod
    def get_password_requirements(cls) -> str:
        """ Get a human-readable string of password requirements """
        requirements = [f"At least {cls.MIN_PASSWORD_LENGTH} characters long"]

        if cls.PASSWORD_REQUIRE_UPPERCASE:
            requirements.append("At least 1 uppercase letter")

        if cls.PASSWORD_REQUIRE_LOWERCASE:
            requirements.append("At least 1 lowercase letter")

        if cls.PASSWORD_REQUIRE_NUMBER:
            requirements.append("At least 1 number")
        
        if cls.PASSWORD_REQUIRE_SPECIAL:
            requirements.append(f"At least 1 special character ({cls.SPECIAL_CHARACTERS[:10]}...)")
        
        return " • ".join(requirements)

    @classmethod
    def is_captcha_enabled(cls) -> bool:
        """ Check if captcha is enabled """
        return bool(cls.RECAPTCHA_SITE_KEY and cls.RECAPTCHA_SECRET_KEY)

