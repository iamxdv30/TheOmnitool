from flask import Blueprint, request, jsonify, render_template, url_for, current_app
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from dotenv import load_dotenv
load_dotenv()


# Verify environment variables
required_env_vars = [
    "MAIL_USERNAME",
    "MAIL_PASSWORD",
    "MAIL_DEFAULT_SENDER",
    "TOKEN_SECRET_KEY",
    "SECURITY_PASSWORD_SALT"
]

for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f"Missing required environment variable: {var}")


# Create a Blueprint for the contact route
contact = Blueprint("contact", __name__)

# Configure Flask-Mail
mail = Mail()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def configure_mail(app):
    # Set Gmail configuration
    app.config.update(
        MAIL_SERVER="smtp.gmail.com",
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER")
    )
    # Log mail configuration (without sensitive data)
    logger.info(f"Mail configured with username: {os.getenv('MAIL_USERNAME')}")
    mail.init_app(app)
# Generate a secure token for email verification
def generate_verification_token(email):
    token_secret_key = os.getenv("TOKEN_SECRET_KEY")  # Use TOKEN_SECRET_KEY instead of SECRET_KEY

    if not token_secret_key:
        raise ValueError("TOKEN_SECRET_KEY is not set or is empty. Please set it in the environment variables.")

    serializer = URLSafeTimedSerializer(token_secret_key)
    salt = os.getenv("SECURITY_PASSWORD_SALT")

    if not salt:
        raise ValueError("SECURITY_PASSWORD_SALT is not set or is empty. Please set it in the environment variables.")

    return serializer.dumps(email, salt=salt)

# Verify the token to confirm the user's email
def verify_verification_token(token, expiration=3600):
    token_secret_key = os.getenv("TOKEN_SECRET_KEY")  # Use TOKEN_SECRET_KEY instead of SECRET_KEY

    if not token_secret_key:
        raise ValueError("TOKEN_SECRET_KEY is not set or is empty. Please set it in the environment variables.")

    serializer = URLSafeTimedSerializer(token_secret_key)
    salt = os.getenv("SECURITY_PASSWORD_SALT")

    if not salt:
        raise ValueError("SECURITY_PASSWORD_SALT is not set or is empty. Please set it in the environment variables.")

    try:
        email = serializer.loads(token, salt=salt, max_age=expiration)
    except Exception:
        return None
    return email

# Route to display the contact form
@contact.route("/contact", methods=["GET"])
def contact_page():
    return render_template("contact.html")

# Define the contact route that handles form submissions
@contact.route("/contact", methods=["POST"])
def handle_contact():
    # Get the form data
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    query_type = data.get("query_type")
    message_content = data.get("message")

    # Validate required fields
    if not name or not email or not message_content:
        return jsonify({"message": "All fields are required."}), 400

    try:
        # Format the sender as "Name <email>" which is the correct format for Flask-Mail
        default_sender = os.getenv('MAIL_DEFAULT_SENDER')
        formatted_sender = f"{name} <{default_sender}>"

        # Create an email message with the contact form details
        msg = Message(
            subject=f"New {query_type.capitalize()} Query from {name}",
            sender=formatted_sender,  # Using the correctly formatted sender string
            recipients=[os.getenv("MAIL_USERNAME", "info.omnitools@gmail.com")],
            body=f"Name: {name}\nEmail: {email}\nQuery Type: {query_type}\nMessage:\n{message_content}",
            reply_to=email
        )
        mail.send(msg)

        return jsonify({"message": "Message sent successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"Failed to send message: {str(e)}"}), 500

# Route to handle email verification when the user clicks the verification link
@contact.route("/verify/<token>")
def verify_email(token):
    email = verify_verification_token(token)
    if email:
        return f"Email {email} verified successfully! You can now submit your query.", 200
    else:
        return "Invalid or expired token.", 400

# Route to send the verification email
@contact.route("/contact/verify-email", methods=["POST"])
def verify_email_request():
    try:
        data = request.get_json()
        email = data.get("email")
        name = data.get("name")

        if not email or not name:
            return jsonify({"message": "Email and name are required."}), 400

        # Log the verification request
        logger.info(f"Email verification requested for: {email}")

        # Generate token and verification link
        token = generate_verification_token(email)
        verification_link = url_for("contact.verify_email", token=token, _external=True)

        # Create email message
        msg = Message(
            subject="Verify Your Email - OmniTools",
            sender=os.getenv("MAIL_DEFAULT_SENDER"),
            recipients=[email]
        )

        # Render HTML template
        msg.html = render_template(
            'email/email_verification.html',
            name=name,
            verification_link=verification_link
        )

        # Set plain text fallback
        msg.body = f"""
Hi {name},

Please verify your email for OmniTools by visiting this link:
{verification_link}

If you didn't request this verification, please ignore this email.

© 2024 OmniTools. All rights reserved.
"""

        mail.send(msg)
        logger.info(f"Verification email sent successfully to: {email}")
        return jsonify({"message": "Verification email sent. Please check your email."}), 200

    except smtplib.SMTPException as smtp_error:
        logger.error(f"SMTP Error sending to {email}: {str(smtp_error)}")
        return jsonify({"message": "Email server error. Please try again later."}), 500
    except Exception as e:
        logger.error(f"Unexpected error sending to {email}: {str(e)}")
        return jsonify({"message": "Failed to send verification email"}), 500
