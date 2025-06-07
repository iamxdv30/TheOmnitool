from flask_sqlalchemy import SQLAlchemy
from abc import ABC, abstractmethod
import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import logging

logging.basicConfig(level=logging.DEBUG)

# Initialize SQLAlchemy instance
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