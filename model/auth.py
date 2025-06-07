from .users import User, Admin, SuperAdmin


# Design Pattern: Factory Pattern for User Creation
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