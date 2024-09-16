# main/model.py

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email}, is_admin={self.is_admin})>"

class Admin(User):
    __tablename__ = 'admins'
    
    id = Column(Integer, primary_key=True)
    admin_level = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Admin(username={self.username}, email={self.email}, admin_level={self.admin_level})>"
