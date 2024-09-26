from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
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

    
    def has_tool_access(self, tool_name):
        return ToolAccess.query.filter_by(user_id=self.id, tool_name=tool_name).first() is not None
    
    @classmethod
    def user_has_tool_access(cls, user_id, tool_name):
        return ToolAccess.query.filter_by(user_id=user_id, tool_name=tool_name).first() is not None

    
    @classmethod
    def assign_default_tools(cls, user_id):
        user = cls.query.get(user_id)
        if not user:
            raise ValueError(f"No user found with id {user_id}")
        default_tools = Tool.query.filter_by(is_default=True).all()
        for tool in default_tools:
            if not ToolAccess.query.filter_by(user_id=user.id, tool_name=tool.name).first():
                tool_access = ToolAccess(user_id=user.id, tool_name=tool.name)
                db.session.add(tool_access)
        db.session.commit()

    @classmethod
    def check_password(cls, user, password):
        # UPDATED: Use cls to refer to the class instead of self
        return check_password_hash(user.password, password)

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
        new_user = UserFactory.create_user(**user_data)
        db.session.add(new_user)
        db.session.commit()  # This ensures the user has an ID
        User.assign_default_tools(new_user.id)  # Now we can assign default tools
        return new_user

    def update_user(self, user_id, user_data):
        user = User.query.get(user_id)
        if user and user.role == "user":
            for key, value in user_data.items():
                if key == "password":
                    user.set_password(value)
                else:
                    setattr(user, key, value)
            db.session.commit()

    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if user and user.role == "user":
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
            if new_role == "admin" and not isinstance(user, Admin):
                new_admin = Admin(
                    username=user.username,
                    email=user.email,
                    fname=user.fname,
                    lname=user.lname,
                    address=user.address,
                    city=user.city,
                    state=user.state,
                    zip=user.zip
                )
                new_admin.password = user.password  # Copy hashed password
                db.session.delete(user)
                db.session.add(new_admin)
            elif new_role == "user" and isinstance(user, (Admin, SuperAdmin)):
                new_user = User(
                    username=user.username,
                    email=user.email,
                    fname=user.fname,
                    lname=user.lname,
                    address=user.address,
                    city=user.city,
                    state=user.state,
                    zip=user.zip
                )
                new_user.password = user.password  # Copy hashed password
                db.session.delete(user)
                db.session.add(new_user)
            db.session.commit()

    def create_user(self, user_data):
        return super().create_user(user_data)
    
    def update_user(self, user_id, user_data):
        user = User.query.get(user_id)
        if user:
            for key, value in user_data.items():
                if key == "password":
                    user.set_password(value)
                else:
                    setattr(user, key, value)
            db.session.commit()

    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
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

    @classmethod
    def get_distinct_tool_names(cls):
        distinct_tools = [row[0] for row in db.session.query(cls.tool_name).distinct().all()]
        print("Distinct tools from database:", distinct_tools)
        return distinct_tools
    
    @classmethod
    def user_has_access(cls, user_id, tool_name):
        return cls.query.filter_by(user_id=user_id, tool_name=tool_name).first() is not None

    def __init__(self, user_id, tool_name):
        self.user_id = user_id
        self.tool_name = tool_name

    def __repr__(self):
        return f"<ToolAccess(user_id={self.user_id}, tool_name={self.tool_name})>"
    
class Tool(db.Model):
    __tablename__ = 'tools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    is_default = db.Column(db.Boolean, default=False)

    def __init__(self, name, description, is_default=False):
        self.name = name
        self.description = description
        self.is_default = is_default

    @classmethod
    def get_default_tools(cls):
        return cls.query.filter_by(is_default=True).all()

    @classmethod
    def assign_default_tools_to_user(cls, user_id):
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"No user found with id {user_id}")
        default_tools = cls.get_default_tools()
        for tool in default_tools:
            if not ToolAccess.query.filter_by(user_id=user.id, tool_name=tool.name).first():
                tool_access = ToolAccess(user_id=user.id, tool_name=tool.name)
                db.session.add(tool_access)
        db.session.commit()

    @classmethod
    def assign_default_tool_to_all_users(cls, tool_name):
        users = User.query.all()
        for user in users:
            if not user.has_tool_access(tool_name):
                new_access = ToolAccess(user_id=user.id, tool_name=tool_name)
                db.session.add(new_access)
        db.session.commit()

    @classmethod
    def remove_default_tool_from_users(cls, tool_name):
        ToolAccess.query.filter_by(tool_name=tool_name).delete()
        db.session.commit()
    
    


# Design Pattern: Factory Pattern
# The UserFactory class implements the Factory Pattern, providing a centralized way to create different types of users.
class UserFactory:
    @staticmethod
    def create_user(**kwargs):
        role = kwargs.pop('role', 'user')
        if role == "user":
            user = User(**kwargs)
        elif role == "admin":
            user = Admin(**kwargs)
        elif role == "super_admin":
            user = SuperAdmin(**kwargs)
        else:
            raise ValueError("Invalid user role")
        user.set_password(kwargs.pop('password'))
        return user




# Date: September 23, 2024