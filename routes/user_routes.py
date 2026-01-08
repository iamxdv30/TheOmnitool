from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from model import User, db, ToolAccess
from werkzeug.security import generate_password_hash
import logging

# Use centralized logging configured in main.py
logger = logging.getLogger(__name__)

user = Blueprint('user', __name__)

@user.route("/")
def index():
    return render_template("index.html")

@user.route('/about')
def about_page():
    """Renders the about page."""
    return render_template('about.html')

@user.route("/user_dashboard", methods=["GET"])
def user_dashboard():
    logging.debug("Entering user_dashboard route")
    if "logged_in" not in session:
        logging.debug("User not logged in, redirecting to login")
        return redirect(url_for("auth.login"))

    role = session.get("role")
    logging.debug(f"User role: {role}")
    if role == "admin":
        logging.debug("Redirecting admin to admin_dashboard")
        return redirect(url_for("admin.admin_dashboard"))
    elif role == "super_admin":
        logging.debug("Redirecting super_admin to superadmin_dashboard")
        return redirect(url_for("admin.superadmin_dashboard"))

    username = session.get("username")
    logging.debug(f"Username: {username}")
    user = User.query.filter_by(username=username).first()
    if user:
        user_tools = [access.tool_name for access in ToolAccess.query.filter_by(user_id=user.id).all()]
        logging.debug(f"User tools: {user_tools}")
        session["user_tools"] = user_tools  # Update session
        return render_template("user_dashboard.html", user=user, user_tools=user_tools)
    else:
        logging.error(f"User not found for username: {username}")
        flash("User not found. Please log in again.", "error")
        return redirect(url_for("auth.logout"))

@user.route("/profile", methods=["GET"])
def profile():
    if "logged_in" in session:
        username = session.get("username")
        if username:
            user = User.query.filter_by(username=username).first()
            if user:
                return render_template("profile.html", user=user)
            else:
                flash("User not found. Please log in again.", "error")
                return redirect(url_for("auth.logout"))
        else:
            flash("Session error. Please log in again.", "error")
            return redirect(url_for("auth.logout"))
    return redirect(url_for("auth.login"))

@user.route("/update_profile", methods=["POST"])
def update_profile():
    if "logged_in" in session:
        username = session.get("username")
        if username:
            user = User.query.filter_by(username=username).first()
            if user:
                user.fname = request.form["fname"]
                user.lname = request.form["lname"]
                user.address = request.form["address"]
                user.city = request.form["city"]
                user.state = request.form["state"]
                user.zip = request.form["zip"]
                db.session.commit()
                flash("Profile updated successfully!", "success")
                return redirect(url_for("user.profile"))
            else:
                flash("User not found. Please log in again.", "error")
        else:
            flash("Session error. Please log in again.", "error")
        return redirect(url_for("auth.logout"))
    return redirect(url_for("auth.login"))

@user.route("/change_password", methods=["POST"])
def change_password():
    if "logged_in" in session:
        user = User.query.filter_by(username=session["username"]).first()
        if user:
            if User.check_password(user, request.form["current_password"]):
                if request.form["new_password"] == request.form["confirm_new_password"]:
                    user.set_password(request.form["new_password"])
                    db.session.commit()
                    flash("Password changed successfully!", "success")
                else:
                    flash("New passwords do not match!", "error")
            else:
                flash("Current password is incorrect!", "error")
        else:
            flash("User not found!", "error")
        return redirect(url_for("user.user_dashboard"))
    return redirect(url_for("auth.login"))