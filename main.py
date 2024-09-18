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
from datetime import timezone, datetime, timedelta
from Tools.char_counter import count_characters
from Tools.tax_calculator import tax_calculator as calculate_tax
import pytz
from jinja2 import FileSystemLoader, Environment, ChoiceLoader


app = Flask(__name__, static_folder="static")

# Set up Jinja2 to load templates from both directories
with app.app_context():
    app.jinja_env.loader = ChoiceLoader([
        FileSystemLoader("Tools/templates"),  # Load templates from Tools/templates
        FileSystemLoader("templates"),  # Load templates from the main templates directory
    ])

# Set the template folder to the correct path
app.config["TEMPLATES_AUTO_RELOAD"] = True

# The secret key is used by Flask to sign session cookies and other cryptographic operations.
app.secret_key = "XDVsuperuser@1993"  # Replace with a strong, unique key in production.

users = {}  # Dictionary to store registered users


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




@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if (
            username in users and users[username]["password"] == password
        ):  # Moved this check up
            session["logged_in"] = True
            session["role"] = users[username]["role"]
            return redirect(
                url_for("user_dashboard")
            )  # Ensure this redirects to user_dashboard
        elif username == "admin" and password == "Xdv-admin@1993":
            session["logged_in"] = True
            session["role"] = "admin"
            return redirect(url_for("dashboard"))
        elif username == "superadmin" and password == "XDVsuperuser@1993":
            session["logged_in"] = True
            session["role"] = "superadmin"
            return redirect(url_for("superadmin"))
        else:
            print(f"Failed login attempt for username: {username}")
            return render_template(
                "login.html",
                role=None,
                error="Invalid username or password. Please try again.",
            )
    return render_template(
        "login.html", role=None
    )  # Pass role as None for GET requests


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("logged_in", None)
    session.pop("role", None)
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users[username] = {
            "password": password,
            "role": "user",
        }  # Store username, password, and role
        print(f"User {username} registered successfully")
        flash("Registration is successful")  # Flash success message
        return redirect(url_for("login"))  # Redirect to login page
    return render_template("register.html")


@app.route("/register_admin", methods=["GET", "POST"])
def register_admin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users[username] = {
            "password": password,
            "role": "admin",
        }  # Store username, password, and role
        return "Registration successful"
    return render_template("register_admin.html")  # Render admin registration form


@app.route("/register_user", methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users[username] = {
            "password": password,
            "role": "user",
        }  # Store username, password, and role
        return "Registration successful"
    return render_template("register_user.html")  # Render user registration form


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
