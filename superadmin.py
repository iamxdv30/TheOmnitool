import sys
import os
from flask_admin import Admin  # Add this import
from flask_login import current_user  # Add this import
from flask_admin.contrib.sqla import ModelView  # Add this import

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main')))

# Ensure 'main' is a package
# Add __init__.py in the main directory

from main import db  # Ensure 'main' is a package
from main.model import User  # Ensure 'main' is a package

# Initialize the admin object
admin = Admin()  # Add this line

class CustomUserAdmin(ModelView):
    # Only allow superadmin to access these actions
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_superadmin

    # Action to make a user an admin
    def make_admin(self, user_id):
        user = User.query.get(user_id)
        if user:
            user.is_admin = True
            db.session.commit()

    # Action to make an admin a user
    def make_user(self, user_id):
        user = User.query.get(user_id)
        if user:
            user.is_admin = False
            db.session.commit()

    # Action to delete a user
    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()

# Register the custom admin view
admin.add_view(CustomUserAdmin(User, db.session))