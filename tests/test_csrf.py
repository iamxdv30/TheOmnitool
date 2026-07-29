"""
CSRF Enforcement Tests

Verifies that mutating /api/v1 requests require a valid X-CSRFToken header
matching the session token when WTF_CSRF_ENABLED is True.
"""

import os
import pytest

from main import create_app
from model import db, User


@pytest.fixture
def csrf_app(monkeypatch):
    from config.auth_config import AuthConfig
    monkeypatch.setattr(AuthConfig, 'RECAPTCHA_SITE_KEY', None)
    monkeypatch.setattr(AuthConfig, 'RECAPTCHA_SECRET_KEY', None)

    app = create_app(test_config={
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': True,  # CSRF enforcement ON
        'SECRET_KEY': os.getenv('SECRET_KEY', 'test-secret-key'),
        'SECURITY_PASSWORD_SALT': os.getenv('SECURITY_PASSWORD_SALT', 'test-salt'),
        'TOKEN_SECRET_KEY': os.getenv('TOKEN_SECRET_KEY', 'test-token-key')
    })

    with app.app_context():
        db.create_all()
        user = User(username='csrfuser', email='csrf@test.com', fname='C', lname='U',
                    address='1 St', city='C', state='S', zip='11111', email_verified=True)
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture
def csrf_client(csrf_app):
    return csrf_app.test_client()


def test_post_without_csrf_token_rejected(csrf_client):
    response = csrf_client.post(
        '/api/v1/auth/login',
        json={'username': 'csrfuser', 'password': 'testpass'},
    )
    assert response.status_code == 403
    assert response.get_json()['error']['code'] == 'CSRF_ERROR'


def test_post_with_wrong_csrf_token_rejected(csrf_client):
    csrf_client.get('/api/v1/auth/csrf')
    response = csrf_client.post(
        '/api/v1/auth/login',
        json={'username': 'csrfuser', 'password': 'testpass'},
        headers={'X-CSRFToken': 'bogus-token'},
    )
    assert response.status_code == 403
    assert response.get_json()['error']['code'] == 'CSRF_ERROR'


def test_post_with_valid_csrf_token_accepted(csrf_client):
    token = csrf_client.get('/api/v1/auth/csrf').get_json()['data']['csrfToken']

    response = csrf_client.post(
        '/api/v1/auth/login',
        json={'username': 'csrfuser', 'password': 'testpass'},
        headers={'X-CSRFToken': token},
    )
    assert response.status_code == 200
    assert response.get_json()['success'] is True


def test_get_requests_do_not_require_csrf(csrf_client):
    response = csrf_client.get('/api/v1/auth/status')
    assert response.status_code == 200
