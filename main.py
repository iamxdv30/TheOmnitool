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
from flask_sqlalchemy import SQLAlchemy  # Already imported in model.model, so not necessary here
import bcrypt  # Import bcrypt for password hashing
from datetime import (
    timezone,
    datetime,
    timedelta,
)
from Tools.char_counter import count_characters  # Import count_characters from Tools
from Tools.tax_calculator import tax_calculator as calculate_tax  # Import tax_calculator from Tools
import pytz  # Import pytz for timezone operations

from jinja2 import (
    FileSystemLoader,
    Environment,
    ChoiceLoader,
)
from model.model import User, db, UsageLog  # Import User model and db from model.model
from flask_migrate import Migrate


# Factory function to create a Flask app
def create_app():
    app = Flask(__name__, static_folder="static")

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"  # Use SQLite for simplicity
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Disable tracking modifications
    app.config["SECRET_KEY"] = "XDVsuperuser@1993"  # Set a secret key for session management
    

    # Initialize the db with the app
    db.init_app(app)

    # Initialize the migrate with the app and db
    migrate = Migrate(app, db)



    # Set up Jinja2 to load templates from both directories
    with app.app_context():
        app.jinja_env.loader = ChoiceLoader(
            [
                FileSystemLoader("Tools/templates"),  # Load templates from Tools/templates
                FileSystemLoader("templates"),  # Load templates from the model templates directory
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
                return make_response(jsonify({"result": "Invalid input, JSON expected"}), 400)
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
                return make_response(jsonify({"result": "Invalid timestamp or timezone"}), 400)
        return make_response(render_template("convert.html"))

    # Route for character counter
    @app.route("/char_counter", methods=["GET", "POST"])
    def char_counter() -> Response:
        if request.method == "POST":
            input_string = request.form.get("text", "")
            total_characters = len(input_string)
            character_limit = 3520
            excess_characters = total_characters - character_limit
            excess_message = f"Character limit exceeded by {excess_characters} characters." if excess_characters > 0 else "Within character limit."
            return make_response(render_template("char_counter.html", input_text=input_string, total_characters=total_characters, excess_message=excess_message))
        return make_response(render_template("char_counter.html"))

    # Route for tax calculator
    @app.route("/tax_calculator", methods=["GET", "POST"])
    def tax_calculator_route():
        if request.method == "POST":
            data = request.form.to_dict()
            calculator_data = {}

            # Process discount items
            discount_items = []
            if data.get("has_discount") == "Y":
                discount_count = int(data.get("discount_count", 0))
                is_discount_taxable = data.get("is_discount_taxable", "N") == "Y"
                for i in range(1, discount_count + 1):
                    try:
                        price = float(data.get(f"discount_price_{i}", 0))
                        if price < 0:
                            raise ValueError
                    except ValueError:
                        price = None
                    item = {"price": price, "is_taxable": is_discount_taxable}
                    if is_discount_taxable:
                        try:
                            tax_rate = float(data.get(f"discount_tax_rate_{i}", 0))
                            if tax_rate < 0:
                                raise ValueError
                            item["tax_rate"] = tax_rate
                        except ValueError:
                            item["tax_rate"] = None
                    discount_items.append(item)
            calculator_data["discount_items"] = discount_items

            # Process shipping details
            has_shipping = data.get("has_shipping", "N") == "Y"
            if has_shipping:
                try:
                    shipping_cost = float(data.get("shipping_cost", 0))
                    if shipping_cost < 0:
                        raise ValueError
                except ValueError:
                    shipping_cost = 0
                shipping_taxable = data.get("shipping_taxable", "N") == "Y"
                if shipping_taxable:
                    try:
                        shipping_tax_rate = float(data.get("shipping_tax_rate", 0))
                        if shipping_tax_rate < 0:
                            raise ValueError
                    except ValueError:
                        shipping_tax_rate = 0
                else:
                    shipping_tax_rate = 0
            else:
                shipping_cost = 0
                shipping_tax_rate = 0
                shipping_taxable = False

            calculator_data["shipping_cost"] = shipping_cost
            calculator_data["shipping_tax_rate"] = shipping_tax_rate
            calculator_data["shipping_taxable"] = shipping_taxable

            # Process line items
            try:
                item_count = int(data.get("item_count", 0))
                if item_count < 0:
                    raise ValueError
            except ValueError:
                item_count = 0
            calculator_data["item_count"] = item_count

            # Collect line items
            for i in range(1, item_count + 1):
                try:
                    price = float(data.get(f"item_price_{i}", 0))
                    if price < 0:
                        raise ValueError
                except ValueError:
                    price = 0
                try:
                    tax_rate = float(data.get(f"item_tax_rate_{i}", 0))
                    if tax_rate < 0:
                        raise ValueError
                except ValueError:
                    tax_rate = 0
                calculator_data[f"item_price_{i}"] = price
                calculator_data[f"item_tax_rate_{i}"] = tax_rate

            result = calculate_tax(calculator_data)
            return render_template("tax_calculator.html", result=result, data=data)
        else:
            data = {}
            return render_template("tax_calculator.html", data=data)
        
    # Route for Canada tax calculator
    @app.route("/canada_tax_calculator", methods=["GET", "POST"])
    def canada_tax_calculator():
        if request.method == "POST":
            data = request.form.to_dict()
            result = calculate_tax(data)
            return render_template("canada_tax_calculator.html", result=result, data=data)
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

            fname = registration_info["fname"]
            lname = registration_info["lname"]
            address = registration_info["address"]
            city = registration_info["city"]
            state = registration_info["state"]
            zip_code = registration_info["zip"]

            new_user = User(
                fname=fname,
                lname=lname,
                address=address,
                city=city,
                state=state,
                zip=zip_code,
                username=username,
                email=email,
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

            # Fetch user from the database
            user = User.query.filter_by(username=username).first()

            # Validate user and password
            if user and bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
                session["logged_in"] = True
                session["role"] = user.role if hasattr(user, "role") else "user"
                return redirect(url_for("user_dashboard"))
            else:
                flash("Invalid username or password!", "error")
                return render_template("login.html")

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
        if "logged_in" in session and session["role"] == "user":
            return render_template("user_dashboard.html")
        return redirect(url_for("login"))

# The 'if __name__' block is still required to run the app
if __name__ == "__model__":
    app = create_app()
    app.run(debug=True)
