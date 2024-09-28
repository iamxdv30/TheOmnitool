import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from main import create_app
from model.model import db, User, Admin, SuperAdmin, Tool, ToolAccess

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.app_context():
        db.create_all()
    
    yield app
    
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_database(app):
    with app.app_context():
        # Create test users
        user = User(username='testuser', email='test@test.com', fname='Test', lname='User',
                    address='123 Test St', city='Testville', state='TS', zip='12345')
        user.set_password('testpass')
        
        admin = Admin(username='adminuser', email='admin@test.com', fname='Admin', lname='User',
                      address='456 Admin St', city='Adminville', state='AS', zip='67890')
        admin.set_password('adminpass')
        
        superadmin = SuperAdmin(username='superadmin', email='super@test.com', fname='Super', lname='Admin',
                                address='789 Super St', city='Superville', state='SA', zip='24680')
        superadmin.set_password('superpass')
        
        # Create test tools
        tool1 = Tool(name='Test Tool 1', description='A test tool', is_default=True)
        tool2 = Tool(name='Test Tool 2', description='Another test tool', is_default=False)
        
        db.session.add_all([user, admin, superadmin, tool1, tool2])
        db.session.commit()
        
        # Assign tool access
        tool_access = ToolAccess(user_id=user.id, tool_name=tool1.name)
        db.session.add(tool_access)
        db.session.commit()

    yield db

@pytest.fixture
def logged_in_user(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    yield
    client.get('/logout')

@pytest.fixture
def logged_in_admin(client):
    client.post('/login', data={'username': 'adminuser', 'password': 'adminpass'})
    yield
    client.get('/logout')

@pytest.fixture
def logged_in_superadmin(client):
    client.post('/login', data={'username': 'superadmin', 'password': 'superpass'})
    yield
    client.get('/logout')