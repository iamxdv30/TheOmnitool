import email
from flask import Blueprint, request, jsonify, redirect, url_for, render_template, session, flash
from model import User, db, UserFactory
from werkzeug.security import check_password_hash
from functools import wraps
from routes.contact_routes import mail, generate_verification_token
from flask_mail import Message

auth = Blueprint('auth', __name__)

@auth.route("/login", methods=["GET", "POST"])
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
            session["user_tools"] = [access.tool_name for access in user.tool_access]
            
            if user.role == "super_admin":
                return redirect(url_for("admin.superadmin_dashboard"))
            elif user.role == "admin":
                return redirect(url_for("admin.admin_dashboard"))
            else:
                return redirect(url_for("user.user_dashboard"))
        else:
            flash("Invalid username or password!", "error")
    else:
        _ = flash("", "")  # Clear any existing flash messages

    return render_template("login.html")

@auth.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    _ = flash("", "")  # Clear any existing flash messages
    return redirect(url_for("auth.login"))

@auth.route("/register_step1", methods=["GET", "POST"])
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

        return redirect(url_for("auth.register_step2"))

    return render_template("register_step1.html")

@auth.route("/register_step2", methods=["GET", "POST"])
def register_step2():
    registration_info = session.get("registration_info")

    if not registration_info:
        flash("Please complete step 1 of registration first.", "error")
        return redirect(url_for("auth.register_step1"))

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("auth.register_step2"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return redirect(url_for("auth.register_step2"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "error")
            return redirect(url_for("auth.register_step2"))

        try:
            new_user = UserFactory.create_user(
                username=username,
                email=email,
                fname=registration_info['fname'],
                lname=registration_info['lname'],
                address=registration_info['address'],
                city=registration_info['city'],
                state=registration_info['state'],
                zip=registration_info['zip'],
                role='user',
                password=password
            )
            db.session.add(new_user)
            db.session.commit()

            User.assign_default_tools(new_user.id)

            session.pop("registration_info", None)

            flash("Registration successful!", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "error")
            return redirect(url_for("auth.register_step2"))

    return render_template("register_step2.html")

@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()

        # For security, we don't reveal if the user was found or not.
        # We always show a confirmation message.

        if user:
            # Generate a secure, timed token (expires in 1 hour by default)
            token = generate_verification_token(email)
            reset_link = url_for("auth.reset_password", token=token, _external=True)
            
            # Create and send the password reset email
            msg = Message(
                subject="Password Reset Request - OmniTools",
                recipients=[email],
            )

            msg.html = render_template(
                "email/password_reset.html",
                name=user.fname + " " + user.lname,
                reset_link=reset_link,
            )
            mail.send(msg)
            
            # For security, always flash the same message and redirect to login for POST requests.
            flash("If an account with that email exists, a password reset link has been sent.", "info")
        return redirect(url_for("auth.login"))
        
    return render_template("forgot_password_request.html")


from routes.contact_routes import verify_verification_token
@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    # Verify the token is valid and not expired
    email = verify_verification_token(token)

    if not email:
        flash("The password reset link is invalid or has expired.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return render_template("reset_password.html")

        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(password)
            db.session.commit()
            flash("Your password has been updated successfully! You can now log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("reset_password.html")