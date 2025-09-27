"""
Fixed auth_routes.py with proper email verification flow
This file replaces the entire routes/auth_routes.py to fix the email verification issues
"""

from flask import Blueprint, request, jsonify, redirect, url_for, render_template, session, flash
from model import User, db, UserFactory
from werkzeug.security import check_password_hash
from functools import wraps
from routes.contact_routes import mail, generate_verification_token, verify_verification_token
from flask_mail import Message
from config.auth_config import AuthConfig
import logging
import re
import os
import requests
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)

def verify_recaptcha(recaptcha_response, remote_ip=None):
    """Verify reCAPTCHA response with Google's servers"""
    if not AuthConfig.is_captcha_enabled():
        logger.info("Captcha verification skipped - captcha disabled")
        return True
    
    if not recaptcha_response:
        logger.warning("Captcha verification failed - no response token provided")
        return False
        
    try:
        data = {
            "secret": AuthConfig.RECAPTCHA_SECRET_KEY,
            "response": recaptcha_response,
        }
        if remote_ip:
            data["remoteip"] = remote_ip
        
        logger.info("Sending captcha verification request to Google")
        response = requests.post(AuthConfig.RECAPTCHA_VERIFY_URL, data=data, timeout=5)
        result = response.json()
        
        success = result.get("success", False)
        if success:
            logger.info("Captcha verification successful")
        else:
            error_codes = result.get("error-codes", [])
            logger.warning(f"Captcha verification failed - Google errors: {error_codes}")
        
        return success
        
    except Exception as e:
        logger.error(f"Captcha verification exception: {str(e)}")
        return False

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            logger.warning(f"Unauthorized access attempt to {request.endpoint} from IP: {request.remote_addr}")
            flash('Please log in to access this page.', 'error')
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

def anonymous_required(f):
    """Decorator to redirect logged-in users away from auth pages"""
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

def parse_full_name(full_name):
    """Parse full name into first and last name"""
    if not full_name or not full_name.strip():
        return "User", "Name"
    
    name_parts = full_name.strip().split()
    if len(name_parts) == 1:
        return name_parts[0], "User"
    elif len(name_parts) == 2:
        return name_parts[0], name_parts[1]
    else:
        # For names with more than 2 parts, first word is fname, rest is lname
        return name_parts[0], " ".join(name_parts[1:])

def send_verification_email(user_email, user_name):
    """Send email verification email to new user"""
    try:
        logger.info(f"Preparing verification email for: {user_email}")
        
        # Generate verification token
        token = generate_verification_token(user_email)
        verification_link = url_for("auth.verify_email", token=token, _external=True)
        
        logger.info(f"Generated verification link: {verification_link}")
        
        # Create verification email
        msg = Message(
            subject="Verify Your Email - OmniTools Registration",
            recipients=[user_email],
        )
        
        # Use the existing registration verification template
        msg.html = render_template(
            "email/email_verification.html",
            name=user_name,
            verification_link=verification_link,
        )
        
        # Fallback plain text
        msg.body = f"""
        Hi {user_name},
        
        Welcome to OmniTools! Please verify your email address by clicking this link:
        {verification_link}
        
        This link will expire in 1 hour for security.
        
        If you didn't create an account, please ignore this email.
        
        © 2024 OmniTools. All rights reserved.
        """
        
        # Send the email
        mail.send(msg)
        logger.info(f"Verification email sent successfully to: {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user_email}: {str(e)}")
        return False

@auth.route("/login", methods=["GET", "POST"])
@anonymous_required
def login():
    """FIXED LOGIN: Now properly checks email verification before allowing login"""
    
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    if request.method == "GET":
        logger.info(f"Login page accessed from IP: {client_ip}")
        # Clear any existing flash messages for GET requests
        session.pop('_flashes', None)
        return render_template("login.html", 
                             captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                             captcha_enabled=AuthConfig.is_captcha_enabled())
    
    # POST request - process login
    logger.info(f"Login attempt initiated from IP: {client_ip}")
    
    try:
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        recaptcha_response = request.form.get("g-recaptcha-response", "")
        
        logger.info(f"Login form data received - username: '{username}', password: {'[PROVIDED]' if password else '[MISSING]'}")
        
        # Basic validation
        if not username:
            logger.warning("Login failed - username not provided")
            flash("Username is required!", "error")
            return render_template("login.html", 
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled())
        
        if not password:
            logger.warning(f"Login failed for '{username}' - password not provided")
            flash("Password is required!", "error")
            return render_template("login.html", 
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled())
        
        # Verify captcha if enabled
        if AuthConfig.is_captcha_enabled():
            logger.info(f"Verifying captcha for login attempt: '{username}'")
            if not verify_recaptcha(recaptcha_response, client_ip):
                logger.warning(f"Login failed for '{username}' - captcha verification failed")
                flash("Please complete the captcha verification!", "error")
                return render_template("login.html", 
                                     captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                     captcha_enabled=AuthConfig.is_captcha_enabled())
            logger.info(f"Captcha verification passed for '{username}'")
        
        # Find and validate user
        logger.info(f"Looking up user in database: '{username}'")
        user = User.query.filter_by(username=username).first()
        
        if not user:
            logger.warning(f"Login failed - user not found: '{username}'")
            flash("Invalid username or password!", "error")
            return render_template("login.html", 
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled())
        
        logger.info(f"User found - ID: {user.id}, Role: {user.role}, Email: {user.email}")
        
        # Check password using the User model's check_password method
        logger.info(f"Verifying password for user: '{username}'")
        if not User.check_password(user, password):
            logger.warning(f"Login failed for '{username}' - invalid password")
            flash("Invalid username or password!", "error")
            return render_template("login.html", 
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled())
        
        logger.info(f"Password verification passed for user: '{username}'")
        
        # CRITICAL FIX: Check if email verification is required - this blocks unverified users
        if hasattr(user, 'email_verified') and not user.email_verified:
            logger.warning(f"Login blocked for '{username}' - email not verified")
            flash("Please verify your email address before logging in. Check your email for the verification link.", "error")
            
            # Store user info for resend verification option
            session['pending_verification_email'] = user.email
            session['pending_verification_name'] = getattr(user, 'name', user.username)
            
            return redirect(url_for("auth.verification_pending"))
        
        logger.info(f"Email verification check passed for user: '{username}'")
        
        # Set up user session - successful login
        session["logged_in"] = True
        session["username"] = username
        session["role"] = user.role
        session["user_id"] = user.id
        
        # Set tool access if available
        if hasattr(user, 'tool_access'):
            tool_names = [access.tool_name for access in user.tool_access]
            session["user_tools"] = tool_names
            logger.info(f"User tools assigned to session: {tool_names}")
        
        # Update last login if attribute exists
        if hasattr(user, 'last_login'):
            user.last_login = datetime.utcnow()
            db.session.commit()
            logger.info(f"Updated last login timestamp for user: '{username}'")
        
        # Determine redirect based on role
        if user.role == "super_admin":
            redirect_route = "admin.superadmin_dashboard"
        elif user.role == "admin":
            redirect_route = "admin.admin_dashboard"
        else:
            redirect_route = "user.user_dashboard"
        
        logger.info(f"LOGIN SUCCESS: User '{username}' logged in from IP: {client_ip}")
        logger.info(f"Redirecting to: {redirect_route}")
        
        return redirect(url_for(redirect_route))
        
    except Exception as e:
        logger.error(f"Login exception for '{username if 'username' in locals() else 'unknown'}': {str(e)}")
        flash("An error occurred during login. Please try again.", "error")
        return render_template("login.html", 
                             captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                             captcha_enabled=AuthConfig.is_captcha_enabled())

@auth.route("/verify_email/<token>")
def verify_email(token):
    """FIXED EMAIL VERIFICATION: Now automatically logs user in after verification"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    logger.info(f"Email verification attempted from IP: {client_ip}")
    
    try:
        logger.info("Verifying email verification token")
        email = verify_verification_token(token, 3600)  # 1 hour expiry
        
        if not email:
            logger.warning("Email verification failed - invalid or expired token")
            flash("Invalid or expired verification link. Please register again or contact support.", "error")
            return redirect(url_for("auth.login"))
        
        logger.info(f"Valid email verification token for: '{email}'")
        user = User.query.filter_by(email=email).first()
        
        if not user:
            logger.error(f"User not found for email verification: '{email}'")
            flash("User account not found. Please register again.", "error")
            return redirect(url_for("auth.register"))
        
        if hasattr(user, 'email_verified'):
            if user.email_verified:
                logger.info(f"Email already verified for user: '{user.username}'")
                flash("Your email was already verified. Welcome back!", "success")
            else:
                logger.info(f"Marking email as verified for user: '{user.username}' (ID: {user.id})")
                user.email_verified = True
                db.session.commit()
                logger.info(f"EMAIL VERIFICATION SUCCESS: Email verified for user '{user.username}' from IP: {client_ip}")
                flash("Email verified successfully! Welcome to OmniTools!", "success")
            
            # Clear pending verification from session
            session.pop('pending_verification_email', None)
            session.pop('pending_verification_name', None)
            
            # CRITICAL FIX: AUTOMATIC LOGIN after email verification
            logger.info(f"Automatically logging in verified user: '{user.username}'")
            session["logged_in"] = True
            session["username"] = user.username
            session["role"] = user.role
            session["user_id"] = user.id
            
            # Set tool access if available
            if hasattr(user, 'tool_access'):
                tool_names = [access.tool_name for access in user.tool_access]
                session["user_tools"] = tool_names
                logger.info(f"User tools assigned to session: {tool_names}")
            
            # Update last login if attribute exists
            if hasattr(user, 'last_login'):
                user.last_login = datetime.utcnow()
                db.session.commit()
                logger.info(f"Updated last login timestamp for user: '{user.username}'")
            
            # Determine redirect based on role
            if user.role == "super_admin":
                redirect_route = "admin.superadmin_dashboard"
            elif user.role == "admin":
                redirect_route = "admin.admin_dashboard"
            else:
                redirect_route = "user.user_dashboard"
            
            logger.info(f"EMAIL VERIFICATION + AUTO-LOGIN SUCCESS: User '{user.username}' verified and logged in from IP: {client_ip}")
            logger.info(f"Redirecting to: {redirect_route}")
            
            # CRITICAL FIX: Redirect directly to dashboard, not login page
            return redirect(url_for(redirect_route))
            
        else:
            logger.info(f"Email verification not required for user: '{user.username}'")
            flash("Email verification completed successfully. You can now log in.", "success")
            return redirect(url_for("auth.login"))
        
    except Exception as e:
        logger.error(f"Email verification exception: {str(e)}")
        flash("An error occurred during email verification. Please try again or contact support.", "error")
        return redirect(url_for("auth.login"))

@auth.route("/verification_pending")
def verification_pending():
    """Show verification pending page after registration"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    logger.info(f"Verification pending page accessed from IP: {client_ip}")
    
    # Get user info from session (set during registration)
    user_email = session.get('pending_verification_email')
    user_name = session.get('pending_verification_name')
    
    if not user_email:
        logger.warning("Verification pending page accessed without email in session")
        flash("Registration session expired. Please register again.", "error")
        return redirect(url_for("auth.register"))
    
    logger.info(f"Showing verification pending page for: {user_email}")
    return render_template("auth/verification_pending.html", 
                         email=user_email, 
                         name=user_name)

@auth.route("/resend_verification", methods=["POST"])
def resend_verification():
    """Resend email verification"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    logger.info(f"Resend verification request from IP: {client_ip}")
    
    try:
        email = session.get('pending_verification_email')
        if not email:
            logger.warning("Resend verification attempted without email in session")
            flash("No pending verification found. Please register again.", "error")
            return redirect(url_for("auth.register"))
        
        logger.info(f"Resending verification email to: {email}")
        user = User.query.filter_by(email=email).first()
        
        if not user:
            logger.error(f"User not found for resend verification: {email}")
            flash("User account not found. Please register again.", "error")
            return redirect(url_for("auth.register"))
        
        # Check if already verified
        if hasattr(user, 'email_verified') and user.email_verified:
            logger.info(f"Resend verification request for already verified user: {email}")
            flash("Your email is already verified. You can log in now.", "success")
            return redirect(url_for("auth.login"))
        
        # Send new verification email
        fname = getattr(user, 'name', email.split('@')[0])
        email_sent = send_verification_email(email, fname)
        
        if email_sent:
            logger.info(f"Verification email resent successfully to: {email}")
            flash("A new verification link has been sent to your email address.", "success")
        else:
            logger.error(f"Failed to resend verification email to: {email}")
            flash("Failed to send verification email. Please try again later.", "error")
        
        return redirect(url_for("auth.verification_pending"))
        
    except Exception as e:
        logger.error(f"Resend verification exception: {str(e)}")
        flash("An error occurred. Please try again.", "error")
        return redirect(url_for("auth.login"))

@auth.route("/register", methods=["GET", "POST"])
@anonymous_required
def register():
    """Simplified single-step registration with email verification"""
    
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    if request.method == "GET":
        logger.info(f"Registration page accessed from IP: {client_ip}")
        return render_template("register.html",
                             captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                             captcha_enabled=AuthConfig.is_captcha_enabled(),
                             password_requirements=AuthConfig.get_password_requirements_text())
    
    # POST request - process registration
    logger.info(f"Registration attempt initiated from IP: {client_ip}")
    
    try:
        # Get form data (adjust field names to match your existing template)
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        recaptcha_response = request.form.get('g-recaptcha-response', '')
        
        logger.info(f"Registration form data received - name: '{name}', username: '{username}', email: '{email}'")
        
        # Store form data for re-rendering on error
        form_data = {
            'name': name,
            'username': username,
            'email': email
        }
        
        # Basic validation
        if not all([name, username, email, password, confirm_password]):
            logger.warning("Registration failed - missing required fields")
            flash("All fields are required!", "error")
            return render_template("register.html",
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 password_requirements=AuthConfig.get_password_requirements_text(),
                                 form_data=form_data)
        
        if password != confirm_password:
            logger.warning("Registration failed - passwords don't match")
            flash("Passwords do not match!", "error")
            return render_template("register.html",
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 password_requirements=AuthConfig.get_password_requirements_text(),
                                 form_data=form_data)
        
        # Verify captcha if enabled
        if AuthConfig.is_captcha_enabled():
            logger.info(f"Verifying captcha for registration: '{username}'")
            if not verify_recaptcha(recaptcha_response, client_ip):
                logger.warning(f"Registration failed for '{username}' - captcha verification failed")
                flash("Please complete the captcha verification!", "error")
                return render_template("register.html",
                                     captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                     captcha_enabled=AuthConfig.is_captcha_enabled(),
                                     password_requirements=AuthConfig.get_password_requirements_text(),
                                     form_data=form_data)
            logger.info(f"Captcha verification passed for '{username}'")
        
        # Check for existing users
        logger.info(f"Checking for existing username: '{username}'")
        if User.query.filter_by(username=username).first():
            logger.warning(f"Registration failed - username '{username}' already exists")
            flash("Username already exists! Please choose a different username.", "error")
            return render_template("register.html",
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 password_requirements=AuthConfig.get_password_requirements_text(),
                                 form_data=form_data)
        
        logger.info(f"Checking for existing email: '{email}'")
        if User.query.filter_by(email=email).first():
            logger.warning(f"Registration failed - email '{email}' already registered")
            flash("Email already registered! Please use a different email or try logging in.", "error")
            return render_template("register.html",
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 password_requirements=AuthConfig.get_password_requirements_text(),
                                 form_data=form_data)
        
        # Parse name
        fname, lname = parse_full_name(name)
        logger.info(f"Parsed name - first: '{fname}', last: '{lname}'")
        
        # Create new user using UserFactory
        logger.info(f"Creating new user with UserFactory")
        new_user = UserFactory.create_user(
            name=name,
            username=username,
            email=email,
            password=password,
            role='user',
            email_verified=False  # CRITICAL: Email not verified initially
        )
        
        logger.info(f"Adding user to database session: ID will be assigned")
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f"User created successfully in database - ID: {new_user.id}")
        
        # Assign default tools if method exists
        if hasattr(User, 'assign_default_tools'):
            logger.info(f"Assigning default tools to user: {new_user.id}")
            User.assign_default_tools(new_user.id)
            logger.info("Default tools assigned successfully")
        else:
            logger.info("No assign_default_tools method found, skipping tool assignment")
        
        # Send verification email
        logger.info(f"Sending verification email to: {email}")
        email_sent = send_verification_email(email, fname)
        
        if email_sent:
            logger.info(f"REGISTRATION SUCCESS: User '{username}' ({email}) registered successfully from IP: {client_ip}")
            logger.info("Verification email sent successfully")
            
            # Store info in session for verification pending page
            session['pending_verification_email'] = email
            session['pending_verification_name'] = fname
            
            # CRITICAL FIX: Redirect to verification pending page, NOT login
            return redirect(url_for("auth.verification_pending"))
        else:
            logger.error(f"Registration completed but failed to send verification email to: {email}")
            flash("Registration successful, but we couldn't send the verification email. Please contact support.", "warning")
            return redirect(url_for("auth.login"))
        
    except Exception as e:
        db.session.rollback()
        username_for_log = username if 'username' in locals() else 'unknown'
        email_for_log = email if 'email' in locals() else 'unknown'
        
        logger.error(f"Registration exception for user '{username_for_log}' ({email_for_log}): {str(e)}")
        logger.error(f"Full exception trace: {e.__class__.__name__}: {str(e)}")
        
        flash("An error occurred during registration. Please try again.", "error")
        return render_template("register.html",
                             captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                             captcha_enabled=AuthConfig.is_captcha_enabled(),
                             password_requirements=AuthConfig.get_password_requirements_text(),
                             form_data=form_data if 'form_data' in locals() else {})

@auth.route("/logout", methods=["GET", "POST"])
def logout():
    """Clean logout implementation"""
    username = session.get('username', 'unknown')
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    logger.info(f"Logout initiated for user: '{username}' from IP: {client_ip}")
    
    session.clear()
    # Clear flash messages to avoid showing them on login page
    session.pop('_flashes', None)
    
    logger.info(f"LOGOUT SUCCESS: User '{username}' logged out successfully")
    return redirect(url_for("auth.login"))

# Keep backward compatibility with existing multi-step registration
@auth.route("/register_step1", methods=["GET", "POST"])
def register_step1():
    """Existing step 1 registration - kept for backward compatibility"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    if request.method == "GET":
        logger.info(f"Multi-step registration step 1 accessed from IP: {client_ip}")
        return render_template("register_step1.html")
    
    logger.info(f"Processing multi-step registration step 1 from IP: {client_ip}")
    
    fname = request.form["fname"]
    lname = request.form["lname"]
    address = request.form["address"]
    city = request.form["city"]
    state = request.form["state"]
    zip_code = request.form["zip"]

    logger.info(f"Step 1 data received - name: '{fname} {lname}', location: {city}, {state}")

    session["registration_info"] = {
        "fname": fname,
        "lname": lname,
        "address": address,
        "city": city,
        "state": state,
        "zip": zip_code,
    }

    logger.info("Step 1 data stored in session, redirecting to step 2")
    return redirect(url_for("auth.register_step2"))

@auth.route("/register_step2", methods=["GET", "POST"])
def register_step2():
    """Existing step 2 registration - kept for backward compatibility"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    registration_info = session.get("registration_info")

    if not registration_info:
        logger.warning(f"Multi-step registration step 2 accessed without step 1 data from IP: {client_ip}")
        flash("Please complete step 1 of registration first.", "error")
        return redirect(url_for("auth.register_step1"))

    if request.method == "GET":
        logger.info(f"Multi-step registration step 2 accessed from IP: {client_ip}")
        return render_template("register_step2.html")

    logger.info(f"Processing multi-step registration step 2 from IP: {client_ip}")

    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    logger.info(f"Step 2 data received - username: '{username}', email: '{email}'")

    if password != confirm_password:
        logger.warning("Multi-step registration failed - passwords don't match")
        flash("Passwords do not match!", "error")
        return redirect(url_for("auth.register_step2"))

    if User.query.filter_by(username=username).first():
        logger.warning(f"Multi-step registration failed - username '{username}' exists")
        flash("Username already exists!", "error")
        return redirect(url_for("auth.register_step2"))

    if User.query.filter_by(email=email).first():
        logger.warning(f"Multi-step registration failed - email '{email}' exists")
        flash("Email already registered!", "error")
        return redirect(url_for("auth.register_step2"))

    try:
        logger.info(f"Creating user with UserFactory for multi-step registration")
        new_user = UserFactory.create_user(
            name=f"{registration_info['fname']} {registration_info['lname']}",
            username=username,
            email=email,
            password=password,
            role='user',
            email_verified=False  # Require email verification for multi-step too
        )
        
        # Add legacy fields if they exist in the user model
        if hasattr(new_user, 'fname'):
            new_user.fname = registration_info['fname']
        if hasattr(new_user, 'lname'):
            new_user.lname = registration_info['lname']
        if hasattr(new_user, 'address'):
            new_user.address = registration_info['address']
        if hasattr(new_user, 'city'):
            new_user.city = registration_info['city']
        if hasattr(new_user, 'state'):
            new_user.state = registration_info['state']
        if hasattr(new_user, 'zip'):
            new_user.zip = registration_info['zip']
        
        db.session.add(new_user)
        db.session.commit()

        if hasattr(User, 'assign_default_tools'):
            User.assign_default_tools(new_user.id)

        session.pop("registration_info", None)
        
        # Send verification email for multi-step registration too
        fname = registration_info['fname']
        email_sent = send_verification_email(email, fname)
        
        if email_sent:
            session['pending_verification_email'] = email
            session['pending_verification_name'] = fname
            
            logger.info(f"MULTI-STEP REGISTRATION SUCCESS: User '{username}' registered")
            flash("Registration successful! Please check your email to verify your account.", "success")
            return redirect(url_for("auth.verification_pending"))
        else:
            logger.error(f"Multi-step registration completed but failed to send verification email")
            flash("Registration successful, but we couldn't send the verification email. Please contact support.", "warning")
            return redirect(url_for("auth.login"))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Multi-step registration exception for '{username}': {str(e)}")
        logger.error(f"Full exception trace: {e.__class__.__name__}: {str(e)}")
        flash("An error occurred during registration. Please try again.", "error")
        return redirect(url_for("auth.register_step2"))

@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    """Existing forgot password functionality"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    if request.method == "GET":
        logger.info(f"Forgot password page accessed from IP: {client_ip}")
        return render_template("forgot_password.html")

    logger.info(f"Password reset request initiated from IP: {client_ip}")
    
    email = request.form.get("email")
    logger.info(f"Password reset requested for email: '{email}'")
    
    user = User.query.filter_by(email=email).first()

    if user:
        logger.info(f"User found for password reset: '{user.username}' (ID: {user.id})")
        try:
            # Generate reset token
            logger.info("Generating password reset token")
            token = generate_verification_token(email)
            reset_link = url_for("auth.reset_password", token=token, _external=True)
            
            # Create reset email
            logger.info(f"Preparing password reset email for: '{email}'")
            msg = Message(
                subject="Password Reset Request",
                recipients=[email],
            )

            # Try to get user's name
            user_name = "User"
            if hasattr(user, 'name') and user.name:
                user_name = user.name
            elif hasattr(user, 'fname') and hasattr(user, 'lname'):
                user_name = f"{user.fname} {user.lname}"

            msg.html = f"""
            <h2>Password Reset Request</h2>
            <p>Hello {user_name},</p>
            <p>You requested a password reset. Click the link below to reset your password:</p>
            <p><a href="{reset_link}">Reset Password</a></p>
            <p>This link will expire in 1 hour for security.</p>
            <p>If you didn't request this reset, please ignore this email.</p>
            <p>© 2024 OmniTools. All rights reserved.</p>
            """
            
            mail.send(msg)
            logger.info(f"Password reset email sent successfully to: {email}")
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {str(e)}")
    else:
        logger.info(f"Password reset requested for non-existent user: {email}")

    # For security, always flash the same message
    flash("If an account with that email exists, a password reset link has been sent.", "info")
    return redirect(url_for("auth.login"))

@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Handle password reset"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    logger.info(f"Password reset page accessed from IP: {client_ip}")
    
    # Verify the token is valid and not expired
    email = verify_verification_token(token)

    if not email:
        logger.warning("Password reset failed - invalid or expired token")
        flash("The password reset link is invalid or has expired.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "GET":
        logger.info(f"Showing password reset form for: {email}")
        return render_template("reset_password.html", token=token)

    logger.info(f"Processing password reset for email: '{email}'")
    
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    
    if not password or not confirm_password:
        logger.warning("Password reset failed - missing password fields")
        flash("Both password fields are required.", "error")
        return render_template("reset_password.html", token=token)
    
    if password != confirm_password:
        logger.warning("Password reset failed - passwords don't match")
        flash("Passwords do not match.", "error")
        return render_template("reset_password.html", token=token)
    
    if len(password) < 8:
        logger.warning(f"Password reset failed - password too short: {len(password)} characters")
        flash("Password must be at least 8 characters long.", "error")
        return render_template("reset_password.html", token=token)
    
    try:
        logger.info(f"Looking up user for password reset: '{email}'")
        user = User.query.filter_by(email=email).first()
        if user:
            logger.info(f"Updating password for user: '{user.username}' (ID: {user.id})")
            user.set_password(password)
            db.session.commit()
            logger.info(f"PASSWORD RESET SUCCESS: Password updated for user '{user.username}' from IP: {client_ip}")
            flash("Password reset successful! You can now log in.", "success")
        else:
            logger.error(f"User not found during password reset: '{email}'")
            flash("User account not found.", "error")
    except Exception as e:
        logger.error(f"Password reset exception for '{email}': {str(e)}")
        flash("An error occurred while resetting your password. Please try again.", "error")

    return redirect(url_for("auth.login"))