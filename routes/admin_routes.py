from flask import Blueprint, request, jsonify, redirect, url_for, render_template, session, flash, get_flashed_messages
from model.model import User, Admin, SuperAdmin, Tool, ToolAccess, db
from sqlalchemy.exc import SQLAlchemyError
import logging

admin = Blueprint('admin', __name__)

@admin.route("/admin_dashboard", methods=["GET"])
def admin_dashboard():
    if "logged_in" in session and session.get("role") in ["admin", "super_admin"]:
        users = User.query.all()
        tools = ToolAccess.get_distinct_tool_names()
        user_tools = {user.id: [access.tool_name for access in user.tool_access] for user in users}
        return render_template("admin_dashboard.html", users=users, tools=tools, user_tools=user_tools)
    return redirect(url_for("auth.login"))

@admin.route("/superadmin_dashboard", methods=["GET"])
def superadmin_dashboard():
    if "logged_in" in session and session.get("role") == "super_admin":
        users = User.query.all()
        tools = Tool.query.all()  # Fetch all tools, regardless of default status
        user_tools = {user.id: [access.tool_name for access in user.tool_access] for user in users}
        messages = session.pop('_flashes', [])
        return render_template("superadmin_dashboard.html", users=users, tools=tools, user_tools=user_tools, messages=messages)
    return redirect(url_for("auth.login"))

@admin.route("/create_user", methods=["GET", "POST"])
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
                logging.error(f"Database error creating user: {str(e)}")
                flash(f"Error creating user: {str(e)}", "error")
            except Exception as e:
                db.session.rollback()
                logging.error(f"Unexpected error creating user: {str(e)}")
                flash("An unexpected error occurred while creating the user", "error")
            return redirect(url_for("admin.superadmin_dashboard" if session.get("role") == "super_admin" else "admin.admin_dashboard"))
        return render_template("create_user.html")
    return redirect(url_for("auth.login"))

@admin.route("/update_user/<int:user_id>", methods=["POST"])
def update_user(user_id: int):
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
            return redirect(url_for("admin.admin_dashboard"))
        elif session.get("role") == "super_admin":
            return redirect(url_for("admin.superadmin_dashboard"))
    
    return redirect(url_for("auth.login"))

@admin.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if "logged_in" in session and session.get("role") in ["admin", "super_admin"]:
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            flash("User deleted successfully", "success")

        if session.get("role") == "admin":
            return redirect(url_for("admin.admin_dashboard"))
        elif session.get("role") == "super_admin":
            return redirect(url_for("admin.superadmin_dashboard"))
    return redirect(url_for("auth.login"))

@admin.route("/change_user_role/<int:user_id>", methods=["POST"])
def change_user_role(user_id):
    if "logged_in" in session and session.get("role") == "super_admin":
        new_role = request.form.get("new_role")
        SuperAdmin().change_user_role(user_id, new_role)
        flash(f"User role changed to {new_role}", "success")
        return redirect(url_for("admin.superadmin_dashboard"))
    return redirect(url_for("auth.login"))

@admin.route('/manage_tools', methods=['GET', 'POST', 'DELETE'])
def manage_tools():
    if "logged_in" not in session or session.get("role") not in ["admin", "super_admin"]:
        flash("You don't have permission to manage tools.", "error")
        return redirect(url_for("auth.login"))

    if request.method == 'POST':
        # Handle both creation and updates
        tool_id = request.form.get('tool_id')
        tool_name = request.form.get('tool_name')
        is_default = 'is_default' in request.form
        description = request.form.get('description', '')

        if tool_id:
            # This is an update operation
            tool = Tool.query.get(tool_id)
            if tool:
                tool.name = tool_name
                tool.is_default = is_default
                tool.description = description
                db.session.commit()
                flash("Tool updated successfully", "success")
            else:
                flash("Tool not found", "error")
        else:
            # This is a create operation
            existing_tool = Tool.query.filter_by(name=tool_name).first()
            if existing_tool:
                flash("A tool with this name already exists.", "error")
            else:
                new_tool = Tool(name=tool_name, description=description, is_default=is_default)
                db.session.add(new_tool)
                db.session.commit()
                flash("Tool created successfully", "success")

    elif request.method == 'DELETE':
        # Handle deletion
        tool_id = request.form.get('tool_id')
        if tool_id is None:
            return jsonify({"error": "No tool_id provided"}), 400
        
        tool = Tool.query.get(tool_id)
        if tool:
            db.session.delete(tool)
            db.session.commit()
            return jsonify({"message": "Tool deleted successfully"}), 200
        else:
            return jsonify({"error": "Tool not found"}), 404
        

    # Clear any unused flash messages
    _ = get_flashed_messages()

    tools = Tool.query.all()
    return render_template('manage_tools.html', tools=tools)




