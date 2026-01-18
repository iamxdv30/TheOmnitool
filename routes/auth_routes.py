"""
Authentication Routes Module

Handles HTTP requests for authentication operations.
Business logic is delegated to AuthService.

Routes:
- /login - User login
- /logout - User logout
- /register - New user registration
- /verify_email/<token> - Email verification
- /verification_pending - Pending verification page
- /resend_verification - Resend verification email
- /forgot_password - Request password reset
- /reset_password/<token> - Reset password with token
"""

from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from functools import wraps
import logging

from config.auth_config import AuthConfig
from services import get_auth_service, ErrorCode

# Set up logging
logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)


# ==================== Decorators ====================

def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            logger.warning(f"Unauthorized access attempt to {request.endpoint} from IP: {request.remote_addr}")
            flash('Please log in to access this page.', 'error')
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def anonymous_required(f):
    """Decorator to redirect logged-in users away from auth pages."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in'):
            username = session.get('username', 'unknown')
            user_role = session.get('role', 'user')
            logger.info(f"Already logged in user '{username}' ({user_role}) redirected from {request.endpoint}")

            if user_role == 'super_admin':
                return redirect(url_for('admin.superadmin_dashboard'))
            elif user_role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('user.user_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== Helper Functions ====================

def _get_client_ip():
    """Get client IP address from request."""
    return request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)


def _set_user_session(user_profile):
    """Set up user session after successful login/verification."""
    session["logged_in"] = True
    session["username"] = user_profile.username
    session["role"] = user_profile.role
    session["user_id"] = user_profile.id
    session["user_tools"] = user_profile.tools


def _get_redirect_route(role):
    """Get the appropriate redirect route based on user role."""
    if role == "super_admin":
        return url_for("admin.superadmin_dashboard")
    elif role == "admin":
        return url_for("admin.admin_dashboard")
    else:
        return url_for("user.user_dashboard")


def _render_login_page(error_message=None):
    """Render the login page with captcha config."""
    if error_message:
        flash(error_message, "error")
    return render_template(
        "login.html",
        captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
        captcha_enabled=AuthConfig.is_captcha_enabled()
    )


def _render_register_page(error_message=None, form_data=None):
    """Render the registration page with form data."""
    if error_message:
        flash(error_message, "error")
    return render_template(
        "register.html",
        captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
        captcha_enabled=AuthConfig.is_captcha_enabled(),
        password_requirements=AuthConfig.get_password_requirements_text(),
        form_data=form_data or {}
    )


# ==================== Routes ====================

@auth.route("/login", methods=["GET", "POST"])
@anonymous_required
def login():
    """
    Handle user login.
    GET: Display login form
    POST: Process login credentials
    """
    client_ip = _get_client_ip()

    if request.method == "GET":
        logger.info(f"Login page accessed from IP: {client_ip}")
        session.pop('_flashes', None)  # Clear flash messages for GET
        return _render_login_page()

    # POST request - process login
    logger.info(f"Login attempt initiated from IP: {client_ip}")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    recaptcha_response = request.form.get("g-recaptcha-response", "")

    # Use auth service for login
    auth_service = get_auth_service()
    result = auth_service.login(
        username=username,
        password=password,
        recaptcha_response=recaptcha_response,
        client_ip=client_ip
    )

    if result.is_failure:
        error = result.error

        # Handle unverified email - redirect to verification pending
        if error.code == ErrorCode.AUTH_UNVERIFIED:
            session['pending_verification_email'] = error.details.get('email')
            session['pending_verification_name'] = error.details.get('name')
            flash(error.message, "error")
            return redirect(url_for("auth.verification_pending"))

        # Handle other errors - stay on login page
        return _render_login_page(error.message)

    # Success - set up session and redirect
    login_result = result.data
    _set_user_session(login_result.user)

    logger.info(f"LOGIN SUCCESS: User '{username}' logged in from IP: {client_ip}")
    return redirect(_get_redirect_route(login_result.user.role))


@auth.route("/verify_email/<token>")
def verify_email(token):
    """
    Email verification route.
    Automatically logs user in after successful verification.
    """
    client_ip = _get_client_ip()
    logger.info(f"Email verification attempted from IP: {client_ip}")

    auth_service = get_auth_service()
    result = auth_service.verify_email(token)

    if result.is_failure:
        error = result.error
        flash(error.message, "error")

        if error.code == ErrorCode.RESOURCE_NOT_FOUND:
            return redirect(url_for("auth.register"))
        return redirect(url_for("auth.login"))

    # Success - set up session and redirect
    user_profile = result.data

    # Clear pending verification from session
    session.pop('pending_verification_email', None)
    session.pop('pending_verification_name', None)

    # Set up session (auto-login)
    _set_user_session(user_profile)

    logger.info(f"EMAIL VERIFICATION + AUTO-LOGIN SUCCESS: User '{user_profile.username}' from IP: {client_ip}")
    flash("Email verified successfully! Welcome to OmniTools!", "success")

    return redirect(_get_redirect_route(user_profile.role))


@auth.route("/verification_pending")
def verification_pending():
    """Show verification pending page after registration."""
    client_ip = _get_client_ip()
    logger.info(f"Verification pending page accessed from IP: {client_ip}")

    user_email = session.get('pending_verification_email')
    user_name = session.get('pending_verification_name')

    if not user_email:
        logger.warning("Verification pending page accessed without email in session")
        flash("Registration session expired. Please register again.", "error")
        return redirect(url_for("auth.register"))

    logger.info(f"Showing verification pending page for: {user_email}")
    return render_template(
        "auth/verification_pending.html",
        email=user_email,
        name=user_name
    )


@auth.route("/resend_verification", methods=["POST"])
def resend_verification():
    """Resend email verification."""
    client_ip = _get_client_ip()
    logger.info(f"Resend verification request from IP: {client_ip}")

    email = session.get('pending_verification_email')
    if not email:
        logger.warning("Resend verification attempted without email in session")
        flash("No pending verification found. Please register again.", "error")
        return redirect(url_for("auth.register"))

    auth_service = get_auth_service()
    result = auth_service.resend_verification_email(email)

    if result.is_failure:
        error = result.error

        if error.code == ErrorCode.RESOURCE_NOT_FOUND:
            flash("User account not found. Please register again.", "error")
            return redirect(url_for("auth.register"))

        # Already verified case
        if error.code == ErrorCode.VALIDATION_ERROR and "already verified" in error.message.lower():
            flash(error.message, "success")
            return redirect(url_for("auth.login"))

        flash(error.message, "error")
        return redirect(url_for("auth.verification_pending"))

    flash("A new verification link has been sent to your email address.", "success")
    return redirect(url_for("auth.verification_pending"))


@auth.route("/register", methods=["GET", "POST"])
@anonymous_required
def register():
    """
    Handle user registration.
    GET: Display registration form
    POST: Process registration
    """
    client_ip = _get_client_ip()

    if request.method == "GET":
        logger.info(f"Registration page accessed from IP: {client_ip}")
        return _render_register_page()

    # POST request - process registration
    logger.info(f"Registration attempt initiated from IP: {client_ip}")

    # Get form data
    name = request.form.get('name', '').strip()
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    recaptcha_response = request.form.get('g-recaptcha-response', '')

    form_data = {'name': name, 'username': username, 'email': email}

    # Use auth service for registration
    auth_service = get_auth_service()
    result = auth_service.register(
        name=name,
        username=username,
        email=email,
        password=password,
        confirm_password=confirm_password,
        recaptcha_response=recaptcha_response,
        client_ip=client_ip
    )

    if result.is_failure:
        return _render_register_page(result.error.message, form_data)

    # Success - redirect to verification pending
    reg_result = result.data
    session['pending_verification_email'] = reg_result.email
    session['pending_verification_name'] = reg_result.name

    logger.info(f"REGISTRATION SUCCESS: User '{username}' ({email}) registered from IP: {client_ip}")

    if not reg_result.verification_email_sent:
        flash("Registration successful, but we couldn't send the verification email. Please contact support.", "warning")
        return redirect(url_for("auth.login"))

    return redirect(url_for("auth.verification_pending"))


@auth.route("/logout", methods=["GET", "POST"])
def logout():
    """Clean logout implementation."""
    username = session.get('username', 'unknown')
    client_ip = _get_client_ip()

    logger.info(f"Logout initiated for user: '{username}' from IP: {client_ip}")

    session.clear()
    session.pop('_flashes', None)

    logger.info(f"LOGOUT SUCCESS: User '{username}' logged out successfully")
    return redirect(url_for("auth.login"))


@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    """Handle password reset requests."""
    client_ip = _get_client_ip()

    if request.method == "GET":
        logger.info(f"Forgot password page accessed from IP: {client_ip}")
        return render_template("forgot_password_request.html")

    logger.info(f"Password reset request initiated from IP: {client_ip}")

    email = request.form.get("email", "").strip()

    auth_service = get_auth_service()
    auth_service.request_password_reset(email)

    # For security, always flash the same message
    flash("If an account with that email exists, a password reset link has been sent.", "info")
    return redirect(url_for("auth.login"))


@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Handle password reset."""
    client_ip = _get_client_ip()
    logger.info(f"Password reset page accessed from IP: {client_ip}")

    auth_service = get_auth_service()

    # Validate token first
    token_result = auth_service.validate_reset_token(token)
    if token_result.is_failure:
        flash(token_result.error.message, "error")
        return redirect(url_for("auth.login"))

    if request.method == "GET":
        logger.info(f"Showing password reset form for: {token_result.data}")
        return render_template("reset_password.html", token=token)

    # POST - process password reset
    logger.info(f"Processing password reset for email: '{token_result.data}'")

    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    result = auth_service.reset_password(
        token=token,
        new_password=password,
        confirm_password=confirm_password
    )

    if result.is_failure:
        flash(result.error.message, "error")
        return render_template("reset_password.html", token=token)

    logger.info(f"PASSWORD RESET SUCCESS from IP: {client_ip}")
    flash("Password reset successful! You can now log in.", "success")
    return redirect(url_for("auth.login"))


@auth.route("/forgot_password_request", methods=["GET", "POST"])
def forgot_password_request():
    """Alternative forgot password route for backward compatibility."""
    return forgot_password()
