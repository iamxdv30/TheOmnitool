import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from main import create_app
from model import db, User, Admin, SuperAdmin, Tool, ToolAccess
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def app(monkeypatch):
    # Disable reCAPTCHA for testing by monkeypatching AuthConfig
    from config.auth_config import AuthConfig
    monkeypatch.setattr(AuthConfig, 'RECAPTCHA_SITE_KEY', None)
    monkeypatch.setattr(AuthConfig, 'RECAPTCHA_SECRET_KEY', None)

    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SECRET_KEY': os.getenv('SECRET_KEY', 'test-secret-key'),
        'SECURITY_PASSWORD_SALT': os.getenv('SECURITY_PASSWORD_SALT', 'test-salt'),
        'TOKEN_SECRET_KEY': os.getenv('TOKEN_SECRET_KEY', 'test-token-key')
    })

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
        # Create test users with email verified (for testing purposes)
        user = User(username='testuser', email='test@test.com', fname='Test', lname='User',
                    address='123 Test St', city='Testville', state='TS', zip='12345',
                    email_verified=True)
        user.set_password('testpass')

        admin = Admin(username='adminuser', email='admin@test.com', fname='Admin', lname='User',
                      address='456 Admin St', city='Adminville', state='AS', zip='67890',
                      email_verified=True)
        admin.set_password('adminpass')

        superadmin = SuperAdmin(username='superadmin', email='super@test.com', fname='Super', lname='Admin',
                                address='789 Super St', city='Superville', state='SA', zip='24680',
                                email_verified=True)
        superadmin.set_password('superpass')
        
        # Create test tools
        tool1 = Tool(name='Test Tool 1', description='A test tool', route='/test_tool_1', is_default=True)
        tool2 = Tool(name='Test Tool 2', description='Another test tool', route='/test_tool_2', is_default=False)
        
        db.session.add_all([user, admin, superadmin, tool1, tool2])
        db.session.commit()
        
        # Assign tool access
        tool_access = ToolAccess(user_id=user.id, tool_name=tool1.name)
        db.session.add(tool_access)
        db.session.commit()

    yield db

@pytest.fixture
def logged_in_user(client):
    with client.session_transaction() as session:
        client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
        session['logged_in'] = True
        session['username'] = 'testuser'
        session['role'] = 'user'
    yield
    client.get('/logout')

@pytest.fixture
def logged_in_admin(client):
    with client.session_transaction() as session:
        client.post('/login', data={'username': 'adminuser', 'password': 'adminpass'})
        session['logged_in'] = True
        session['username'] = 'adminuser'
        session['role'] = 'admin'
    yield
    client.get('/logout')

@pytest.fixture
def logged_in_superadmin(client):
    with client.session_transaction() as session:
        client.post('/login', data={'username': 'superadmin', 'password': 'superpass'})
        session['logged_in'] = True
        session['username'] = 'superadmin'
        session['role'] = 'super_admin'
    yield
    client.get('/logout')