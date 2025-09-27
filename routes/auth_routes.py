"""
Clean Authentication Routes with Comprehensive Logging
Works with existing HTML templates, fixes login and registration issues
"""
import os
import re
import requests
from flask import Blueprint, request, redirect, url_for, render_template, session, flash, current_app
from model import User, db, UserFactory
from werkzeug.security import check_password_hash
from functools import wraps
from routes.contact_routes import mail, generate_verification_token
from flask_mail import Message
import logging

# Set up clean logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [AUTH] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)

# Simple configuration class to avoid complex dependencies
class AuthConfig:
    RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY')
    RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
    RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
    
    @classmethod
    def is_captcha_enabled(cls):
        enabled = bool(cls.RECAPTCHA_SITE_KEY and cls.RECAPTCHA_SECRET_KEY)
        logger.info(f"Captcha configuration check: {'ENABLED' if enabled else 'DISABLED'}")
        return enabled
    
    @classmethod
    def get_password_requirements_text(cls):
        return "Minimum 8 characters, include uppercase, lowercase, number, and special character"
    
    @classmethod
    def verify_recaptcha(cls, recaptcha_response, remote_ip=None):
        """Verify reCAPTCHA response"""
        logger.info(f"Captcha verification requested from IP: {remote_ip or 'unknown'}")
        
        if not cls.is_captcha_enabled():
            logger.info("Captcha verification skipped - captcha disabled")
            return True
        
        if not recaptcha_response:
            logger.warning("Captcha verification failed - no response token provided")
            return False
            
        try:
            data = {
                "secret": cls.RECAPTCHA_SECRET_KEY,
                "response": recaptcha_response,
            }
            if remote_ip:
                data["remoteip"] = remote_ip
            
            logger.info("Sending captcha verification request to Google")
            response = requests.post(cls.RECAPTCHA_VERIFY_URL, data=data, timeout=5)
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

@auth.route("/login", methods=["GET", "POST"])
@anonymous_required
def login():
    """Clean login implementation - works with existing login.html"""
    
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
            if not AuthConfig.verify_recaptcha(recaptcha_response, client_ip):
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
        
        # Check if email verification is required (if user has this attribute)
        if hasattr(user, 'email_verified') and not user.email_verified:
            logger.warning(f"Login blocked for '{username}' - email not verified")
            flash("Please verify your email address before logging in. Check your email for verification link.", "error")
            return render_template("login.html", 
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled())
        
        # Successful login - set session
        logger.info(f"Setting up session for successful login: '{username}' (Role: {user.role})")
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
            from datetime import datetime
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
        
        logger.info(f"LOGIN SUCCESS: User '{username}' ({user.role}) logged in successfully from IP: {client_ip}")
        logger.info(f"Redirecting to: {redirect_route}")
        
        return redirect(url_for(redirect_route))
    
    except Exception as e:
        logger.error(f"Login exception for user '{username if 'username' in locals() else 'unknown'}': {str(e)}")
        logger.error(f"Full exception trace: {e.__class__.__name__}: {str(e)}")
        flash("An error occurred during login. Please try again.", "error")
        return render_template("login.html", 
                             captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                             captcha_enabled=AuthConfig.is_captcha_enabled())

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

@auth.route("/register", methods=["GET", "POST"])
@anonymous_required
def register():
    """Simplified single-step registration - works with existing register.html"""
    
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
        
        logger.info(f"Registration form data - name: '{name}', username: '{username}', email: '{email}'")
        
        # Store form data for re-rendering on error
        form_data = {
            'name': name,
            'username': username,
            'email': email
        }
        
        # Basic validation
        logger.info("Starting registration validation")
        
        if not name:
            logger.warning("Registration validation failed - name missing")
            flash("Name is required", "error")
            return render_template("register.html",
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 password_requirements=AuthConfig.get_password_requirements_text(),
                                 form_data=form_data)
        
        if not username:
            logger.warning("Registration validation failed - username missing")
            flash("Username is required", "error")
            return render_template("register.html",
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 password_requirements=AuthConfig.get_password_requirements_text(),
                                 form_data=form_data)
        
        if not email:
            logger.warning("Registration validation failed - email missing")
            flash("Email is required", "error")
            return render_template("register.html",
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 password_requirements=AuthConfig.get_password_requirements_text(),
                                 form_data=form_data)
        
        if not password:
            logger.warning("Registration validation failed - password missing")
            flash("Password is required", "error")
            return render_template("register.html",
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 password_requirements=AuthConfig.get_password_requirements_text(),
                                 form_data=form_data)
        
        if password != confirm_password:
            logger.warning("Registration validation failed - passwords don't match")
            flash("Passwords do not match", "error")
            return render_template("register.html",
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 password_requirements=AuthConfig.get_password_requirements_text(),
                                 form_data=form_data)
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            logger.warning(f"Registration validation failed - invalid email format: '{email}'")
            flash("Please enter a valid email address", "error")
            return render_template("register.html",
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 password_requirements=AuthConfig.get_password_requirements_text(),
                                 form_data=form_data)
        
        # Validate username format
        if len(username) < 3 or len(username) > 50:
            logger.warning(f"Registration validation failed - username length invalid: '{username}' (length: {len(username)})")
            flash("Username must be between 3 and 50 characters", "error")
            return render_template("register.html",
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 password_requirements=AuthConfig.get_password_requirements_text(),
                                 form_data=form_data)
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            logger.warning(f"Registration validation failed - username contains invalid characters: '{username}'")
            flash("Username can only contain letters, numbers, and underscores", "error")
            return render_template("register.html",
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 password_requirements=AuthConfig.get_password_requirements_text(),
                                 form_data=form_data)
        
        # Basic password validation
        if len(password) < 8:
            logger.warning(f"Registration validation failed - password too short: {len(password)} characters")
            flash("Password must be at least 8 characters long", "error")
            return render_template("register.html",
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 password_requirements=AuthConfig.get_password_requirements_text(),
                                 form_data=form_data)
        
        logger.info("Basic validation passed, checking captcha")
        
        # Verify captcha if enabled
        if AuthConfig.is_captcha_enabled():
            logger.info(f"Verifying captcha for registration: '{username}'")
            if not AuthConfig.verify_recaptcha(recaptcha_response, client_ip):
                logger.warning(f"Registration failed for '{username}' - captcha verification failed")
                flash("Please complete the captcha verification!", "error")
                return render_template("register.html",
                                     captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                     captcha_enabled=AuthConfig.is_captcha_enabled(),
                                     password_requirements=AuthConfig.get_password_requirements_text(),
                                     form_data=form_data)
            logger.info(f"Captcha verification passed for registration: '{username}'")
        
        logger.info("Checking for existing username and email")
        
        # Check for existing username
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            logger.warning(f"Registration failed - username already exists: '{username}'")
            flash("Username already exists", "error")
            return render_template("register.html",
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 password_requirements=AuthConfig.get_password_requirements_text(),
                                 form_data=form_data)
        
        # Check for existing email
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            logger.warning(f"Registration failed - email already exists: '{email}'")
            flash("Email already registered", "error")
            return render_template("register.html",
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 password_requirements=AuthConfig.get_password_requirements_text(),
                                 form_data=form_data)
        
        logger.info(f"Username and email available, creating new user: '{username}' ({email})")
        
        # Create new user using the existing UserFactory
        try:
            logger.info("Attempting to create user with new UserFactory method")
            # Try the new simplified UserFactory method first
            new_user = UserFactory.create_user(
                name=name,
                username=username,
                email=email,
                password=password,
                role='user'
            )
            logger.info("User created successfully with new UserFactory method")
        except TypeError as e:
            logger.info(f"New UserFactory method failed ({str(e)}), trying fallback method")
            # Fallback to the old UserFactory method if the new one doesn't exist
            new_user = UserFactory.create_user(
                username=username,
                email=email,
                role='user',
                password=password
            )
            # Set name field if it exists
            if hasattr(new_user, 'name'):
                new_user.name = name
                logger.info("User created with fallback method, name field set")
        
        # Set email as verified for now (you can implement email verification later)
        if hasattr(new_user, 'email_verified'):
            new_user.email_verified = True
            logger.info("Email marked as verified for new user")
        
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
        
        logger.info(f"REGISTRATION SUCCESS: User '{username}' ({email}) registered successfully from IP: {client_ip}")
        flash("Registration successful! You can now log in.", "success")
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

# Keep your existing multi-step registration for backward compatibility
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
        logger.warning(f"Multi-step registration failed - username exists: '{username}'")
        flash("Username already exists!", "error")
        return redirect(url_for("auth.register_step2"))

    if User.query.filter_by(email=email).first():
        logger.warning(f"Multi-step registration failed - email exists: '{email}'")
        flash("Email already registered!", "error")
        return redirect(url_for("auth.register_step2"))

    try:
        logger.info(f"Creating user with multi-step registration data: '{username}'")
        
        # Create user with old method for backward compatibility
        try:
            logger.info("Attempting new UserFactory method for multi-step registration")
            # Try new method first
            new_user = UserFactory.create_user(
                name=f"{registration_info['fname']} {registration_info['lname']}",
                username=username,
                email=email,
                password=password,
                role='user'
            )
            logger.info("Multi-step user created with new UserFactory method")
        except TypeError as e:
            logger.info(f"New method failed ({str(e)}), using fallback for multi-step registration")
            # Fallback to old method
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
            # Set name field if it exists
            if hasattr(new_user, 'name') and not new_user.name:
                new_user.name = f"{registration_info['fname']} {registration_info['lname']}"
                logger.info("Multi-step user created with fallback method, name field set")
        
        # Mark as verified for legacy users
        if hasattr(new_user, 'email_verified'):
            new_user.email_verified = True
            logger.info("Multi-step user marked as email verified")
        
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f"Multi-step user created successfully in database - ID: {new_user.id}")

        # Assign default tools if method exists
        if hasattr(User, 'assign_default_tools'):
            logger.info(f"Assigning default tools to multi-step user: {new_user.id}")
            User.assign_default_tools(new_user.id)
            logger.info("Default tools assigned to multi-step user")

        session.pop("registration_info", None)
        logger.info("Multi-step registration info cleared from session")

        logger.info(f"MULTI-STEP REGISTRATION SUCCESS: User '{username}' ({email}) registered from IP: {client_ip}")
        flash("Registration successful!", "success")
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
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
            """
            
            logger.info(f"Sending password reset email to: '{email}'")
            mail.send(msg)
            logger.info(f"Password reset email sent successfully to: '{email}'")
            
        except Exception as e:
            logger.error(f"Error sending password reset email to '{email}': {str(e)}")
    else:
        logger.warning(f"Password reset requested for non-existent email: '{email}'")
    
    # Always show success message for security
    logger.info(f"Password reset process completed for email: '{email}' (showing generic success message)")
    flash("If an account with that email exists, a password reset link has been sent.", "success")
    return redirect(url_for("auth.login"))

@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Existing reset password functionality"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    logger.info(f"Password reset attempted with token from IP: {client_ip}")
    
    try:
        from routes.contact_routes import verify_verification_token
        logger.info("Verifying password reset token")
        email = verify_verification_token(token, 3600)  # 1 hour expiry
        if email:
            logger.info(f"Valid password reset token for email: '{email}'")
        else:
            logger.warning("Invalid password reset token provided")
    except Exception as e:
        logger.error(f"Error verifying password reset token: {str(e)}")
        email = None
    
    if not email:
        logger.warning("Password reset failed - invalid or expired token")
        flash("Invalid or expired reset link.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "GET":
        logger.info(f"Password reset form displayed for email: '{email}'")
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
            return redirect(url_for("auth.login"))
        else:
            logger.error(f"User not found during password reset for email: '{email}'")
            flash("User not found.", "error")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Password reset exception for email '{email}': {str(e)}")
        flash("An error occurred. Please try again.", "error")

    return render_template("reset_password.html", token=token)

# Email verification route (if you want to implement it later)
@auth.route("/verify_email/<token>")
def verify_email(token):
    """Email verification route - optional"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    logger.info(f"Email verification attempted from IP: {client_ip}")
    
    try:
        from routes.contact_routes import verify_verification_token
        logger.info("Verifying email verification token")
        email = verify_verification_token(token, 3600)  # 1 hour expiry
        
        if not email:
            logger.warning("Email verification failed - invalid or expired token")
            flash("Invalid or expired verification link.", "error")
            return redirect(url_for("auth.login"))
        
        logger.info(f"Valid email verification token for: '{email}'")
        user = User.query.filter_by(email=email).first()
        
        if not user:
            logger.error(f"User not found for email verification: '{email}'")
            flash("User not found.", "error")
            return redirect(url_for("auth.login"))
        
        if hasattr(user, 'email_verified'):
            if user.email_verified:
                logger.info(f"Email already verified for user: '{user.username}'")
                flash("Email already verified. You can now log in.", "success")
            else:
                logger.info(f"Marking email as verified for user: '{user.username}' (ID: {user.id})")
                user.email_verified = True
                db.session.commit()
                logger.info(f"EMAIL VERIFICATION SUCCESS: Email verified for user '{user.username}' from IP: {client_ip}")
                flash("Email verified successfully! You can now log in.", "success")
        else:
            logger.info(f"Email verification not required for user: '{user.username}'")
            flash("Email verification is not required for your account.", "info")
        
        return redirect(url_for("auth.login"))
        
    except Exception as e:
        logger.error(f"Email verification exception: {str(e)}")
        flash("An error occurred during email verification.", "error")
        return redirect(url_for("auth.login"))