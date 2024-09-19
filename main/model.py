from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import bcrypt

Base = declarative_base()

class User(Base):
    """Represents a user in the system."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # Unique identifier for the user
    fname = Column(String(50), nullable=False)  # User's first name
    lname = Column(String(50), nullable=False)  # User's last name
    address = Column(String(200), nullable=False)  # User's address
    city = Column(String(50), nullable=False)  # User's city
    state = Column(String(50), nullable=False)  # User's state
    zip = Column(String(10), nullable=False)  # User's postal code
    username = Column(String(50), unique=True, nullable=False)  # Unique username for the user
    email = Column(String(100), unique=True, nullable=False)  # Unique email for the user
    _password = Column("password", String(128), nullable=False)  # Use hashed passwords
    is_admin = Column(Boolean, default=False)  # Indicates if the user is an admin
    
    def __repr__(self):
        """Return a string representation of the User object."""
        return f"<User(username={self.username}, email={self.email}, is_admin={self.is_admin})>"

    def set_password(self, password: str):
        """Hashes and sets the password.
        
        Args:
            password (str): The password to be hashed and set.
        """
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self._password = hashed.decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Checks if the provided password matches the stored hashed password.
        
        Args:
            password (str): The password to check against the stored hash.
        
        Returns:
            bool: True if the password matches, False otherwise.
        """
        return bcrypt.checkpw(password.encode('utf-8'), self._password.encode('utf-8'))

class Admin(User):
    """Represents an admin user, inheriting from User."""
    __tablename__ = 'admins'
    
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)  # Unique identifier for the admin
    admin_level = Column(Integer, nullable=False)  # Level of admin privileges

    def __repr__(self):
        """Return a string representation of the Admin object."""
        return f"<Admin(username={self.username}, email={self.email}, admin_level={self.admin_level})>"

class Order(Base):
    """Represents an order made by a user."""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)  # Unique identifier for the order
    user_id = Column(Integer, ForeignKey('users.id'))  # Foreign key linking to the user who made the order
    total_amount = Column(Integer, nullable=False)  # Total amount for the order
    
    user = relationship('User', back_populates='orders')  # Relationship to the User model

User.orders = relationship('Order', back_populates='user')  # Establishes a relationship between User and Order
