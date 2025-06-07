from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import logging

from .base import db, BcryptPasswordHasher


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
    
    # Relationships
    usage_logs = db.relationship(
        "UsageLog", back_populates="user", cascade="all, delete-orphan"
    )
    tool_access = db.relationship(
        "ToolAccess", back_populates="user", cascade="all, delete-orphan"
    )
    email_templates = db.relationship(
        "EmailTemplate", order_by="EmailTemplate.id", 
        back_populates="user", cascade="all, delete-orphan"
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
        from .tools import ToolAccess
        return ToolAccess.query.filter_by(user_id=self.id, tool_name=tool_name).first() is not None
    
    @classmethod
    def user_has_tool_access(cls, user_id, tool_name):
        from .tools import ToolAccess
        return ToolAccess.query.filter_by(user_id=user_id, tool_name=tool_name).first() is not None

    @classmethod
    def assign_default_tools(cls, user_id):
        from .tools import Tool, ToolAccess
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
        return check_password_hash(user.password, password)

    def __repr__(self):
        return f"<{self.__class__.__name__}(username={self.username}, email={self.email})>"


class Admin(User):
    __tablename__ = "admins"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    admin_level = db.Column(db.Integer, nullable=False)

    __mapper_args__ = {"polymorphic_identity": "admin"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = "admin"
        if "admin_level" not in kwargs:
            self.admin_level = 1

    def view_user_activity(self, user_id):
        from .tools import UsageLog
        return UsageLog.query.filter_by(user_id=user_id).all()

    def create_user(self, user_data):
        from .auth import UserFactory
        new_user = UserFactory.create_user(**user_data)
        db.session.add(new_user)
        db.session.commit()
        User.assign_default_tools(new_user.id)
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
        from .tools import ToolAccess
        access = ToolAccess(user_id=user_id, tool_name=tool_name)
        db.session.add(access)
        db.session.commit()

    def revoke_tool_access(self, user_id, tool_name):
        from .tools import ToolAccess
        ToolAccess.query.filter_by(user_id=user_id, tool_name=tool_name).delete()
        db.session.commit()


class SuperAdmin(Admin):
    __tablename__ = "super_admins"

    id = db.Column(db.Integer, db.ForeignKey("admins.id"), primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "super_admin"}

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
                new_admin.password = user.password
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
                new_user.password = user.password
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
        from .tools import UsageLog
        return UsageLog.query.all()