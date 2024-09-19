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
from flask_sqlalchemy import SQLAlchemy  # Import SQLAlchemy for database operations
import bcrypt  # Import bcrypt for password hashing
from datetime import timezone, datetime, timedelta  # Import datetime for timestamp operations
from Tools.char_counter import count_characters  # Import count_characters from Tools
from Tools.tax_calculator import tax_calculator as calculate_tax  # Import tax_calculator from Tools
import pytz  # Import pytz for timezone operations
from jinja2 import FileSystemLoader, Environment, ChoiceLoader  # Import Jinja2 for template rendering
from main.model import User  # Import User model from main.model

app = Flask(__name__, static_folder="static")

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable tracking modifications
app.config['SECRET_KEY'] = 'XDVsuperuser@1993'  # Set a secret key for session management

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Set up Jinja2 to load templates from both directories
with app.app_context():
    app.jinja_env.loader = ChoiceLoader([
        FileSystemLoader("Tools/templates"),  # Load templates from Tools/templates
        FileSystemLoader("templates"),  # Load templates from the main templates directory
    ])

# Set the template folder to the correct path
app.config["TEMPLATES_AUTO_RELOAD"] = True

# The secret key is used by Flask to sign session cookies and other cryptographic operations.
app.secret_key = app.config['SECRET_KEY']  # Use the secret key from app config


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/test")
def test_page():
    return render_template("test.html")


@app.route("/convert", methods=["GET", "POST"])
def convert() -> Response:
    """
    Convert the input timestamp to the specified timezone format.
    The input_timestamp parameter is expected to be an integer representing a Unix timestamp.
    """
    if "logged_in" not in session or session["role"] not in ["admin", "superadmin"]:
        return make_response(
            redirect(url_for("convert"))
        )  # Cast redirect to flask.Response

    if request.method == "POST":
        if request.json is None:
            return make_response(
                jsonify({"result": "Invalid input, JSON expected"}), 400
            )  # Handle missing JSON body
        input_timestamp_str = request.json.get(
            "timestamp"
        )  # Extract timestamp as string
        timezone_str = request.json.get(
            "timezone", "UTC"
        )  # Get timezone from request, default to UTC
        try:
            input_timestamp = int(input_timestamp_str)  # Convert string to integer
            # Convert to the specified timezone
            timezone = pytz.timezone(timezone_str)
            result = datetime.fromtimestamp(input_timestamp, timezone).strftime(
                "%Y-%m-%d %H:%M:%S %Z"
            )
            return make_response(
                render_template("convert.html", result=result)
            )  # Wrap with make_response
        except (ValueError, pytz.UnknownTimeZoneError):
            return make_response(
                jsonify({"result": "Invalid timestamp or timezone"}), 400
            )  # Handle invalid input
    return make_response(render_template("convert.html"))  # Wrap with make_response


@app.route("/char_counter", methods=["GET", "POST"])
def char_counter() -> Response:
    if request.method == "POST":
        input_string = request.form.get("text", "")
        total_characters = len(input_string)
        character_limit = 3520
        excess_characters = total_characters - character_limit
        if excess_characters > 0:
            excess_message = (
                f"Character limit exceeded by {excess_characters} characters."
            )
        else:
            excess_message = "Within character limit."
        return make_response(
            render_template(
                "char_counter.html",
                input_text=input_string,
                total_characters=total_characters,
                excess_message=excess_message,
            )
        )
    else:
        return make_response(render_template("char_counter.html"))


from Tools.tax_calculator import tax_calculator as calculate_tax

@app.route("/tax_calculator", methods=["GET", "POST"])
def tax_calculator_route():
    if request.method == "POST":
        data = request.form.to_dict()
        calculator_data = {}
        
        # Process discount items
        discount_items = []
        if data.get('has_discount') == 'Y':
            discount_count = int(data.get('discount_count', 0))
            is_discount_taxable = data.get('is_discount_taxable', 'N') == 'Y'
            for i in range(1, discount_count + 1):
                try:
                    price = float(data.get(f'discount_price_{i}', 0))
                    if price < 0:
                        raise ValueError
                except ValueError:
                    price = None  # Will be handled in validation
                item = {'price': price, 'is_taxable': is_discount_taxable}
                if is_discount_taxable:
                    try:
                        tax_rate = float(data.get(f'discount_tax_rate_{i}', 0))
                        if tax_rate < 0:
                            raise ValueError
                        item['tax_rate'] = tax_rate
                    except ValueError:
                        item['tax_rate'] = None  # Will be handled in validation
                discount_items.append(item)
        calculator_data['discount_items'] = discount_items

        # Process shipping details
        has_shipping = data.get('has_shipping', 'N') == 'Y'
        if has_shipping:
            try:
                shipping_cost = float(data.get('shipping_cost', 0))
                if shipping_cost < 0:
                    raise ValueError
            except ValueError:
                shipping_cost = 0  # Handle invalid input
            shipping_taxable = data.get('shipping_taxable', 'N') == 'Y'
            if shipping_taxable:
                try:
                    shipping_tax_rate = float(data.get('shipping_tax_rate', 0))
                    if shipping_tax_rate < 0:
                        raise ValueError
                except ValueError:
                    shipping_tax_rate = 0  # Handle invalid input
            else:
                shipping_tax_rate = 0
        else:
            shipping_cost = 0
            shipping_tax_rate = 0
            shipping_taxable = False

        calculator_data['shipping_cost'] = shipping_cost
        calculator_data['shipping_tax_rate'] = shipping_tax_rate
        calculator_data['shipping_taxable'] = shipping_taxable

        # Process line items
        try:
            item_count = int(data.get('item_count', 0))
            if item_count < 0:
                raise ValueError
        except ValueError:
            item_count = 0  # Handle invalid input
        calculator_data['item_count'] = item_count

        # Collect line items
        for i in range(1, item_count + 1):
            try:
                price = float(data.get(f'item_price_{i}', 0))
                if price < 0:
                    raise ValueError
            except ValueError:
                price = 0  # Handle invalid input
            try:
                tax_rate = float(data.get(f'item_tax_rate_{i}', 0))
                if tax_rate < 0:
                    raise ValueError
            except ValueError:
                tax_rate = 0  # Handle invalid input
            calculator_data[f'item_price_{i}'] = price
            calculator_data[f'item_tax_rate_{i}'] = tax_rate

        # Now call tax_calculator with calculator_data
        result = calculate_tax(calculator_data)

        return render_template("tax_calculator.html", result=result, data=data)
    else:
        data = {}
        return render_template("tax_calculator.html", data=data)


# Updated register route using User model and SQLAlchemy
# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         # Get form data
#         fname = request.form["fname"]
#         lname = request.form["lname"]
#         address = request.form["address"]
#         city = request.form["city"]
#         state = request.form["state"]
#         zip_code = request.form["zip"]
#         username = request.form["username"]
#         email = request.form["email"]
#         password = request.form["password"]

#         # Check if the username or email already exists
#         if User.query.filter_by(username=username).first():
#             flash("Username already exists!", "error")
#             return redirect(url_for("register"))

#         if User.query.filter_by(email=email).first():
#             flash("Email already registered!", "error")
#             return redirect(url_for("register"))

#         # Create a new User object with all the fields
#         new_user = User(
#             fname=fname,
#             lname=lname,
#             address=address,
#             city=city,
#             state=state,
#             zip=zip_code,
#             username=username,
#             email=email
#         )

#         # Set hashed password
#         hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#         new_user.password = hashed_password.decode('utf-8')

#         # Add the new user to the database
#         db.session.add(new_user)
#         db.session.commit()

#         flash("Registration successful!", "success")
#         return redirect(url_for("login"))

#     return render_template("register.html")

@app.route("/register_step1", methods=["GET", "POST"])
def register_step1():
    if request.method == "POST":
        # Collect personal information
        fname = request.form["fname"]
        lname = request.form["lname"]
        address = request.form["address"]
        city = request.form["city"]
        state = request.form["state"]
        zip_code = request.form["zip"]

        # Store the data in session for the next step
        session['registration_info'] = {
            'fname': fname,
            'lname': lname,
            'address': address,
            'city': city,
            'state': state,
            'zip': zip_code
        }

        # Redirect to the next step (username, email, and password)
        return redirect(url_for("register_step2"))

    return render_template("register_step1.html")

@app.route("/register_step2", methods=["GET", "POST"])
def register_step2():
    # Retrieve the personal info from the session
    registration_info = session.get('registration_info')

    # Check if the session contains the registration info
    if not registration_info:
        flash("Please complete step 1 of registration first.", "error")
        return redirect(url_for("register_step1"))

    if request.method == "POST":
        # Collect the remaining account info
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Validate that passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("register_step2"))

        # Check if the username or email already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return redirect(url_for("register_step2"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "error")
            return redirect(url_for("register_step2"))

        # Extract the data from the session
        fname = registration_info['fname']
        lname = registration_info['lname']
        address = registration_info['address']
        city = registration_info['city']
        state = registration_info['state']
        zip_code = registration_info['zip']

        # Create a new User object with all the collected data
        new_user = User(
            fname=fname,
            lname=lname,
            address=address,
            city=city,
            state=state,
            zip=zip_code,
            username=username,
            email=email
        )

        # Set hashed password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user.password = hashed_password.decode('utf-8')

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Clear the session data after successful registration
        session.pop('registration_info', None)

        flash("Registration successful!", "success")
        return redirect(url_for("login"))

    return render_template("register_step2.html")


# Updated login route using User model and password validation
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Fetch user from the database
        user = User.query.filter_by(username=username).first()

        # Validate user and password
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session["logged_in"] = True
            session["role"] = user.role if hasattr(user, 'role') else "user"
            return redirect(url_for("user_dashboard"))
        else:
            flash("Invalid username or password!", "error")
            return render_template("login.html")

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("logged_in", None)
    session.pop("role", None)
    return redirect(url_for("index"))


# Updated register_admin route using User model and SQLAlchemy
@app.route("/register_admin", methods=["GET", "POST"])
def register_admin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return redirect(url_for("register_admin"))

        # Create a new Admin user
        new_admin = User(username=username, role="admin")
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_admin.password = hashed_password.decode('utf-8')

        db.session.add(new_admin)
        db.session.commit()

        return "Admin registration successful"
    return render_template("register_admin.html")


# Updated register_user route using User model and SQLAlchemy
@app.route("/register_user", methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return redirect(url_for("register_user"))

        # Create a new standard user
        new_user = User(username=username, role="user")
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user.password = hashed_password.decode('utf-8')

        db.session.add(new_user)
        db.session.commit()

        return "User registration successful"
    return render_template("register_user.html")


@app.route("/user/<name>", methods=["GET", "POST"])
def user(name):
    if "logged_in" in session:
        return render_template("user_dashboard.html", name=name)
    else:
        return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "logged_in" in session:
        if session["role"] == "admin":
            return render_template("admin.html")
        elif session["role"] == "superadmin":
            return render_template("superadmin.html")
        elif session["role"] == "user":
            return render_template(
                "user_dashboard.html", converter_accessible=False
            )  # User cannot access converter
        else:
            return render_template(
                "dashboard.html", converter_accessible=False
            )  # Default case for other roles
    else:
        return redirect(url_for("login"))


@app.route("/superadmin", methods=["GET"])
def superadmin():
    if "logged_in" in session and session["role"] == "superadmin":
        return render_template("superadmin.html")
    return redirect(url_for("login"))  # Redirect to login if not logged in


@app.route("/user_dashboard", methods=["GET"])
def user_dashboard():
    if "logged_in" in session and session["role"] == "user":
        return render_template("user_dashboard.html")  # Render user dashboard
    return redirect(url_for("login"))  # Redirect to login if not logged in


if __name__ == "__main__":
    app.run(debug=True)
