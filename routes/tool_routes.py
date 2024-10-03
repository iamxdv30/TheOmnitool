from flask import Blueprint, request, jsonify, redirect, url_for, render_template, session, flash, make_response
from model.model import User, ToolAccess, Tool, db, EmailTemplate
from functools import wraps
import pytz
from datetime import datetime
from Tools.char_counter import count_characters
from Tools.tax_calculator import tax_calculator as calculate_tax
import logging

tool = Blueprint('tool', __name__)

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

            if user_role not in ["admin", "superadmin"] and not User.user_has_tool_access(user_id, tool_name):
                flash(f"You don't have access to {tool_name}. Please contact an administrator.", "error")
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
        return render_template(
            "canada_tax_calculator.html", result=result, data=data
        )
    else:
        data = {}
        return render_template("canada_tax_calculator.html", data=data)

@tool.route("/email_templates", methods=["GET", "POST", "PUT", "DELETE"])
@tool_access_required("Email Templates")
def email_templates():
    if "user_id" not in session:
        flash("You must be logged in to access this feature.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "GET":
        templates = EmailTemplate.query.filter_by(user_id=session["user_id"]).all()
        return render_template("email_templates.html", templates=templates)
    
    elif request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        if not title or not content:
            flash("Both title and content are required.", "error")
        else:
            try:
                new_template = EmailTemplate(
                    user_id=session["user_id"],
                    title=title,
                    content=content
                )
                db.session.add(new_template)
                db.session.commit()
                flash("Email template added successfully!", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred while adding the template: {str(e)}", "error")
    
    elif request.method in ["PUT", "DELETE"]:
        template_id = request.form.get("template_id")
        if not template_id:
            flash("Template ID is required for update and delete operations.", "error")
        else:
            template = EmailTemplate.query.get(template_id)
            if not template:
                flash("Template not found.", "error")
            elif template.user_id != session["user_id"]:
                flash("You don't have permission to modify this template.", "error")
            else:
                try:
                    if request.method == "PUT":
                        template.title = request.form.get("title")
                        template.content = request.form.get("content")
                        flash("Email template updated successfully!", "success")
                    elif request.method == "DELETE":
                        db.session.delete(template)
                        flash("Email template deleted successfully!", "success")
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    flash(f"An error occurred: {str(e)}", "error")
    
    return redirect(url_for("tool.email_templates"))
    
    #Admin capabilities to handle tool access

@tool.route("/grant_tool_access", methods=["POST"])
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
        return redirect(url_for("admin.superadmin_dashboard" if session.get("role") == "super_admin" else "admin.admin_dashboard"))
    return redirect(url_for("auth.login"))

@tool.route("/revoke_tool_access", methods=["POST"])
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
        return redirect(url_for("admin.superadmin_dashboard" if session.get("role") == "super_admin" else "admin.admin_dashboard"))
    return redirect(url_for("auth.login"))

@tool.route("/check_tool_access/<tool_name>")
def check_tool_access(tool_name):
    logging.debug(f"Checking access for tool: {tool_name}")
    if "logged_in" in session:
        user_id = session.get('user_id')
        logging.debug(f"User ID: {user_id}")
        
        has_access = ToolAccess.query.filter_by(user_id=user_id, tool_name=tool_name).first() is not None
        logging.debug(f"Has access: {has_access}")
        
        if has_access:
            logging.debug(f"Access granted for tool: {tool_name}")
            tool_urls = {
                "Tax Calculator": url_for("tool.tax_calculator_route"),
                "Character Counter": url_for("tool.char_counter"),
                "Canada Tax Calculator": url_for("tool.canada_tax_calculator"),
                "Unix Timestamp Converter": url_for("tool.convert"),
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
                    return redirect(url_for("user.user_dashboard"))
        else:
            message = f"You don't have access to {tool_name}. Please contact an administrator."
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"access": False, "message": message})
            else:
                flash(message, "error")
                return redirect(url_for("user.user_dashboard"))
    
    message = "Please log in to access tools."
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"access": False, "message": message})
    else:
        flash(message, "error")
        return redirect(url_for("auth.login"))