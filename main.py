import os

os.environ["FLASK_APP"] = "main.py"

from flask import (
    Flask,
    request,
    jsonify,
    redirect,
    url_for,
    render_template,
    session,
    flash,
    Response,
    make_response,
    get_flashed_messages,
)

from sqlalchemy.exc import SQLAlchemyError
import bcrypt  # Import bcrypt for password hashing
from datetime import (
    timezone,
    datetime,
    timedelta,
)
from Tools.char_counter import count_characters  # Import count_characters from Tools
from Tools.tax_calculator import (
    tax_calculator as calculate_tax,
)  # Import tax_calculator from Tools
import pytz  # Import pytz for timezone operations

from jinja2 import (
    FileSystemLoader,
    Environment,
    ChoiceLoader,
)
from model.model import (
    User,
    Admin,
    SuperAdmin,
    UsageLog,
    ToolAccess,
    Tool,
    db,
    UserFactory,
)
from flask_migrate import Migrate
from werkzeug.wrappers import Response
from typing import Union
from functools import wraps
import logging


# Factory function to create a Flask app
def create_app():
    app = Flask(__name__, static_folder="static")
    app.config['METHOD_OVERRIDE_EXCEPTIONS'] = True

    # Custom method override
    @app.before_request
    def handle_method_override():
        if request.form and '_method' in request.form:
            method = request.form['_method'].upper()
            if method in ['PUT', 'DELETE', 'PATCH']:
                request.environ['REQUEST_METHOD'] = method

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///users.db"  # Use SQLite for simplicity
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = (
        False  # Disable tracking modifications
    )
    app.config["SECRET_KEY"] = (
        "XDVsuperuser@1993"  # Set a secret key for session management
    )

    # Initialize the db with the app
    db.init_app(app)

    # Initialize the migrate with the app and db
    migrate = Migrate(app, db)

    # Set up Jinja2 to load templates from both directories
    with app.app_context():
        app.jinja_env.loader = ChoiceLoader(
            [
                FileSystemLoader(
                    "Tools/templates"
                ),  # Load templates from Tools/templates
                FileSystemLoader(
                    "templates"
                ),  # Load templates from the model templates directory
            ]
        )

        # Create all tables in the database
        db.create_all()  # Create the tables based on models

    # Set the template folder to the correct path
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    # Register routes
    register_routes(app)

    @app.context_processor
    def inject_flashed_messages():
        return dict(messages=get_flashed_messages(with_categories=True))

    return app


# Register all routes in a separate function
def register_routes(app):

    # Home page route
    @app.route("/")
    def index():
        return render_template("index.html")

    # Test page route
    @app.route("/test")
    def test_page():
        return render_template("test.html")
    
    # This function is a decorator that checks if a user has access to a specific tool.
    # It verifies if the user is logged in and if they have the necessary permissions
    # based on their role or specific tool access.
    def tool_access_required(tool_name):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if "logged_in" not in session:
                    flash("You need to log in to access this tool.", "error")
                    return redirect(url_for("login"))

                user_role = session.get("role")
                user_id = session.get("user_id")

                if user_role not in ["admin", "superadmin"] and not User.user_has_tool_access(user_id, tool_name):
                    flash(f"You don't have access to {tool_name}. Please contact an administrator.", "error")
                    return redirect(url_for("user_dashboard"))

                return f(*args, **kwargs)
            return decorated_function
        return decorator

    # Route to convert timestamp to a specific timezone
    @app.route("/convert", methods=["GET", "POST"])
    @tool_access_required("Unix Timestamp Converter")
    def convert() -> Response:
        if request.method == "POST":
            if request.json is None:
                return make_response(
                    jsonify({"result": "Invalid input, JSON expected"}), 400
                )
            input_timestamp_str = request.json.get("timestamp")
            timezone_str = request.json.get("timezone", "UTC")
            try:
                input_timestamp = int(input_timestamp_str)
                timezone = pytz.timezone(timezone_str)
                result = datetime.fromtimestamp(input_timestamp, timezone).strftime(
                    "%Y-%m-%d %H:%M:%S %Z"
                )
                return make_response(render_template("convert.html", result=result))
            except (ValueError, pytz.UnknownTimeZoneError):
                return make_response(
                    jsonify({"result": "Invalid timestamp or timezone"}), 400
                )
        return make_response(render_template("convert.html"))

    # Route for character counter
    @app.route("/char_counter", methods=["GET", "POST"])
    def char_counter() -> Response:
        if "logged_in" not in session or not User.user_has_tool_access(session.get('user_id'), "Character Counter"):
            flash("You don't have access to this tool.", "error")
            return redirect(url_for("user_dashboard"))
        
        if request.method == "POST":
            input_string = request.form.get("text", "")
            total_characters = len(input_string)
            character_limit = 3520
            excess_characters = total_characters - character_limit
            excess_message = (
                f"Character limit exceeded by {excess_characters} characters."
                if excess_characters > 0
                else "Within character limit."
            )
            return make_response(
                render_template(
                    "char_counter.html",
                    input_text=input_string,
                    total_characters=total_characters,
                    excess_message=excess_message,
                )
            )
        return make_response(render_template("char_counter.html"))

    # Route for tax calculator
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    @app.route("/tax_calculator", methods=["GET", "POST"])
    def tax_calculator_route():
        if "logged_in" not in session or not User.user_has_tool_access(session.get('user_id'), "Tax Calculator"):
            flash("You don't have access to this tool.", "error")
            return redirect(url_for("user_dashboard"))
        
        if request.method == "POST":
            calculator_type = request.form.get("calculator_type")
            if calculator_type == "canada":
                return redirect(url_for("canada_tax_calculator"))

            logger.debug("Received POST request for US tax calculation")
            data = request.form.to_dict()
            logger.debug(f"Received form data: {data}")

            try:
                # Process items
                items = []
                i = 1
                while f"item_price_{i}" in data and f"item_tax_rate_{i}" in data:
                    price = data[f"item_price_{i}"].strip()
                    tax_rate = data[f"item_tax_rate_{i}"].strip()
                    if price and tax_rate:
                        items.append(
                            {"price": float(price), "tax_rate": float(tax_rate)}
                        )
                    i += 1

                # Process discounts
                discounts = []
                i = 1
                while (
                    f"discount_amount_{i}" in data
                    and f"is_discount_taxable_{i}" in data
                ):
                    amount = data[f"discount_amount_{i}"].strip()
                    if amount:
                        discounts.append(
                            {
                                "amount": float(amount),
                                "is_taxable": data[f"is_discount_taxable_{i}"] == "Y",
                            }
                        )
                    i += 1

                # Process shipping
                shipping_cost = data.get("shipping_cost", "").strip()
                shipping_cost = float(shipping_cost) if shipping_cost else 0
                shipping_taxable = data.get("shipping_taxable") == "Y"
                shipping_tax_rate = data.get("shipping_tax_rate", "").strip()
                shipping_tax_rate = float(shipping_tax_rate) if shipping_tax_rate else 0

                calc_data = {
                    "items": items,
                    "discounts": discounts,
                    "shipping_cost": shipping_cost,
                    "shipping_taxable": shipping_taxable,
                    "shipping_tax_rate": shipping_tax_rate,
                }

                logger.debug(f"Processed data for calculation: {calc_data}")

                result = calculate_tax(calc_data)
                logger.debug(f"Calculation result: {result}")
            except ValueError as e:
                logger.error(f"Error during tax calculation: {str(e)}")
                result = None
                flash(
                    f"Invalid input: Please ensure all numeric fields contain valid numbers.",
                    "error",
                )
            except Exception as e:
                logger.error(f"Unexpected error during tax calculation: {str(e)}")
                result = None
                flash("An unexpected error occurred. Please try again.", "error")

            return render_template("tax_calculator.html", result=result, data=data)
        else:
            logger.debug("Received GET request for tax calculator")
            data = {}
            return render_template("tax_calculator.html", data=data)

    # Route for Canada tax calculator
    @app.route("/canada_tax_calculator", methods=["GET", "POST"])
    def canada_tax_calculator():
        if "logged_in" not in session or not User.user_has_tool_access(session.get('user_id'), "Canada Tax Calculator"):
            flash("You need to login and have access to use the Canada Tax Calculator.", "error")
            return redirect(url_for("user_dashboard"))

        if request.method == "POST":
            data = request.form.to_dict()
            result = calculate_tax(data)
            return render_template(
                "canada_tax_calculator.html", result=result, data=data
            )
        else:
            data = {}
            return render_template("canada_tax_calculator.html", data=data)

    # Route for registration step 1
    @app.route("/register_step1", methods=["GET", "POST"])
    def register_step1():
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

            return redirect(url_for("register_step2"))

        return render_template("register_step1.html")

    # Route for registration step 2
    @app.route("/register_step2", methods=["GET", "POST"])
    def register_step2():
        registration_info = session.get("registration_info")

        if not registration_info:
            flash("Please complete step 1 of registration first.", "error")
            return redirect(url_for("register_step1"))

        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            confirm_password = request.form["confirm_password"]

            if password != confirm_password:
                flash("Passwords do not match!", "error")
                return redirect(url_for("register_step2"))

            if User.query.filter_by(username=username).first():
                flash("Username already exists!", "error")
                return redirect(url_for("register_step2"))

            if User.query.filter_by(email=email).first():
                flash("Email already registered!", "error")
                return redirect(url_for("register_step2"))

            try:
                new_user = User(
                    username=username,
                    email=email,
                    fname=registration_info['fname'],
                    lname=registration_info['lname'],
                    address=registration_info['address'],
                    city=registration_info['city'],
                    state=registration_info['state'],
                    zip=registration_info['zip'],
                    role='user'
                )
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()

                # Assign default tools
                Tool.assign_default_tools_to_user(new_user.id)

                session.pop("registration_info", None)

                flash("Registration successful!", "success")
                return redirect(url_for("login"))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error during user registration: {str(e)}")
                flash("An error occurred during registration. Please try again.", "error")
                return redirect(url_for("register_step2"))

        return render_template("register_step2.html")

    # Login route
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            user = User.query.filter_by(username=username).first()
            if user and User.check_password(user, password):
                session["logged_in"] = True
                session["username"] = username
                session["role"] = user.role
                session["user_id"] = user.id
                # Refresh tool access information
                session["user_tools"] = [access.tool_name for access in user.tool_access]
                
                if user.role == "super_admin":
                    return redirect(url_for("superadmin_dashboard"))
                elif user.role == "admin":
                    return redirect(url_for("admin_dashboard"))
                else:
                    return redirect(url_for("user_dashboard"))
            else:
                flash("Invalid username or password!", "error")
        else:
            _ = get_flashed_messages()

        return render_template("login.html")

    # Logout route
    @app.route("/logout", methods=["GET", "POST"])
    def logout():
        session.clear()
        # Clear any remaining flash messages
        _ = get_flashed_messages()  # This will consume all flashed messages
        return redirect(url_for("login"))

    # User dashboard route
    @app.route("/user_dashboard", methods=["GET"])
    def user_dashboard():
        logging.debug("Entering user_dashboard route")
        if "logged_in" not in session:
            logging.debug("User not logged in, redirecting to login")
            return redirect(url_for("login"))

        role = session.get("role")
        logging.debug(f"User role: {role}")
        if role == "admin":
            logging.debug("Redirecting admin to admin_dashboard")
            return redirect(url_for("admin_dashboard"))
        elif role == "super_admin":
            logging.debug("Redirecting super_admin to superadmin_dashboard")
            return redirect(url_for("superadmin_dashboard"))

        username = session.get("username")
        logging.debug(f"Username: {username}")
        user = User.query.filter_by(username=username).first()
        if user:
            # Refresh user's tool access from the database
            user_tools = [access.tool_name for access in ToolAccess.query.filter_by(user_id=user.id).all()]
            logging.debug(f"User tools: {user_tools}")
            session["user_tools"] = user_tools  # Update session
            return render_template("user_dashboard.html", user=user, user_tools=user_tools)
        else:
            logging.error(f"User not found for username: {username}")
            flash("User not found. Please log in again.", "error")
            return redirect(url_for("logout"))

    @app.route("/profile", methods=["GET"])
    def profile():
        if "logged_in" in session:
            username = session.get("username")
            if username:
                user = User.query.filter_by(username=username).first()
                if user:
                    return render_template("profile.html", user=user)
                else:
                    flash("User not found. Please log in again.", "error")
                    return redirect(url_for("logout"))
            else:
                flash("Session error. Please log in again.", "error")
                return redirect(url_for("logout"))
        return redirect(url_for("login"))

    @app.route("/update_profile", methods=["POST"])
    def update_profile():
        if "logged_in" in session:
            username = session.get("username")
            if username:
                user = User.query.filter_by(username=username).first()
                if user:
                    # ADDED: Update user information
                    user.fname = request.form["fname"]
                    user.lname = request.form["lname"]
                    user.address = request.form["address"]
                    user.city = request.form["city"]
                    user.state = request.form["state"]
                    user.zip = request.form["zip"]
                    db.session.commit()
                    flash("Profile updated successfully!", "success")
                    # MODIFIED: Redirect to the new profile page
                    return redirect(url_for("profile"))
                else:
                    flash("User not found. Please log in again.", "error")
            else:
                flash("Session error. Please log in again.", "error")
            return redirect(url_for("logout"))
        return redirect(url_for("login"))

    @app.route("/change_password", methods=["POST"])
    def change_password():
        if "logged_in" in session:
            user = User.query.filter_by(username=session["username"]).first()
            if user:  # UPDATED: Check if user exists
                if user.check_password(
                    request.form["current_password"]
                ):  # UPDATED: Use instance method
                    if (
                        request.form["new_password"]
                        == request.form["confirm_new_password"]
                    ):
                        user.set_password(request.form["new_password"])
                        db.session.commit()
                        flash("Password changed successfully!", "success")
                    else:
                        flash("New passwords do not match!", "error")
                else:
                    flash("Current password is incorrect!", "error")
            else:
                flash("User not found!", "error")
            return redirect(url_for("user_dashboard"))
        return redirect(url_for("login"))
    
    def refresh_user_tools(user_id):
        user = User.query.get(user_id)
        if user:
            session["user_tools"] = [access.tool_name for access in user.tool_access]

    # Admin dashboard route
    @app.route("/admin_dashboard", methods=["GET"])
    def admin_dashboard():
        if "logged_in" in session and session.get("role") in ["admin", "super_admin"]:
            users = User.query.all()
            tools = ToolAccess.get_distinct_tool_names()
            user_tools = {user.id: [access.tool_name for access in user.tool_access] for user in users}
            return render_template("admin_dashboard.html", users=users, tools=tools, user_tools=user_tools)
        return redirect(url_for("login"))

    # New route for super admin dashboard
    @app.route("/superadmin_dashboard", methods=["GET"])
    def superadmin_dashboard():
        if "logged_in" in session and session.get("role") == "super_admin":
            users = User.query.all()
            tools = ToolAccess.get_distinct_tool_names()
            user_tools = {user.id: [access.tool_name for access in user.tool_access] for user in users}
            
            # Get flash messages here, so they appear on the dashboard
            messages = get_flashed_messages(with_categories=True)
            
            return render_template("superadmin_dashboard.html", users=users, tools=tools, user_tools=user_tools, messages=messages)
        return redirect(url_for("login"))

    # Routes for Admins and Super Admins capabilities

    @app.route("/grant_tool_access", methods=["POST"])
    def grant_tool_access():
        if "logged_in" in session and session.get("role") in ["admin", "super_admin"]:
            user_id = request.form.get("user_id")
            tool_name = request.form.get("tool_name")
            user = User.query.get(user_id)
            if user:
                if not ToolAccess.query.filter_by(user_id=user_id, tool_name=tool_name).first():
                    new_access = ToolAccess(user_id=user_id, tool_name=tool_name)
                    db.session.add(new_access)
                    db.session.commit()
                    if 'user_tools' in session:
                        del session['user_tools']  # Clear the session to force a refresh
                    flash(f"Tool access granted for {tool_name} to {user.username}", "success")
                else:
                    flash(f"User already has access to {tool_name}", "info")
            else:
                flash("User not found", "error")
            return redirect(url_for("superadmin_dashboard" if session.get("role") == "super_admin" else "admin_dashboard"))
        return redirect(url_for("login"))

    @app.route("/revoke_tool_access", methods=["POST"])
    def revoke_tool_access():
        if "logged_in" in session and session.get("role") in ["admin", "super_admin"]:
            user_id = request.form.get("user_id")
            tool_name = request.form.get("tool_name")
            tool_access = ToolAccess.query.filter_by(user_id=user_id, tool_name=tool_name).first()
            if tool_access:
                db.session.delete(tool_access)
                db.session.commit()
                if 'user_tools' in session:
                    del session['user_tools']  # Clear the session to force a refresh
                flash(f"Tool access revoked for {tool_name}", "success")
            else:
                flash(f"User doesn't have access to {tool_name}", "info")
            return redirect(url_for("superadmin_dashboard" if session.get("role") == "super_admin" else "admin_dashboard"))
        return redirect(url_for("login"))
    

    @app.route("/check_tool_access/<tool_name>")
    def check_tool_access(tool_name):
        logging.debug(f"Checking access for tool: {tool_name}")
        if "logged_in" in session:
            user_id = session.get('user_id')
            logging.debug(f"User ID: {user_id}")
            
            # Use the ToolAccess model to check access
            has_access = ToolAccess.query.filter_by(user_id=user_id, tool_name=tool_name).first() is not None
            logging.debug(f"Has access: {has_access}")
            
            if has_access:
                logging.debug(f"Access granted for tool: {tool_name}")
                tool_urls = {
                    "Tax Calculator": url_for("tax_calculator_route"),
                    "Character Counter": url_for("char_counter"),
                    "Canada Tax Calculator": url_for("canada_tax_calculator"),
                    # Add other tools and their corresponding URLs here
                }
                
                if tool_name in tool_urls:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({"access": True, "url": tool_urls[tool_name]})
                    else:
                        return redirect(tool_urls[tool_name])
                else:
                    message = f"Tool {tool_name} is not implemented yet."
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({"access": False, "message": message})
                    else:
                        flash(message, "warning")
                        return redirect(url_for("user_dashboard"))
            else:
                message = f"You don't have access to {tool_name}. Please contact an administrator."
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({"access": False, "message": message})
                else:
                    flash(message, "error")
                    return redirect(url_for("user_dashboard"))
        
        message = "Please log in to access tools."
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"access": False, "message": message})
        else:
            flash(message, "error")
            return redirect(url_for("login"))

    # New route for changing user role
    @app.route("/change_user_role/<int:user_id>", methods=["POST"])
    def change_user_role(user_id):
        if "logged_in" in session and session.get("role") == "super_admin":
            new_role = request.form.get("new_role")
            SuperAdmin().change_user_role(user_id, new_role)
            flash(f"User role changed to {new_role}", "success")
            return redirect(url_for("superadmin_dashboard"))
        return redirect(url_for("login"))
    
    @app.route('/manage_tools', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def manage_tools():
        if "logged_in" not in session or session.get("role") not in ["admin", "super_admin"]:
            flash("You don't have permission to manage tools.", "error")
            return redirect(url_for("login"))

        if request.method == 'POST':
            tool_name = request.form.get('tool_name')
            is_default = 'is_default' in request.form
            description = request.form.get('description', '')
            existing_tool = Tool.query.filter_by(name=tool_name).first()
            if existing_tool:
                flash("A tool with this name already exists.", "error")
            else:
                new_tool = Tool(name=tool_name, description=description, is_default=is_default)
                db.session.add(new_tool)
                db.session.commit()
                if is_default:
                    Tool.assign_default_tool_to_all_users(tool_name)
                flash("Tool created successfully", "success")
        elif request.method == 'PUT':
            tool_name = request.form.get('tool_name')
            is_default = 'is_default' in request.form
            description = request.form.get('description', '')
            tool = Tool.query.filter_by(name=tool_name).first()
            if tool:
                old_is_default = tool.is_default
                tool.is_default = is_default
                tool.description = description
                db.session.commit()
                if not old_is_default and is_default:
                    Tool.assign_default_tool_to_all_users(tool_name)
                elif old_is_default and not is_default:
                    Tool.remove_default_tool_from_users(tool_name)
                flash("Tool updated successfully", "success")
            else:
                flash("Tool not found", "error")
        elif request.method == 'DELETE':
            tool_name = request.form.get('tool_name')
            tool = Tool.query.filter_by(name=tool_name).first()
            if tool:
                ToolAccess.query.filter_by(tool_name=tool_name).delete()
                db.session.delete(tool)
                db.session.commit()
                flash("Tool deleted successfully", "success")
            else:
                flash("Tool not found", "error")
        
        tools = Tool.query.all()
        return render_template('manage_tools.html', tools=tools)




    # CRUD for Admins and Super Admins

    @app.route("/create_user", methods=["GET", "POST"])
    def create_user():
        if "logged_in" in session and session.get("role") in ["admin", "super_admin"]:
            if request.method == "POST":
                user_data = {
                    "username": request.form.get("username"),
                    "email": request.form.get("email"),
                    "password": request.form.get("password"),
                    "fname": request.form.get("fname"),
                    "lname": request.form.get("lname"),
                    "address": request.form.get("address"),
                    "city": request.form.get("city"),
                    "state": request.form.get("state"),
                    "zip": request.form.get("zip"),
                    "role": request.form.get("role", "user"),
                }
                try:
                    if session.get("role") == "admin":
                        new_user = Admin().create_user(user_data)
                    else:
                        new_user = SuperAdmin().create_user(user_data)
                    Tool.assign_default_tools_to_user(new_user.id)
                    flash("User created successfully", "success")
                except SQLAlchemyError as e:
                    db.session.rollback()
                    app.logger.error(f"Database error creating user: {str(e)}")
                    flash(f"Error creating user: {str(e)}", "error")
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(f"Unexpected error creating user: {str(e)}")
                    flash("An unexpected error occurred while creating the user", "error")
                return redirect(url_for("superadmin_dashboard" if session.get("role") == "super_admin" else "admin_dashboard"))
            return render_template("create_user.html")
        return redirect(url_for("login"))

    @app.route("/update_user/<int:user_id>", methods=["POST"])
    def update_user(user_id: int) -> Union[Response, str]:
        if "logged_in" in session and session.get("role") in ["admin", "super_admin"]:
            user_data = {
                "username": request.form.get("username"),
                "email": request.form.get("email"),
                "fname": request.form.get("fname"),
                "lname": request.form.get("lname"),
                "address": request.form.get("address"),
                "city": request.form.get("city"),
                "state": request.form.get("state"),
                "zip": request.form.get("zip"),
            }
            if request.form.get("password"):
                user_data["password"] = request.form.get("password")

            if session.get("role") == "admin":
                Admin().update_user(user_id, user_data)
            else:
                SuperAdmin().update_user(user_id, user_data)
            flash("User updated successfully", "success")

            if session.get("role") == "admin":
                return redirect(url_for("admin_dashboard"))
            elif session.get("role") == "super_admin":
                return redirect(url_for("superadmin_dashboard"))
        
        return redirect(url_for("login"))


    @app.route("/delete_user/<int:user_id>", methods=["POST"])
    def delete_user(user_id):
        if "logged_in" in session and session.get("role") in ["admin", "super_admin"]:
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                flash("User deleted successfully", "success")

            if session.get("role") == "admin":
                return redirect(url_for("admin_dashboard"))
            elif session.get("role") == "super_admin":
                return redirect(url_for("superadmin_dashboard"))
            else:
                return redirect(url_for("login"))
        return redirect(url_for("login"))

    return app


# The 'if __name__' block is still required to run the app
if __name__ == "__model__":
    app = create_app()
    app.run(debug=True)
