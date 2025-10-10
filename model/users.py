from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import logging

from .base import db, BcryptPasswordHasher


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Legacy fields (kept for backward compatibility with existing database)
    fname = db.Column(db.String(50), nullable=True)
    lname = db.Column(db.String(50), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    zip = db.Column(db.String(10), nullable=True)

    # Core user fields
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column("password", db.String(128), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='user')

    # Email verification fields
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verification_token = db.Column(db.String(255), nullable=True)
    email_verification_sent_at = db.Column(db.DateTime, nullable=True)

    # OAuth integration fields
    oauth_provider = db.Column(db.String(50), nullable=True)
    oauth_id = db.Column(db.String(255), nullable=True)
    requires_password_setup = db.Column(db.Boolean, default=False)

    # Account management fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
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

    def __init__(self, name=None, username=None, email=None, role='user',
                 oauth_provider=None, oauth_id=None, email_verified=False,
                 requires_password_setup=False, fname=None, lname=None,
                 address=None, city=None, state=None, zip=None, **kwargs):
        super().__init__(**kwargs)

        # Set name field (required)
        if name is not None:
            self.name = name
            # Also parse into fname/lname for backward compatibility
            name_parts = name.strip().split()
            if len(name_parts) == 1:
                self.fname = name_parts[0]
                self.lname = "User"
            elif len(name_parts) >= 2:
                self.fname = name_parts[0]
                self.lname = " ".join(name_parts[1:])
        elif fname is not None and lname is not None:
            # Legacy: if fname/lname provided, combine into name
            self.fname = fname
            self.lname = lname
            self.name = f"{fname} {lname}"
        else:
            # Fallback
            self.name = username if username else "Unknown"

        if username is not None:
            self.username = username
        if email is not None:
            self.email = email
        if role is not None:
            self.role = role

        # Set address fields with defaults (optional now)
        self.address = address if address is not None else ""
        self.city = city if city is not None else ""
        self.state = state if state is not None else ""
        self.zip = zip if zip is not None else ""

        # Set authentication fields
        if oauth_provider is not None:
            self.oauth_provider = oauth_provider
        if oauth_id is not None:
            self.oauth_id = oauth_id
        self.email_verified = email_verified if email_verified is not None else False
        if requires_password_setup is not None:
            self.requires_password_setup = requires_password_setup

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