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
)
from flask_sqlalchemy import (
    SQLAlchemy,
)  # Already imported in model.model, so not necessary here
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
    db,
    UserFactory,
    ToolAccessManager,
)
from flask_migrate import Migrate
import logging


# Factory function to create a Flask app
def create_app():
    app = Flask(__name__, static_folder="static")

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

    # Route to convert timestamp to a specific timezone
    @app.route("/convert", methods=["GET", "POST"])
    def convert() -> Response:
        if "logged_in" not in session or session["role"] not in ["admin", "superadmin"]:
            return make_response(redirect(url_for("convert")))

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
        if request.method == "POST":
            calculator_type = request.form.get("calculator_type")
            if calculator_type == "canada":
                return redirect(url_for("canada_tax_calculator_check"))

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

    @app.route("/canada_tax_calculator_check", methods=["GET", "POST"])
    def canada_tax_calculator_check():
        """
        Check if the user is logged in before accessing the Canada Tax Calculator.

        This route handler performs the following actions:
        1. Checks if the user is logged in by verifying the presence of 'logged_in' in the session.
        2. If logged in, redirects the user to the Canada Tax Calculator page.
        3. If not logged in, flashes an info message and redirects to the login page.

        Returns:
            A redirect response to either the Canada Tax Calculator or login page.
        """
        if "logged_in" in session:
            return redirect(url_for("canada_tax_calculator"))
        else:
            flash("You need to login to access the Canada Tax Calculator.", "info")
        return redirect(url_for("login"))

    # Route for Canada tax calculator
    @app.route("/canada_tax_calculator", methods=["GET", "POST"])
    def canada_tax_calculator():
        if "logged_in" not in session:
            flash("You need to login to access the Canada Tax Calculator.", "info")
            return redirect(url_for("login"))

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

            new_user = UserFactory.create_user(
                "user", **registration_info, username=username, email=email
            )
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            session.pop("registration_info", None)

            flash("Registration successful!", "success")
            return redirect(url_for("login"))

        return render_template("register_step2.html")

    # Login route
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            user = User.query.filter_by(username=username).first()
            logging.debug(f"User found: {user}")
            if user:
                logging.debug(f"Stored password hash: {user.password}")

            if user and user.check_password(password):
                session["logged_in"] = True
                session["username"] = username
                session["role"] = user.role
                if user.role == "super_admin":
                    return redirect(url_for("superadmin_dashboard"))
                elif user.role == "admin":
                    return redirect(url_for("admin_dashboard"))
                else:
                    return redirect(url_for("user_dashboard"))
        else:
            flash("Invalid username or password!", "error")

        return render_template("login.html")

    # Logout route
    @app.route("/logout", methods=["GET", "POST"])
    def logout():
        session.pop("logged_in", None)
        session.pop("role", None)
        return redirect(url_for("index"))

    # User dashboard route
    @app.route("/user_dashboard", methods=["GET"])
    def user_dashboard():
        if "logged_in" in session:
            username = session.get("username")
            if username:
                user = User.query.filter_by(username=username).first()
                if user:
                    return render_template("user_dashboard.html", user=user)
                else:
                    flash("User not found. Please log in again.", "error")
                    return redirect(url_for("logout"))
            else:
                flash("Session error. Please log in again.", "error")
                return redirect(url_for("logout"))
        return redirect(url_for("login"))

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
            if bcrypt.checkpw(
                request.form["current_password"].encode("utf-8"),
                user.password.encode("utf-8"),
            ):
                if request.form["new_password"] == request.form["confirm_new_password"]:
                    user.set_password(request.form["new_password"])
                    db.session.commit()
                    flash("Password changed successfully!", "success")
                else:
                    flash("New passwords do not match!", "error")
            else:
                flash("Current password is incorrect!", "error")
            return redirect(url_for("user_dashboard"))
        return redirect(url_for("login"))

    # Admin dashboard route
    @app.route("/admin_dashboard", methods=["GET"])
    def admin_dashboard():
        if "logged_in" in session and session.get("role") in ["admin", "super_admin"]:
            users = User.query.all()
            return render_template("admin_dashboard.html", users=users)
        return redirect(url_for("login"))

    # New route for viewing user activity
    @app.route("/view_user_activity/<int:user_id>", methods=["GET"])
    def view_user_activity(user_id):
        if "logged_in" in session and session.get("role") in ["admin", "super_admin"]:
            admin = Admin.query.filter_by(username=session.get("username")).first()
            if admin:
                activity = admin.view_user_activity(user_id)
                return render_template("user_activity.html", activity=activity)
        return redirect(url_for("login"))

    # New route for granting tool access
    @app.route("/grant_tool_access", methods=["POST"])
    def grant_tool_access():
        if "logged_in" in session and session.get("role") in ["admin", "super_admin"]:
            admin = Admin.query.filter_by(username=session.get("username")).first()
            if admin:
                user_id = request.form.get("user_id")
                tool_name = request.form.get("tool_name")
                admin.grant_tool_access(user_id, tool_name)
                flash(f"Tool access granted for {tool_name}", "success")
                return redirect(url_for("admin_dashboard"))
        return redirect(url_for("login"))

        # New route for revoking tool access

    @app.route("/revoke_tool_access", methods=["POST"])
    def revoke_tool_access():
        if "logged_in" in session and session.get("role") in ["admin", "super_admin"]:
            admin = Admin.query.filter_by(username=session.get("username")).first()
            if admin:
                user_id = request.form.get("user_id")
                tool_name = request.form.get("tool_name")
                admin.revoke_tool_access(user_id, tool_name)
                flash(f"Tool access revoked for {tool_name}", "success")
                return redirect(url_for("admin_dashboard"))
        return redirect(url_for("login"))

    # New route for super admin dashboard
    @app.route("/super_admin_dashboard", methods=["GET"])
    def super_admin_dashboard():
        if "logged_in" in session and session.get("role") == "super_admin":
            users = User.query.all()
            admins = Admin.query.all()
            return render_template(
                "super_admin_dashboard.html", users=users, admins=admins
            )
        return redirect(url_for("login"))

    # New route for changing user role
    @app.route("/change_user_role", methods=["POST"])
    def change_user_role():
        if "logged_in" in session and session.get("role") == "super_admin":
            super_admin = SuperAdmin.query.filter_by(
                username=session.get("username")
            ).first()
            if super_admin:
                user_id = request.form.get("user_id")
                new_role = request.form.get("new_role")
                super_admin.change_user_role(user_id, new_role)
                flash(f"User role changed to {new_role}", "success")
                return redirect(url_for("super_admin_dashboard"))
        return redirect(url_for("login"))

    # The following setup route is commented out as it has already been run once for security reasons.
    @app.route("/setup", methods=["GET"])
    def setup():
        try:
            print("Starting setup...")
            if not User.query.filter_by(role="super_admin").first():
                print("Creating superadmin...")
                superadmin = User(
                    username="superadmin",
                    email="super@admin.com",
                    fname="Super",
                    lname="Admin",
                    address="123 Admin St",
                    city="Admin City",
                    state="AS",
                    zip="12345",
                    role="super_admin",
                )
                print("Setting superadmin password...")
                superadmin.set_password("superpass")
                print("Superadmin password set")

                print("Creating admin...")
                admin = User(
                    username="admin",
                    email="admin@example.com",
                    fname="Regular",
                    lname="Admin",
                    address="456 Admin Ave",
                    city="Admin Town",
                    state="AT",
                    zip="67890",
                    role="admin",
                )
                print("Setting admin password...")
                admin.set_password("adminpass")
                print("Admin password set")

                print("Adding to session...")
                db.session.add(superadmin)
                db.session.add(admin)
                print("Committing...")
                db.session.commit()
                print("Setup complete")
                return "Setup complete. Superadmin and Admin created."
            return "Setup already done."
        except Exception as e:
            db.session.rollback()
            print(f"Error during setup: {str(e)}")
            return f"Error during setup: {str(e)}"


# The 'if __name__' block is still required to run the app
if __name__ == "__model__":
    app = create_app()
    app.run(debug=True)
