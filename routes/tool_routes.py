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
from model import User, ToolAccess, Tool, db, EmailTemplate
from functools import wraps
import pytz
from datetime import datetime
from typing import Union
from Tools.char_counter import count_characters
from Tools.tax_calculator import tax_calculator as calculate_tax, calculate_vat
import logging

# Use centralized logging configured in main.py
logger = logging.getLogger(__name__)

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
    # This block handles the form submission
    if request.method == "POST":
        input_string = request.form.get("text", "")
        char_limit_str = request.form.get("char_limit")
        
        # --- Robustly get and validate the character limit ---
        try:
            # Use user's limit if provided and valid, otherwise use default
            char_limit = int(char_limit_str) if char_limit_str else 3532
        except (ValueError, TypeError):
            # If input is not a valid number, fall back to default
            char_limit = 3532

        result_data = count_characters(input_string, char_limit)

        return render_template(
            "char_counter.html",
            input_text=input_string,
            total_characters=result_data["total_characters"],
            excess_message=result_data["excess_message"],
            char_limit=char_limit 
        )

    # This handles the initial page load (GET request)
    return render_template("char_counter.html", char_limit=3532)


@tool.route("/tax_calculator", methods=["GET"])
@tool_access_required("Tax Calculator")
def tax_calculator_route():
    """Legacy route - redirects to unified tax calculator"""
    return redirect(url_for("tool.unified_tax_calculator"))


@tool.route("/canada_tax_calculator", methods=["GET"])
@tool_access_required("Tax Calculator")
def canada_tax_calculator():
    """Legacy route - redirects to unified tax calculator (Canada tab)"""
    return redirect(url_for("tool.unified_tax_calculator") + "#canada")


@tool.route("/unified_tax_calculator", methods=["GET", "POST"])
@tool_access_required("Tax Calculator")
def unified_tax_calculator():
    """
    Unified tax calculator route handling US, Canada, and VAT calculations.
    Returns JSON for AJAX requests or renders template for direct access.
    """
    if request.method == "POST":
        try:
            # Handle JSON requests from AJAX
            if request.is_json:
                data = request.json
                calculator_type = data.get("calculator_type", "us")

                logging.debug(f"Unified calculator request for type: {calculator_type}")
                logging.debug(f"Received data: {data}")

                # Route to appropriate calculator based on type
                if calculator_type == "vat":
                    # Prepare data for VAT calculation
                    vat_data = {
                        "vat_rate": data.get("vat_rate", 0),
                        "items": data.get("items", []),
                        "discounts": data.get("discounts", []),
                        "shipping_cost": data.get("shipping_cost", 0),
                        "shipping_taxable": data.get("shipping_taxable", True),
                        "is_sales_before_tax": data.get("options", {}).get("is_sales_before_tax", False),
                        "discount_is_taxable": data.get("options", {}).get("discount_is_taxable", True)
                    }
                    result = calculate_vat(vat_data)

                elif calculator_type == "canada":
                    # Prepare data for Canada sales tax calculation (GST/PST)
                    gst_rate = data.get("gst_rate", 0)
                    pst_rate = data.get("pst_rate", 0)
                    total_tax_rate = float(gst_rate) + float(pst_rate)

                    sales_tax_data = {
                        "items": [],
                        "discounts": data.get("discounts", []),
                        "shipping_cost": data.get("shipping_cost", 0),
                        "shipping_taxable": data.get("shipping_taxable", False),
                        "shipping_tax_rate": total_tax_rate,
                        "is_sales_before_tax": data.get("options", {}).get("is_sales_before_tax", False),
                        "discount_is_taxable": data.get("options", {}).get("discount_is_taxable", True)
                    }

                    # For Canada, all items use the same combined GST/PST rate
                    for item in data.get("items", []):
                        sales_tax_data["items"].append({
                            "price": item.get("price", 0),
                            "tax_rate": total_tax_rate
                        })

                    result = calculate_tax(sales_tax_data)

                elif calculator_type == "us":
                    # Prepare data for US sales tax calculation
                    sales_tax_data = {
                        "items": [],
                        "discounts": data.get("discounts", []),
                        "shipping_cost": data.get("shipping_cost", 0),
                        "shipping_taxable": data.get("shipping_taxable", False),
                        "shipping_tax_rate": data.get("shipping_tax_rate", 0),
                        "is_sales_before_tax": data.get("options", {}).get("is_sales_before_tax", False),
                        "discount_is_taxable": data.get("options", {}).get("discount_is_taxable", True)
                    }

                    # Add tax_rate to items for US (each item has its own rate)
                    for item in data.get("items", []):
                        sales_tax_data["items"].append({
                            "price": item.get("price", 0),
                            "tax_rate": item.get("tax_rate", 0)
                        })

                    result = calculate_tax(sales_tax_data)

                else:
                    raise ValueError(f"Invalid calculator type: {calculator_type}")

                logging.debug(f"Calculation result: {result}")
                return jsonify({"success": True, "data": result})

            else:
                # Handle form submission (fallback)
                return jsonify({"success": False, "error": "JSON data expected"}), 400

        except ValueError as e:
            logging.error(f"Validation error in unified calculator: {str(e)}")
            logging.error(f"Request data was: {request.json}")
            return jsonify({"success": False, "error": str(e)}), 400

        except Exception as e:
            logging.error(f"Unexpected error in unified calculator: {str(e)}")
            logging.error(f"Request data was: {request.json}")
            logging.exception("Full traceback:")
            return jsonify({"success": False, "error": f"An unexpected error occurred: {str(e)}"}), 500

    else:
        # GET request - render the unified calculator template
        return render_template("unified_tax_calculator.html")


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
        tool = Tool.query.filter_by(name=tool_name).first()
        
        if user and tool:
            if tool.is_default and session.get("role") != "super_admin":
                flash(f"Only super admins can grant access to default tools", "error")
            elif not ToolAccess.query.filter_by(user_id=user_id, tool_name=tool_name).first():
                new_access = ToolAccess(user_id=user_id, tool_name=tool_name)
                db.session.add(new_access)
                db.session.commit()
                if "user_tools" in session:
                    del session["user_tools"]  # Clear the session to force a refresh
                flash(f"Tool access granted for {tool_name} to {user.username}", "success")
            else:
                flash(f"User already has access to {tool_name}", "info")
        else:
            flash("User or tool not found", "error")
        return redirect(url_for("admin.superadmin_dashboard" if session.get("role") == "super_admin" else "admin.admin_dashboard"))
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
        user_role = session.get("role")
        logging.debug(f"User ID: {user_id}, Role: {user_role}")

        # Admins and superadmins have access to all tools
        if user_role in ["admin", "superadmin"]:
            has_access = True
        else:
            # For regular users, check ToolAccess table
            has_access = (
                ToolAccess.query.filter_by(user_id=user_id, tool_name=tool_name).first()
                is not None
            )
        logging.debug(f"Has access: {has_access}")

        if has_access:
            logging.debug(f"Access granted for tool: {tool_name}")
            tool_urls = {
                "Tax Calculator": "tool.unified_tax_calculator",
                "Unified Tax Calculator": "tool.unified_tax_calculator",  # Legacy name
                "Canada Tax Calculator": "tool.unified_tax_calculator",  # Legacy name - redirects to Canada tab
                "Character Counter": "tool.char_counter",
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
