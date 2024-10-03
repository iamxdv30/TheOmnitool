from flask import (
    Blueprint,
    request,
    jsonify,
    redirect,
    url_for,
    render_template,
    session,
    flash,
    make_response,
    Response,
)
from model.model import User, ToolAccess, Tool, db, EmailTemplate
from functools import wraps
import pytz
from datetime import datetime
from typing import Union
from Tools.char_counter import count_characters
from Tools.tax_calculator import tax_calculator as calculate_tax
import logging

tool = Blueprint("tool", __name__)

# This function is a decorator that checks if a user has access to a specific tool.
# It verifies if the user is logged in and if they have the necessary permissions
# based on their role or specific tool access.


def tool_access_required(tool_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "logged_in" not in session:
                flash("You need to log in to access this tool.", "error")
                return redirect(url_for("auth.login"))

            user_role = session.get("role")
            user_id = session.get("user_id")

            if user_role not in [
                "admin",
                "superadmin",
            ] and not User.user_has_tool_access(user_id, tool_name):
                flash(
                    f"You don't have access to {tool_name}. Please contact an administrator.",
                    "error",
                )
                return redirect(url_for("user.user_dashboard"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator


@tool.route("/convert", methods=["GET", "POST"])
@tool_access_required("Unix Timestamp Converter")
def convert():
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


@tool.route("/char_counter", methods=["GET", "POST"])
@tool_access_required("Character Counter")
def char_counter():
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


@tool.route("/tax_calculator", methods=["GET", "POST"])
@tool_access_required("Tax Calculator")
def tax_calculator_route():
    if request.method == "POST":
        calculator_type = request.form.get("calculator_type")
        if calculator_type == "canada":
            return redirect(url_for("tool.canada_tax_calculator"))

        logging.debug("Received POST request for US tax calculation")
        data = request.form.to_dict()
        logging.debug(f"Received form data: {data}")

        try:
            # Process items
            items = []
            i = 1
            while f"item_price_{i}" in data and f"item_tax_rate_{i}" in data:
                price = data[f"item_price_{i}"].strip()
                tax_rate = data[f"item_tax_rate_{i}"].strip()
                if price and tax_rate:
                    items.append({"price": float(price), "tax_rate": float(tax_rate)})
                i += 1

            # Process discounts
            discounts = []
            i = 1
            while f"discount_amount_{i}" in data and f"is_discount_taxable_{i}" in data:
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

            logging.debug(f"Processed data for calculation: {calc_data}")

            result = calculate_tax(calc_data)
            logging.debug(f"Calculation result: {result}")
        except ValueError as e:
            logging.error(f"Error during tax calculation: {str(e)}")
            result = None
            flash(
                f"Invalid input: Please ensure all numeric fields contain valid numbers.",
                "error",
            )
        except Exception as e:
            logging.error(f"Unexpected error during tax calculation: {str(e)}")
            result = None
            flash("An unexpected error occurred. Please try again.", "error")

        return render_template("tax_calculator.html", result=result, data=data)
    else:
        logging.debug("Received GET request for tax calculator")
        data = {}
        return render_template("tax_calculator.html", data=data)


@tool.route("/canada_tax_calculator", methods=["GET", "POST"])
@tool_access_required("Canada Tax Calculator")
def canada_tax_calculator():
    if request.method == "POST":
        data = request.form.to_dict()
        result = calculate_tax(data)
        return render_template("canada_tax_calculator.html", result=result, data=data)
    else:
        data = {}
        return render_template("canada_tax_calculator.html", data=data)


@tool.route("/email_templates", methods=["GET", "POST"])
@tool_access_required("Email Templates")
def email_templates() -> Union[Response, str]:
    if "user_id" not in session:
        return make_response(
            jsonify({"error": "You must be logged in to access this feature."}), 401
        )

    if request.method == "GET":
        templates = EmailTemplate.query.filter_by(user_id=session["user_id"]).all()
        return render_template("email_templates.html", templates=templates)

    elif request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        if not title or not content:
            return make_response(
                jsonify({"error": "Both title and content are required."}), 400
            )

        try:
            new_template = EmailTemplate(
                user_id=session["user_id"], title=title, content=content
            )
            db.session.add(new_template)
            db.session.commit()
            return make_response(
                jsonify({"message": "Email template added successfully!"}), 200
            )
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding new template: {str(e)}")
            return make_response(
                jsonify(
                    {"error": f"An error occurred while adding the template: {str(e)}"}
                ),
                500,
            )

    # This should never be reached, but we include it to satisfy the type checker
    return make_response(jsonify({"error": "Invalid request method"}), 405)


@tool.route("/email_templates/<int:template_id>", methods=["PUT", "DELETE"])
@tool_access_required("Email Templates")
def manage_email_template(template_id: int) -> Response:
    if "user_id" not in session:
        return make_response(
            jsonify({"error": "You must be logged in to access this feature."}), 401
        )

    template = EmailTemplate.query.get(template_id)
    if not template or template.user_id != session["user_id"]:
        return make_response(
            jsonify(
                {
                    "error": "Template not found or you don't have permission to modify it."
                }
            ),
            404,
        )

    if request.method == "PUT":
        data = request.json
        if not data:
            return make_response(jsonify({"error": "No data provided"}), 400)

        title = data.get("title")
        content = data.get("content")
        if not title or not content:
            return make_response(
                jsonify({"error": "Both title and content are required."}), 400
            )

        try:
            template.title = title
            template.content = content
            db.session.commit()
            return make_response(
                jsonify({"message": "Email template updated successfully!"}), 200
            )
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating template: {str(e)}")
            return make_response(
                jsonify(
                    {
                        "error": f"An error occurred while updating the template: {str(e)}"
                    }
                ),
                500,
            )

    elif request.method == "DELETE":
        try:
            db.session.delete(template)
            db.session.commit()
            return make_response(
                jsonify({"message": "Email template deleted successfully!"}), 200
            )
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error deleting template: {str(e)}")
            return make_response(
                jsonify(
                    {
                        "error": f"An error occurred while deleting the template: {str(e)}"
                    }
                ),
                500,
            )

    # This line should never be reached, but we include it to satisfy type checking
    return make_response(jsonify({"error": "Invalid method"}), 405)

    # Admin capabilities to handle tool access


@tool.route("/grant_tool_access", methods=["POST"])
def grant_tool_access():
    if "logged_in" in session and session.get("role") in ["admin", "super_admin"]:
        user_id = request.form.get("user_id")
        tool_name = request.form.get("tool_name")
        user = User.query.get(user_id)
        if user:
            if not ToolAccess.query.filter_by(
                user_id=user_id, tool_name=tool_name
            ).first():
                new_access = ToolAccess(user_id=user_id, tool_name=tool_name)
                db.session.add(new_access)
                db.session.commit()
                if "user_tools" in session:
                    del session["user_tools"]  # Clear the session to force a refresh
                flash(
                    f"Tool access granted for {tool_name} to {user.username}", "success"
                )
            else:
                flash(f"User already has access to {tool_name}", "info")
        else:
            flash("User not found", "error")
        return redirect(
            url_for(
                "admin.superadmin_dashboard"
                if session.get("role") == "super_admin"
                else "admin.admin_dashboard"
            )
        )
    return redirect(url_for("auth.login"))


@tool.route("/revoke_tool_access", methods=["POST"])
def revoke_tool_access():
    if "logged_in" in session and session.get("role") in ["admin", "super_admin"]:
        user_id = request.form.get("user_id")
        tool_name = request.form.get("tool_name")
        tool_access = ToolAccess.query.filter_by(
            user_id=user_id, tool_name=tool_name
        ).first()
        if tool_access:
            db.session.delete(tool_access)
            db.session.commit()
            if "user_tools" in session:
                del session["user_tools"]  # Clear the session to force a refresh
            flash(f"Tool access revoked for {tool_name}", "success")
        else:
            flash(f"User doesn't have access to {tool_name}", "info")
        return redirect(
            url_for(
                "admin.superadmin_dashboard"
                if session.get("role") == "super_admin"
                else "admin.admin_dashboard"
            )
        )
    return redirect(url_for("auth.login"))


@tool.route("/check_tool_access/<tool_name>")
def check_tool_access(tool_name):
    logging.debug(f"Checking access for tool: {tool_name}")
    if "logged_in" in session:
        user_id = session.get("user_id")
        logging.debug(f"User ID: {user_id}")

        has_access = (
            ToolAccess.query.filter_by(user_id=user_id, tool_name=tool_name).first()
            is not None
        )
        logging.debug(f"Has access: {has_access}")

        if has_access:
            logging.debug(f"Access granted for tool: {tool_name}")
            tool_urls = {
                "Tax Calculator": "tool.tax_calculator_route",
                "Character Counter": "tool.char_counter",
                "Canada Tax Calculator": "tool.canada_tax_calculator",
                "Unix Timestamp Converter": "tool.convert",
                "Email Templates": "tool.email_templates",
            }

            if tool_name in tool_urls:
                tool_url = url_for(tool_urls[tool_name])
                logging.debug(f"Redirecting to: {tool_url}")
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return jsonify({"access": True, "url": tool_url})
                else:
                    return redirect(tool_url)
            else:
                message = f"Tool {tool_name} is not implemented yet."
                logging.warning(message)
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return jsonify({"access": False, "message": message})
                else:
                    flash(message, "warning")
                    return redirect(url_for("user.user_dashboard"))
        else:
            message = f"You don't have access to {tool_name}. Please contact an administrator."
            logging.warning(f"Access denied for user {user_id} to tool {tool_name}")
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"access": False, "message": message})
            else:
                flash(message, "error")
                return redirect(url_for("user.user_dashboard"))

    message = "Please log in to access tools."
    logging.warning("Attempted tool access without login")
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"access": False, "message": message})
    else:
        flash(message, "error")
        return redirect(url_for("auth.login"))
