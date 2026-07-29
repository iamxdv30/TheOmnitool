"""
API Validation Schemas

Marshmallow schemas for validating API request payloads.
These ensure input data conforms to expected formats before
being processed by services.
"""

from marshmallow import Schema, fields, validate, validates, ValidationError


# ==================== Auth Schemas ====================

class LoginSchema(Schema):
    """Schema for login request."""
    username = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={"required": "Username is required."}
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "Password is required."}
    )
    recaptcha_token = fields.Str(
        load_default=None,
        allow_none=True
    )


class RegisterSchema(Schema):
    """Schema for registration request."""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={"required": "Name is required."}
    )
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=50),
            validate.Regexp(
                r'^[a-zA-Z0-9_]+$',
                error="Username can only contain letters, numbers, and underscores."
            )
        ],
        error_messages={"required": "Username is required."}
    )
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Invalid email address."
        }
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        error_messages={
            "required": "Password is required.",
            "validator_failed": "Password must be at least 8 characters."
        }
    )
    confirm_password = fields.Str(
        required=True,
        error_messages={"required": "Password confirmation is required."}
    )
    recaptcha_token = fields.Str(
        load_default=None,
        allow_none=True
    )

    @validates('confirm_password')
    def validate_confirm_password(self, value):
        """Validate passwords match during load."""
        # Note: This runs per-field, cross-field validation done in service
        pass


class ForgotPasswordSchema(Schema):
    """Schema for forgot password request."""
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Invalid email address."
        }
    )
    recaptcha_token = fields.Str(
        load_default=None,
        allow_none=True
    )


class ResetPasswordSchema(Schema):
    """Schema for password reset request."""
    token = fields.Str(
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "Reset token is required."}
    )
    new_password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        error_messages={
            "required": "New password is required.",
            "validator_failed": "Password must be at least 8 characters."
        }
    )
    confirm_password = fields.Str(
        required=True,
        error_messages={"required": "Password confirmation is required."}
    )


class ResendVerificationSchema(Schema):
    """Schema for resend verification request."""
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Invalid email address."
        }
    )
    recaptcha_token = fields.Str(
        load_default=None,
        allow_none=True
    )


class ValidateTokenSchema(Schema):
    """Schema for token validation request."""
    token = fields.Str(
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "Token is required."}
    )


# ==================== User Schemas ====================

class UpdateProfileSchema(Schema):
    """Schema for profile update request."""
    name = fields.Str(
        load_default=None,
        validate=validate.Length(max=100)
    )
    fname = fields.Str(
        load_default=None,
        validate=validate.Length(max=50)
    )
    lname = fields.Str(
        load_default=None,
        validate=validate.Length(max=50)
    )
    address = fields.Str(
        load_default=None,
        validate=validate.Length(max=200)
    )
    city = fields.Str(
        load_default=None,
        validate=validate.Length(max=100)
    )
    state = fields.Str(
        load_default=None,
        validate=validate.Length(max=50)
    )
    zip = fields.Str(
        load_default=None,
        validate=validate.Length(max=20)
    )


class ChangePasswordSchema(Schema):
    """Schema for password change request."""
    current_password = fields.Str(
        required=True,
        error_messages={"required": "Current password is required."}
    )
    new_password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        error_messages={
            "required": "New password is required.",
            "validator_failed": "Password must be at least 8 characters."
        }
    )
    confirm_password = fields.Str(
        required=True,
        error_messages={"required": "Password confirmation is required."}
    )


class UpdateEmailSchema(Schema):
    """Schema for email update request."""
    new_email = fields.Email(
        required=True,
        error_messages={
            "required": "New email is required.",
            "invalid": "Invalid email address."
        }
    )
    current_password = fields.Str(
        required=True,
        error_messages={"required": "Current password is required."}
    )


# ==================== Tool Schemas ====================

class TaxItemSchema(Schema):
    """Schema for a tax calculation item."""
    price = fields.Float(
        required=True,
        validate=validate.Range(min=0),
        error_messages={"required": "Item price is required."}
    )
    tax_rate = fields.Float(
        load_default=0,
        validate=validate.Range(min=0, max=100)
    )


class TaxDiscountSchema(Schema):
    """Schema for a discount."""
    amount = fields.Float(
        required=True,
        validate=validate.Range(min=0),
        error_messages={"required": "Discount amount is required."}
    )
    type = fields.Str(
        load_default="fixed",
        validate=validate.OneOf(["fixed", "percentage"])
    )


class TaxOptionsSchema(Schema):
    """Schema for tax calculation options."""
    is_sales_before_tax = fields.Bool(load_default=False)
    discount_is_taxable = fields.Bool(load_default=True)


class TaxCalculationSchema(Schema):
    """Schema for tax calculation request."""
    calculator_type = fields.Str(
        required=True,
        validate=validate.OneOf(["us", "canada", "vat"]),
        error_messages={
            "required": "Calculator type is required.",
            "validator_failed": "Must be 'us', 'canada', or 'vat'."
        }
    )
    items = fields.List(
        fields.Nested(TaxItemSchema),
        load_default=[]
    )
    discounts = fields.List(
        fields.Nested(TaxDiscountSchema),
        load_default=[]
    )
    shipping_cost = fields.Float(
        load_default=0,
        validate=validate.Range(min=0)
    )
    shipping_taxable = fields.Bool(load_default=False)
    shipping_tax_rate = fields.Float(
        load_default=0,
        validate=validate.Range(min=0, max=100)
    )
    # Canada-specific
    gst_rate = fields.Float(
        load_default=0,
        validate=validate.Range(min=0, max=100)
    )
    pst_rate = fields.Float(
        load_default=0,
        validate=validate.Range(min=0, max=100)
    )
    # VAT-specific
    vat_rate = fields.Float(
        load_default=0,
        validate=validate.Range(min=0, max=100)
    )
    options = fields.Nested(TaxOptionsSchema, load_default=TaxOptionsSchema().load({}))


class CharacterCountSchema(Schema):
    """Schema for character count request."""
    text = fields.Str(
        required=True,
        error_messages={"required": "Text is required."}
    )
    char_limit = fields.Int(
        load_default=3532,
        validate=validate.Range(min=1)
    )


class EmailTemplateSchema(Schema):
    """Schema for email template create/update."""
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200),
        error_messages={"required": "Title is required."}
    )
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "Content is required."}
    )


# ==================== Validation Helper ====================

def validate_request(schema_class, data):
    """
    Validate request data against a schema.

    Args:
        schema_class: Marshmallow schema class
        data: Dictionary of request data

    Returns:
        Tuple of (validated_data, errors)
        - If valid: (dict, None)
        - If invalid: (None, dict of errors)
    """
    schema = schema_class()
    try:
        validated = schema.load(data)
        return validated, None
    except ValidationError as err:
        return None, err.messages
