from flask_sqlalchemy import SQLAlchemy
import bcrypt
from datetime import datetime
from abc import ABC, abstractmethod
from werkzeug.security import generate_password_hash, check_password_hash
import logging

logging.basicConfig(level=logging.DEBUG)

db = SQLAlchemy()


# Design Pattern: Strategy Pattern
# The PasswordHasher abstract base class and its concrete implementation BcryptPasswordHasher
# demonstrate the Strategy Pattern. This allows for easy swapping of password hashing algorithms.
class PasswordHasher(ABC):
    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass
    

    @abstractmethod
    def check_password(self, password: str, hashed: str) -> bool:
        pass


class BcryptPasswordHasher(PasswordHasher):
    def hash_password(self, password: str) -> str:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    def check_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# Design Pattern: Active Record Pattern
# The User class and its subclasses (Admin, SuperAdmin) implement the Active Record Pattern,
# combining database access with business logic in a single class.
class User(db.Model):
    __tablename__ = "users"

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
    role = db.Column(db.String(20), nullable=False)
    usage_logs = db.relationship(
        "UsageLog", back_populates="user", cascade="all, delete-orphan"
    )
    tool_access = db.relationship(
        "ToolAccess", back_populates="user", cascade="all, delete-orphan"
    )

    __mapper_args__ = {"polymorphic_identity": "user", "polymorphic_on": role}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.password_hasher = BcryptPasswordHasher()

    def set_password(self, password):
        logging.debug(f"Setting password for user {self.username}")
        self.password = generate_password_hash(password, method="pbkdf2:sha256")
        logging.debug(f"Password hash: {self.password}")

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}(username={self.username}, email={self.email})>"
        )


# Design Pattern: Inheritance
# The Admin class inherits from User, demonstrating the use of inheritance to extend functionality.
class Admin(User):
    __tablename__ = "admins"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    admin_level = db.Column(db.Integer, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = "admin"
        if "admin_level" not in kwargs:
            self.admin_level = 1

    def view_user_activity(self, user_id):
        return UsageLog.query.filter_by(user_id=user_id).all()

    def create_user(self, user_data):
        new_user = User(**user_data)
        db.session.add(new_user)
        db.session.commit()

    def update_user(self, user_id, user_data):
        user = User.query.get(user_id)
        if user:
            for key, value in user_data.items():
                setattr(user, key, value)
            db.session.commit()

    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()

    def grant_tool_access(self, user_id, tool_name):
        access = ToolAccess(user_id=user_id, tool_name=tool_name)
        db.session.add(access)
        db.session.commit()

    def revoke_tool_access(self, user_id, tool_name):
        ToolAccess.query.filter_by(user_id=user_id, tool_name=tool_name).delete()
        db.session.commit()


# Design Pattern: Inheritance
# The SuperAdmin class further extends Admin, showing multi-level inheritance.
class SuperAdmin(Admin):
    __tablename__ = "super_admins"

    id = db.Column(db.Integer, db.ForeignKey("admins.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "super_admin",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = "super_admin"
        self.admin_level = 2

    def change_user_role(self, user_id, new_role):
        user = User.query.get(user_id)
        if user:
            if new_role == "admin":
                new_admin = Admin(id=user.id, admin_level=1)
                db.session.delete(user)
                db.session.add(new_admin)
            elif new_role == "user":
                new_user = User(id=user.id)
                db.session.delete(user)
                db.session.add(new_user)
            db.session.commit()

    def view_all_activity(self):
        return UsageLog.query.all()


# Design Pattern: Active Record Pattern
class UsageLog(db.Model):
    __tablename__ = "usage_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    tool_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="usage_logs")

    def __repr__(self):
        return f"<UsageLog(user_id={self.user_id}, tool_name={self.tool_name}, timestamp={self.timestamp})>"


# Design Pattern: Active Record Pattern
class ToolAccess(db.Model):
    __tablename__ = "tool_access"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    tool_name = db.Column(db.String(100), nullable=False)

    user = db.relationship("User", back_populates="tool_access")

    def __init__(self, user_id, tool_name):
        self.user_id = user_id
        self.tool_name = tool_name

    def __repr__(self):
        return f"<ToolAccess(user_id={self.user_id}, tool_name={self.tool_name})>"


# Design Pattern: Factory Pattern
# The UserFactory class implements the Factory Pattern, providing a centralized way to create different types of users.
class UserFactory:
    @staticmethod
    def create_user(role, **kwargs):
        if role == "user":
            return User(**kwargs)
        elif role == "admin":
            return Admin(**kwargs)
        elif role == "super_admin":
            return SuperAdmin(**kwargs)
        else:
            raise ValueError("Invalid user role")


# Design Pattern: Singleton Pattern
# The ToolAccessManager class implements the Singleton Pattern, ensuring only one instance of the class exists.
class ToolAccessManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def check_access(self, user_id, tool_name):
        return (
            ToolAccess.query.filter_by(user_id=user_id, tool_name=tool_name).first()
            is not None
        )


# Date: September 23, 2024