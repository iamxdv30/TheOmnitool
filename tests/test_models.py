import pytest
from model.model import User, Admin, SuperAdmin, Tool, ToolAccess, db
from werkzeug.security import check_password_hash

def test_user_creation(app):
    with app.app_context():
        user = User(username='testuser', email='test@test.com', fname='Test', lname='User',
                    address='123 Test St', city='Testville', state='TS', zip='12345')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()

        fetched_user = User.query.filter_by(username='testuser').first()
        assert fetched_user is not None
        assert fetched_user.email == 'test@test.com'
        assert check_password_hash(fetched_user.password, 'testpass')

def test_admin_creation(app):
    with app.app_context():
        admin = Admin(username='adminuser', email='admin@test.com', fname='Admin', lname='User',
                      address='456 Admin St', city='Adminville', state='AS', zip='67890')
        admin.set_password('adminpass')
        db.session.add(admin)
        db.session.commit()

        fetched_admin = Admin.query.filter_by(username='adminuser').first()
        assert fetched_admin is not None
        assert fetched_admin.role == 'admin'

def test_tool_access(app):
    with app.app_context():
        user = User(username='tooluser', email='tool@test.com', fname='Tool', lname='User',
                    address='789 Tool St', city='Toolville', state='TL', zip='13579')
        user.set_password('testpass')  # Set a password
        db.session.add(user)
        db.session.commit()

        tool = Tool(name='Test Tool', description='A test tool', is_default=False)
        db.session.add(tool)
        db.session.commit()

        tool_access = ToolAccess(user_id=user.id, tool_name=tool.name)
        db.session.add(tool_access)
        db.session.commit()

        assert user.has_tool_access(tool.name)