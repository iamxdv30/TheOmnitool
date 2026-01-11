from datetime import datetime
from .base import db


class UsageLog(db.Model):
    __tablename__ = "usage_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    tool_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="usage_logs")

    def __repr__(self):
        return f"<UsageLog(user_id={self.user_id}, tool_name={self.tool_name}, timestamp={self.timestamp})>"


class EmailTemplate(db.Model):
    __tablename__ = "email_templates"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

    user = db.relationship("User", back_populates="email_templates")

    def __init__(self, user_id: int, title: str, content: str):
        self.user_id = user_id
        self.title = title
        self.content = content


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
    route = db.Column(db.String(255), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, description, route, is_default=False, is_active=True):
        self.name = name
        self.description = description
        self.route = route
        self.is_default = is_default
        self.is_active = is_active

    @classmethod
    def get_default_tools(cls):
        return cls.query.filter_by(is_default=True).all()

    @classmethod
    def assign_default_tools_to_user(cls, user_id):
        from .users import User  # Import here to avoid circular imports
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
        from .users import User  # Import here to avoid circular imports
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