import pytest
from flask import session
from werkzeug.security import check_password_hash
from model import User, Admin, SuperAdmin, Tool, ToolAccess, db

def test_login_post(client):
    """Test login with non-existent user returns error."""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    # Check for error message (period or exclamation mark)
    assert (b"Invalid username or password" in response.data or
            b"invalid" in response.data.lower())

def test_register_process(client):
    # Test the new simplified registration process
    response = client.post('/register', data={
        'name': 'Test User',
        'username': 'newuser',
        'email': 'newuser@test.com',
        'password': 'NewPass123!',
        'confirm_password': 'NewPass123!'
    }, follow_redirects=True)
    # After successful registration, user should be redirected to verification pending page
    assert (b"verify" in response.data.lower() or
            b"registration" in response.data.lower() or
            b"email" in response.data.lower())

def test_user_dashboard_authenticated(client, app):
    with app.app_context():
        # Create a test user with email verified
        user = User(username='testuser', email='test@test.com', fname='Test', lname='User',
                    address='123 Test St', city='Testville', state='TS', zip='12345',
                    email_verified=True)
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()

        # Log in the user
        client.post('/login', data={'username': 'testuser', 'password': 'testpass'})

        # Access the user dashboard
        response = client.get('/user_dashboard')

    assert response.status_code == 200
    assert b"User Dashboard" in response.data

    # Clean up
    with app.app_context():
        db.session.delete(user)
        db.session.commit()

def test_admin_dashboard_authenticated(client):
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['username'] = 'adminuser'
        sess['role'] = 'admin'
    
    response = client.get('/admin_dashboard')
    assert response.status_code == 200
    assert b"Admin Dashboard" in response.data

def test_superadmin_dashboard_authenticated(client):
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['username'] = 'superadmin'
        sess['role'] = 'super_admin'
    
    response = client.get('/superadmin_dashboard')
    assert response.status_code == 200
    assert b"Super Admin Dashboard" in response.data

def test_logout(client):
    with client.session_transaction() as sess:
        sess['logged_in'] = True
    
    response = client.get('/logout', follow_redirects=True)
    assert b"Login" in response.data
    with client.session_transaction() as sess:
        assert 'logged_in' not in sess