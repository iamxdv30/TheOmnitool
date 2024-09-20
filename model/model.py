from flask_sqlalchemy import SQLAlchemy
import bcrypt
from datetime import datetime

# Import db object from app where it's initialized
db = SQLAlchemy()

class User(db.Model):
    """Represents a user in the system."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip = db.Column(db.String(10), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column("password", db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    usage_logs = db.relationship('UsageLog', back_populates='user', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email}, is_admin={self.is_admin})>"

    def set_password(self, password: str):
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.password = hashed.decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

class Admin(User):
    """Represents an admin user, inheriting from User."""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    admin_level = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Admin(username={self.username}, email={self.email}, admin_level={self.admin_level})>"

class UsageLog(db.Model):
    """Represents a log of tool usage by a user."""
    __tablename__ = 'usage_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Unique identifier for each usage log
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key linking to the user
    tool_name = db.Column(db.String(100), nullable=False)  # Name of the tool used (e.g., tax calculator, character counter)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Timestamp when the tool was used
    
    # Establishing a relationship to the User model
    user = db.relationship('User', back_populates='usage_logs')

    def __repr__(self):
        return f"<UsageLog(user_id={self.user_id}, tool_name={self.tool_name}, timestamp={self.timestamp})>"

# Define the relationship from the User side
User.usage_logs = db.relationship('UsageLog', back_populates='user', cascade="all, delete-orphan")


# Date: September 19, 2024
