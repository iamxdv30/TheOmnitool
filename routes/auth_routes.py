"""
Complete Enhanced Authentication Routes
Keeps existing templates, adds new functionality:
- Simplified registration with captcha
- Email verification for new users  
- Enhanced login with captcha
- Keeps existing forgot_password/reset_password (they work perfectly)
- Backward compatibility with existing users
"""
import email
from flask import Blueprint, request, jsonify, redirect, url_for, render_template, session, flash, current_app
from model.model import User, db, UserFactory
from model.validation import validate_registration_data, validate_login_data
from werkzeug.security import check_password_hash
from functools import wraps
from routes.contact_routes import mail, generate_verification_token, verify_verification_token
from flask_mail import Message
from config.auth_config import AuthConfig
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def anonymous_required(f):
    """Decorator to redirect logged-in users away from auth pages"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in'):
            user_role = session.get('role', 'user')
            if user_role == 'super_admin':
                return redirect(url_for('admin.superadmin_dashboard'))
            elif user_role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('user.user_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@auth.route("/login", methods=["GET", "POST"])
@anonymous_required
def login():
    """Enhanced login with captcha support - uses existing login.html template"""
    
    if request.method == "GET":
        # Use your existing login.html template
        return render_template("login.html", 
                             captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                             captcha_enabled=AuthConfig.is_captcha_enabled())
    
    # POST request - process login
    try:
        # Get form data (works with your existing form)
        form_data = {
            'username': request.form.get('username', '').strip(),
            'password': request.form.get('password', ''),
            'g-recaptcha-response': request.form.get('g-recaptcha-response', '')
        }
        
        # Get client IP for captcha verification
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        # Basic validation first
        username = form_data['username']
        password = form_data['password']
        
        if not username:
            flash("Username is required!", "error")
            return render_template("login.html", 
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled())
        
        if not password:
            flash("Password is required!", "error")
            return render_template("login.html", 
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled())
        
        # Validate captcha if enabled
        if AuthConfig.is_captcha_enabled():
            validated_data, validation_errors = validate_login_data(form_data, client_ip)
            if validation_errors:
                for field, errors in validation_errors.items():
                    for error in errors:
                        flash(error, 'error')
                return render_template("login.html", 
                                     captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                     captcha_enabled=AuthConfig.is_captcha_enabled())
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user:
            flash("Invalid username or password!", "error")
            return render_template("login.html", 
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled())
        
        # Check if user can log in
        if hasattr(user, 'email_verified') and not user.email_verified:
            flash("Please verify your email address before logging in.", "error")
            return render_template("login.html", 
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 show_resend_verification=True,
                                 user_email=user.email)
        
        # Verify password - works with both old and new users
        if not User.check_password(user, password):
            flash("Invalid username or password!", "error")
            return render_template("login.html", 
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled())
        
        # Update last login if method exists
        if hasattr(user, 'update_last_login'):
            user.update_last_login()
        
        db.session.commit()
        
        # Set session (same as before)
        session["logged_in"] = True
        session["username"] = user.username
        session["role"] = user.role
        session["user_id"] = user.id
        session["user_tools"] = [access.tool_name for access in user.tool_access]
        
        logger.info(f"User {user.username} logged in successfully")
        
        # Redirect based on role (same as before)
        if user.role == "super_admin":
            return redirect(url_for("admin.superadmin_dashboard"))
        elif user.role == "admin":
            return redirect(url_for("admin.admin_dashboard"))
        else:
            return redirect(url_for("user.user_dashboard"))
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        flash("An error occurred during login. Please try again.", "error")
        return render_template("login.html", 
                             captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                             captcha_enabled=AuthConfig.is_captcha_enabled())


@auth.route("/register", methods=["GET", "POST"])
@anonymous_required
def register():
    """NEW: Simplified single-step registration with email verification"""
    
    if request.method == "GET":
        # Create new simple registration template (will create this)
        return render_template("auth/register.html",
                             captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                             captcha_enabled=AuthConfig.is_captcha_enabled(),
                             password_requirements=AuthConfig.get_password_requirements_text())
    
    # POST request - process registration
    try:
        # Get form data
        form_data = {
            'name': request.form.get('name', '').strip(),
            'username': request.form.get('username', '').strip(),
            'email': request.form.get('email', '').strip().lower(),
            'password': request.form.get('password', ''),
            'confirm_password': request.form.get('confirm_password', ''),
            'g-recaptcha-response': request.form.get('g-recaptcha-response', '')
        }
        
        # Get client IP for captcha verification
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        # Validate input data with captcha
        validated_data, validation_errors = validate_registration_data(form_data, client_ip)
        
        if validation_errors:
            for field, errors in validation_errors.items():
                for error in errors:
                    flash(error, 'error')
            return render_template("auth/register.html",
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 password_requirements=AuthConfig.get_password_requirements_text(),
                                 form_data=form_data)
        
        # Create new user
        new_user = UserFactory.create_user(
            name=validated_data['name'],
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role='user',
            oauth_provider='manual'
        )
        
        # Generate email verification token
        if hasattr(new_user, 'generate_email_verification_token'):
            verification_token = new_user.generate_email_verification_token()
        else:
            verification_token = generate_verification_token(new_user.email)
        
        # Save user to database
        db.session.add(new_user)
        db.session.commit()
        
        # Assign default tools
        User.assign_default_tools(new_user.id)
        
        # Send verification email
        try:
            send_verification_email(new_user.email, new_user.name, verification_token)
            logger.info(f"Verification email sent to {new_user.email}")
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            # Don't fail registration if email sending fails
        
        flash("Registration successful! Please check your email to verify your account before logging in.", "success")
        return redirect(url_for("auth.login"))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        flash("An error occurred during registration. Please try again.", "error")
        return render_template("auth/register.html",
                             captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                             captcha_enabled=AuthConfig.is_captcha_enabled(),
                             password_requirements=AuthConfig.get_password_requirements_text(),
                             form_data=form_data)


# KEEP EXISTING ROUTES - Your old registration system (works in parallel)
@auth.route("/register_step1", methods=["GET", "POST"])
def register_step1():
    """EXISTING: Keep your old step 1 registration for backward compatibility"""
    if request.method == "POST":
        fname = request.form["fname"]
        lname = request.form["lname"]
        address = request.form["address"]
        city = request.form["city"]
        state = request.form["state"]
        zip_code = request.form["zip"]

        session["registration_info"] = {
            "fname": fname,
            "lname": lname,
            "address": address,
            "city": city,
            "state": state,
            "zip": zip_code,
        }

        return redirect(url_for("auth.register_step2"))

    return render_template("register_step1.html")


@auth.route("/register_step2", methods=["GET", "POST"])
def register_step2():
    """EXISTING: Keep your old step 2 registration for backward compatibility"""
    registration_info = session.get("registration_info")

    if not registration_info:
        flash("Please complete step 1 of registration first.", "error")
        return redirect(url_for("auth.register_step1"))

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("auth.register_step2"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return redirect(url_for("auth.register_step2"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "error")
            return redirect(url_for("auth.register_step2"))

        try:
            # Use old UserFactory for backward compatibility
            new_user = UserFactory.create_user(
                username=username,
                email=email,
                fname=registration_info['fname'],
                lname=registration_info['lname'],
                address=registration_info['address'],
                city=registration_info['city'],
                state=registration_info['state'],
                zip=registration_info['zip'],
                role='user',
                password=password
            )
            
            # For legacy users, mark as verified and set name
            if hasattr(new_user, 'email_verified'):
                new_user.email_verified = True
            if hasattr(new_user, 'name') and not new_user.name:
                new_user.name = f"{registration_info['fname']} {registration_info['lname']}"
            
            db.session.add(new_user)
            db.session.commit()

            User.assign_default_tools(new_user.id)

            session.pop("registration_info", None)

            flash("Registration successful!", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "error")
            return redirect(url_for("auth.register_step2"))

    return render_template("register_step2.html")


@auth.route("/verify_email/<token>")
def verify_email(token):
    """NEW: Verify user email address"""
    try:
        # Verify token
        email = verify_verification_token(token, AuthConfig.EMAIL_VERIFICATION_EXPIRY)
        
        if not email:
            flash("Invalid or expired verification link.", "error")
            return redirect(url_for("auth.login"))
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash("User not found.", "error")
            return redirect(url_for("auth.login"))
        
        if hasattr(user, 'email_verified') and user.email_verified:
            flash("Email already verified. You can now log in.", "info")
            return redirect(url_for("auth.login"))
        
        # Verify email
        if hasattr(user, 'verify_email'):
            user.verify_email()
        elif hasattr(user, 'email_verified'):
            user.email_verified = True
            
        db.session.commit()
        
        logger.info(f"Email verified for user: {user.username}")
        flash("Email verified successfully! You can now log in.", "success")
        return redirect(url_for("auth.login"))
        
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        flash("An error occurred during email verification.", "error")
        return redirect(url_for("auth.login"))


@auth.route("/resend_verification", methods=["POST"])
def resend_verification():
    """NEW: Resend email verification"""
    try:
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash("Email address is required.", "error")
            return redirect(url_for("auth.login"))
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Don't reveal that user doesn't exist
            flash("If that email address is registered, we've sent a verification email.", "info")
            return redirect(url_for("auth.login"))
        
        if hasattr(user, 'email_verified') and user.email_verified:
            flash("Email is already verified. You can log in.", "info")
            return redirect(url_for("auth.login"))
        
        # Generate new verification token
        if hasattr(user, 'generate_email_verification_token'):
            verification_token = user.generate_email_verification_token()
        else:
            verification_token = generate_verification_token(user.email)
            
        db.session.commit()
        
        # Send verification email
        display_name = getattr(user, 'name', None) or f"{getattr(user, 'fname', '')} {getattr(user, 'lname', '')}".strip() or user.username
        send_verification_email(user.email, display_name, verification_token)
        
        flash("Verification email sent. Please check your inbox.", "success")
        return redirect(url_for("auth.login"))
        
    except Exception as e:
        logger.error(f"Resend verification error: {str(e)}")
        flash("An error occurred. Please try again.", "error")
        return redirect(url_for("auth.login"))


@auth.route("/logout", methods=["GET", "POST"])
def logout():
    """EXISTING: Keep your logout exactly as is"""
    username = session.get('username', 'Unknown')
    session.clear()
    logger.info(f"User {username} logged out")
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))

@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()

        # For security, we don't reveal if the user was found or not.
        # We always show a confirmation message.

        if user:
            # Generate a secure, timed token (expires in 1 hour by default)
            token = generate_verification_token(email)
            reset_link = url_for("auth.reset_password", token=token, _external=True)
            
            # Create and send the password reset email
            msg = Message(
                subject="Password Reset Request - OmniTools",
                recipients=[email],
            )

            # Get display name (works with both old and new users)
            display_name = getattr(user, 'name', None) or f"{getattr(user, 'fname', '')} {getattr(user, 'lname', '')}".strip() or user.username

            msg.html = render_template(
                "email/password_reset.html",
                name=display_name,
                reset_link=reset_link,
            )
            mail.send(msg)
            
            # For security, always flash the same message and redirect to login for POST requests.
        flash("If an account with that email exists, a password reset link has been sent.", "info")
        return redirect(url_for("auth.login"))
        
    return render_template("forgot_password_request.html")


@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):

    # Verify the token is valid and not expired
    email = verify_verification_token(token)

    if not email:
        flash("The password reset link is invalid or has expired.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return render_template("reset_password.html")

        # Add password validation for new password policy
        try:
            is_valid, errors = AuthConfig.validate_password(password)
            if not is_valid:
                for error in errors:
                    flash(error, "error")
                return render_template("reset_password.html")
        except:
            # If validation fails, continue with basic validation
            if len(password) < 8:
                flash("Password must be at least 8 characters long.", "error")
                return render_template("reset_password.html")

        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(password)
            
            # Update last login if method exists
            if hasattr(user, 'update_last_login'):
                user.update_last_login()
                
            db.session.commit()
            flash("Your password has been updated successfully! You can now log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("reset_password.html")


def send_verification_email(email, name, token):
    verification_link = url_for("auth.verify_email", token=token, _external=True)
    
    msg = Message(
        subject="Verify Your Email - OmniTools",
        recipients=[email],
    )
    
    msg.html = render_template(
        "email/registration_verification.html",
        name=name,
        verification_link=verification_link,
    )
    
    msg.body = f"""
Hi {name},

Welcome to OmniTools! Please verify your email address by clicking the link below:
{verification_link}

This link will expire in 1 hour.

If you didn't create this account, please ignore this email.

Best regards,
The OmniTools Team
"""
    
    mail.send(msg)