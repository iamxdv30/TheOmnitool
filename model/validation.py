"""
Validation module for authentication and user data
Uses Marshmallow for robust input validation and serialization
"""
import re
import requests
from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from model.model import User
from config.auth_config import AuthConfig
import logging


logger = logging.getLogger(__name__)

def verify_recaptcha(recaptcha_response: str, remote_ip: str = None) -> bool:
    """
    Verify reCAPTCHA response with Google's servers
    
    Args:
        recaptcha_response: The response token from reCAPTCHA
        remote_ip: Optional IP address of the user
        
    Returns:
        Boolean indicating if captcha verification passed
    """
    if not AuthConfig.is_captcha_enabled():
        return True
    
    try:
        data = {
            "secret": AuthConfig.RECAPTCHA_SECRET_KEY,
            "response": recaptcha_response,
        }
        if remote_ip:
            data["remoteip"] = remote_ip
        
        response = requests.post(AuthConfig.RECAPTCHA_VERIFY_URL, data=data, timeout=5)
        result = response.json()
        
        success = result.get("success", False)
        if not success:
            error_codes = result.get("error-codes", [])
            logger.warning(f"Captcha Verification Failed: {error_codes}")

        return success
    
    except Exception as e:
        logger.error(f"Captcha Verification Failed: {str(e)}")
        return False

class PasswordField(fields.String):
    """Custom password field with built-in validation"""
    
    def _validate(self, value, attr, data, **kwargs):
        if value is None:
            return

        is_valid, errors = AuthConfig.validate_password(value)
        if not is_valid:
            raise ValidationError(errors)

class RegistrationSchema(Schema):
    """ Schema for user registration validation """
    
    name = fields.String(
        required=True,
        validate=[
            validate.Length(min=2, max=100, error="Name must be between 2 and 100 characters"),
            validate.Regexp(
                r'^[a-zA-Z\s\'-]+$',
                error="Name can only contain letters, spaces, hyphens, and apostrophes"
            )
        ],
        error_messages={'required': 'Name is required'}
    )
    
    username = fields.String(
        required=True,
        validate=[
            validate.Length(min=3, max=50, error="Username must be between 3 and 50 characters"),
            validate.Regexp(
                r'^[a-zA-Z0-9_]+$',
                error="Username can only contain letters, numbers, and underscores"
            )
        ],
        error_messages={'required': 'Username is required'}
    )
    
    email = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        error_messages={
            'required': 'Email is required',
            'invalid': 'Please enter a valid email address'
        }
    )
    
    password = PasswordField(
        required=True,
        error_messages={'required': 'Password is required'}
    )
    
    confirm_password = fields.String(
        required=True,
        error_messages={'required': 'Password confirmation is required'}
    )
    
    captcha_response = fields.String(
        required=True,
        data_key='g-recaptcha-response',
        error_messages={'required': 'Please complete the captcha'}
    )

    @validates('username')
    def validate_username_unique(self, value):
        """Check if username already exists"""
        if User.query.filter_by(username=value).first():
            raise ValidationError("Username already exists")
    
    @validates('email')
    def validate_email_unique(self, value):
        """Check if email already exists"""
        if User.query.filter_by(email=value).first():
            raise ValidationError("Email already registered")
    
    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        """Ensure password and confirm_password match"""
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError('Passwords do not match', 'confirm_password')
    
    def validate_captcha(self, data, remote_ip=None):
        """Validate captcha response"""
        captcha_response = data.get('captcha_response')
        if not captcha_response:
            raise ValidationError({'captcha_response': ['Please complete the captcha']})
        
        if not verify_recaptcha(captcha_response, remote_ip):
            raise ValidationError({'captcha_response': ['Captcha verification failed. Please try again.']})
        
        return True
class EmailVerificationSchema(Schema):
    """Schema for email verification request"""
    
    email = fields.Email(
        required=True,
        error_messages={
            'required': 'Email is required',
            'invalid': 'Please enter a valid email address'
        }
    )


class PasswordResetSchema(Schema):
    """Schema for password reset"""
    
    password = PasswordField(
        required=True,
        error_messages={'required': 'Password is required'}
    )
    
    confirm_password = fields.String(
        required=True,
        error_messages={'required': 'Password confirmation is required'}
    )
    
    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        """Ensure password and confirm_password match"""
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError('Passwords do not match', 'confirm_password')


# Export commonly used validators
def validate_registration_data(data, remote_ip=None):
    """Validate registration data with captcha"""
    schema = RegistrationSchema()
    try:
        validated_data = schema.load(data)
        schema.validate_captcha(validated_data, remote_ip)
        return validated_data, None
    except ValidationError as e:
        return None, e.messages


def validate_login_data(data, remote_ip=None):
    """Validate login data with captcha"""
    schema = LoginSchema()
    try:
        validated_data = schema.load(data)
        schema.validate_captcha(validated_data, remote_ip)
        return validated_data, None
    except ValidationError as e:
        return None, e.messages