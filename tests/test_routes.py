import pytest
from flask import session
from werkzeug.security import check_password_hash
from model.model import User, Admin, SuperAdmin, Tool, ToolAccess, db

def test_login_post(client):
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    assert b"Invalid username or password!" in response.data

def test_register_process(client):
    # Step 1
    response = client.post('/register_step1', data={
        'fname': 'Test',
        'lname': 'User',
        'address': '123 Test St',
        'city': 'Testville',
        'state': 'TS',
        'zip': '12345'
    }, follow_redirects=True)
    assert b"Step 2" in response.data

    # Step 2
    response = client.post('/register_step2', data={
        'username': 'newuser',
        'email': 'newuser@test.com',
        'password': 'newpass',
        'confirm_password': 'newpass'
    }, follow_redirects=True)
    assert b"Registration successful!" in response.data

def test_user_dashboard_authenticated(client, app):
    with app.app_context():
        # Create a test user
        user = User(username='testuser', email='test@test.com', fname='Test', lname='User',
                    address='123 Test St', city='Testville', state='TS', zip='12345')
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