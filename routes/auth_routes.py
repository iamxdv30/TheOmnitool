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
from flask import Blueprint, request, jsonify, redirect, url_for, render_template, session, flash, current_app, g
from model import User, db, UserFactory
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


@auth.route("/cleanup_test_users", methods=["GET"])
def cleanup_test_users():
    """Temporary route to clean up test users"""
    try:
        # Delete test users
        test_users = db.session.query(User).filter(
            User.username.in_(['xyrus_devera', 'test_user'])
        ).all()
        
        for user in test_users:
            db.session.delete(user)
        
        db.session.commit()
        return f"Cleaned up {len(test_users)} test users"
    except Exception as e:
        db.session.rollback()
        return f"Error cleaning up: {str(e)}"


@auth.route("/verify_test_user", methods=["GET"])
def verify_test_user():
    """Temporary route to mark test user as email verified"""
    try:
        with current_app.app_context():
            user = db.session.query(User).filter_by(username='xyrus_devera').first()
            if user:
                if hasattr(user, 'email_verified'):
                    user.email_verified = True
                    db.session.commit()
                    return f"User {user.username} marked as email verified"
                else:
                    return f"User {user.username} doesn't have email_verified attribute"
            else:
                return "User xyrus_devera not found"
    except Exception as e:
        db.session.rollback()
        return f"Error verifying user: {str(e)}"


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
        
        logger.info(f"Login attempt for username: {form_data['username']}")
        
        # Get client IP for captcha verification
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        # Basic validation first
        username = form_data['username']
        password = form_data['password']
        
        if not username:
            logger.warning("Login failed: username not provided")
            flash("Username is required!", "error")
            return render_template("login.html", 
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled())
        
        if not password:
            logger.warning(f"Login failed for {username}: password not provided")
            flash("Password is required!", "error")
            return render_template("login.html", 
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled())
        
        # Validate captcha if enabled
        if AuthConfig.is_captcha_enabled():
            logger.info("Validating captcha for login...")
            validated_data, validation_errors = validate_login_data(form_data, client_ip)
            if validation_errors:
                logger.warning(f"Login captcha validation failed: {validation_errors}")
                for field, errors in validation_errors.items():
                    for error in errors:
                        flash(error, 'error')
                return render_template("login.html", 
                                     captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                     captcha_enabled=AuthConfig.is_captcha_enabled())
        
        # Find user with proper Flask context
        logger.info(f"Finding user with username: {username}")
        with current_app.app_context():
            try:
                user = db.session.query(User).filter_by(username=username).first()
            except Exception as e:
                logger.error(f"Error finding user: {str(e)}")
                flash("An error occurred during login. Please try again.", "error")
                return render_template("login.html", 
                                     captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                     captcha_enabled=AuthConfig.is_captcha_enabled())
        
        if not user:
            logger.warning(f"Login failed: user not found with username: {username}")
            flash("Invalid username or password!", "error")
            return render_template("login.html", 
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled())
        
        logger.info(f"User found: {user.username}, id: {user.id}")
        
        # Check if user can log in
        if hasattr(user, 'email_verified') and not user.email_verified:
            logger.warning(f"Login failed for {username}: email not verified")
            flash("Please verify your email address before logging in.", "error")
            return render_template("login.html", 
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled(),
                                 show_resend_verification=True,
                                 user_email=user.email)
        
        # Verify password - works with both old and new users
        logger.info(f"Verifying password for user: {user.username}")
        if not User.check_password(user, password):
            logger.warning(f"Login failed for {username}: invalid password")
            flash("Invalid username or password!", "error")
            return render_template("login.html", 
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled())
        
        logger.info(f"Password verified successfully for user: {user.username}")
        
        # Update last login if method exists
        if hasattr(user, 'update_last_login'):
            logger.info(f"Updating last login timestamp for user: {user.username}")
            user.update_last_login()
        
        try:
            db.session.commit()
            logger.info(f"Database session committed for user: {user.username}")
        except Exception as db_e:
            logger.error(f"Error committing database session: {str(db_e)}")
            flash("An error occurred during login. Please try again.", "error")
            return render_template("login.html", 
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled())
        
        # Set session (same as before)
        try:
            session["logged_in"] = True
            session["username"] = user.username
            session["role"] = user.role
            session["user_id"] = user.id
            session["user_tools"] = [access.tool_name for access in user.tool_access]
            logger.info(f"Session data set for user: {user.username}")
        except Exception as session_e:
            logger.error(f"Error setting session data: {str(session_e)}")
            flash("An error occurred during login. Please try again.", "error")
            return render_template("login.html", 
                                 captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                 captcha_enabled=AuthConfig.is_captcha_enabled())
        
        logger.info(f"User {user.username} logged in successfully")
        
        # Redirect based on role (same as before)
        if user.role == "super_admin":
            logger.info(f"Redirecting super_admin user {user.username} to superadmin dashboard")
            return redirect(url_for("admin.superadmin_dashboard"))
        elif user.role == "admin":
            logger.info(f"Redirecting admin user {user.username} to admin dashboard")
            return redirect(url_for("admin.admin_dashboard"))
        else:
            logger.info(f"Redirecting regular user {user.username} to user dashboard")
            return redirect(url_for("user.user_dashboard"))
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        import traceback
        logger.error(f"Login traceback: {traceback.format_exc()}")
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
        return render_template("register.html",
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
        
        logger.info(f"Registration attempt for user: {form_data['username']}, email: {form_data['email']}")
        
        # Get client IP for captcha verification
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        # Basic validation without schema
        logger.info("Validating registration data...")
        
        # Validate required fields
        if not form_data['name'].strip():
            flash("Name is required", "error")
            return render_template("register.html",
                                captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                captcha_enabled=AuthConfig.is_captcha_enabled(),
                                password_requirements=AuthConfig.get_password_requirements_text(),
                                form_data=form_data)
                                
        if not form_data['username'].strip():
            flash("Username is required", "error")
            return render_template("register.html",
                                captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                captcha_enabled=AuthConfig.is_captcha_enabled(),
                                password_requirements=AuthConfig.get_password_requirements_text(),
                                form_data=form_data)
                                
        if not form_data['email'].strip():
            flash("Email is required", "error")
            return render_template("register.html",
                                captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                captcha_enabled=AuthConfig.is_captcha_enabled(),
                                password_requirements=AuthConfig.get_password_requirements_text(),
                                form_data=form_data)
                                
        if not form_data['password']:
            flash("Password is required", "error")
            return render_template("register.html",
                                captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                captcha_enabled=AuthConfig.is_captcha_enabled(),
                                password_requirements=AuthConfig.get_password_requirements_text(),
                                form_data=form_data)
                                
        if form_data['password'] != form_data['confirm_password']:
            flash("Passwords do not match", "error")
            return render_template("register.html",
                                captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                captcha_enabled=AuthConfig.is_captcha_enabled(),
                                password_requirements=AuthConfig.get_password_requirements_text(),
                                form_data=form_data)
        
        # Validate password strength
        is_valid, password_errors = AuthConfig.validate_password(form_data['password'])
        if not is_valid:
            for error in password_errors:
                flash(error, "error")
            return render_template("register.html",
                                captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                captcha_enabled=AuthConfig.is_captcha_enabled(),
                                password_requirements=AuthConfig.get_password_requirements_text(),
                                form_data=form_data)
                                
        # Check username uniqueness with proper Flask context
        logger.info("Checking username uniqueness...")
        with current_app.app_context():
            try:
                existing_user = db.session.query(User).filter_by(username=form_data['username']).first()
                if existing_user:
                    logger.warning(f"Username {form_data['username']} already exists")
                    flash("Username already exists", "error")
                    return render_template("register.html",
                                        captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                        captcha_enabled=AuthConfig.is_captcha_enabled(),
                                        password_requirements=AuthConfig.get_password_requirements_text(),
                                        form_data=form_data)
            except Exception as e:
                logger.error(f"Error checking username uniqueness: {str(e)}")
                flash("An error occurred during registration. Please try again.", "error")
                return render_template("register.html",
                                    captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                    captcha_enabled=AuthConfig.is_captcha_enabled(),
                                    password_requirements=AuthConfig.get_password_requirements_text(),
                                    form_data=form_data)
                                    
        # Check email uniqueness with proper Flask context
        logger.info("Checking email uniqueness...")
        with current_app.app_context():
            try:
                existing_email = db.session.query(User).filter_by(email=form_data['email']).first()
                if existing_email:
                    logger.warning(f"Email {form_data['email']} already exists")
                    flash("Email already registered", "error")
                    return render_template("register.html",
                                        captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                        captcha_enabled=AuthConfig.is_captcha_enabled(),
                                        password_requirements=AuthConfig.get_password_requirements_text(),
                                        form_data=form_data)
            except Exception as e:
                logger.error(f"Error checking email uniqueness: {str(e)}")
                flash("An error occurred during registration. Please try again.", "error")
                return render_template("register.html",
                                    captcha_site_key=AuthConfig.RECAPTCHA_SITE_KEY,
                                    captcha_enabled=AuthConfig.is_captcha_enabled(),
                                    password_requirements=AuthConfig.get_password_requirements_text(),
                                    form_data=form_data)
        
        # Create validated_data dict for user creation
        validated_data = {
            'name': form_data['name'].strip(),
            'username': form_data['username'].strip(),
            'email': form_data['email'].strip().lower(),
            'password': form_data['password']
        }
        
        logger.info("Validation successful, creating new user...")
        
        # Create new user
        try:
            new_user = UserFactory.create_user(
                name=validated_data['name'],
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                role='user',
                oauth_provider='manual'
            )
            logger.info(f"User object created: {new_user.username}")
            
            # Generate email verification token
            if hasattr(new_user, 'generate_email_verification_token'):
                verification_token = new_user.generate_email_verification_token()
                logger.info("Generated verification token via user method")
            else:
                verification_token = generate_verification_token(new_user.email)
                logger.info("Generated verification token via utility function")
            
            # Save user to database
            logger.info("Saving user to database...")
            db.session.add(new_user)
            db.session.commit()
            logger.info(f"User {new_user.username} successfully saved to database")
        except Exception as inner_e:
            logger.error(f"Error creating user: {str(inner_e)}")
            raise  # Re-raise to be caught by outer exception handler
        
        # Assign default tools
        try:
            logger.info(f"Assigning default tools to user {new_user.id}")
            User.assign_default_tools(new_user.id)
            logger.info("Default tools assigned successfully")
        except Exception as tool_e:
            logger.error(f"Error assigning default tools: {str(tool_e)}")
            # Continue even if tool assignment fails
        
        # Send verification email
        try:
            logger.info(f"Sending verification email to {new_user.email}")
            send_verification_email(new_user.email, new_user.name, verification_token)
            logger.info(f"Verification email sent to {new_user.email}")
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            # Don't fail registration if email sending fails
        
        logger.info(f"Registration complete for user: {new_user.username}")
        flash("Registration successful! Please check your email to verify your account before logging in.", "success")
        return redirect(url_for("auth.login"))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        import traceback
        logger.error(f"Registration traceback: {traceback.format_exc()}")
        flash("An error occurred during registration. Please try again.", "error")
        return render_template("register.html",  # Changed from auth/register.html to register.html
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