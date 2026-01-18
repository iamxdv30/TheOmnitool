"""
API Integration Tests

Tests for the JSON API endpoints (/api/v1/*).
These tests verify the API contract, response formats, and authentication flows.
"""

import pytest
import json


class TestAuthAPI:
    """Tests for /api/v1/auth/* endpoints."""

    def test_login_success(self, client, init_database):
        """Test successful login returns user data and sets session."""
        response = client.post(
            '/api/v1/auth/login',
            json={
                'username': 'testuser',
                'password': 'testpass'
            },
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data['success'] is True
        assert 'data' in data
        assert 'user' in data['data']
        assert data['data']['user']['username'] == 'testuser'
        assert data['data']['user']['email'] == 'test@test.com'
        assert 'redirect_route' in data['data']

    def test_login_invalid_credentials(self, client, init_database):
        """Test login with wrong password returns 401."""
        response = client.post(
            '/api/v1/auth/login',
            json={
                'username': 'testuser',
                'password': 'wrongpassword'
            },
            content_type='application/json'
        )

        assert response.status_code == 401
        data = response.get_json()

        assert data['success'] is False
        assert data['error']['code'] == 'AUTH_INVALID_CREDENTIALS'

    def test_login_user_not_found(self, client, init_database):
        """Test login with non-existent user returns 401."""
        response = client.post(
            '/api/v1/auth/login',
            json={
                'username': 'nonexistent',
                'password': 'testpass'
            },
            content_type='application/json'
        )

        assert response.status_code == 401
        data = response.get_json()

        assert data['success'] is False
        assert data['error']['code'] == 'AUTH_INVALID_CREDENTIALS'

    def test_login_missing_fields(self, client, init_database):
        """Test login with missing fields returns validation error."""
        response = client.post(
            '/api/v1/auth/login',
            json={'username': 'testuser'},
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.get_json()

        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'

    def test_login_not_json(self, client, init_database):
        """Test login with non-JSON body returns error."""
        response = client.post(
            '/api/v1/auth/login',
            data='username=test&password=test',
            content_type='application/x-www-form-urlencoded'
        )

        assert response.status_code == 400
        data = response.get_json()

        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'

    def test_logout(self, client, init_database):
        """Test logout clears session."""
        # First login
        client.post(
            '/api/v1/auth/login',
            json={'username': 'testuser', 'password': 'testpass'},
            content_type='application/json'
        )

        # Then logout
        response = client.post('/api/v1/auth/logout')

        assert response.status_code == 200
        data = response.get_json()

        assert data['success'] is True

        # Verify session is cleared
        status_response = client.get('/api/v1/auth/status')
        status_data = status_response.get_json()
        assert status_data['data']['isAuthenticated'] is False

    def test_auth_status_not_authenticated(self, client, init_database):
        """Test auth status when not logged in."""
        response = client.get('/api/v1/auth/status')

        assert response.status_code == 200
        data = response.get_json()

        assert data['success'] is True
        assert data['data']['isAuthenticated'] is False
        assert data['data']['user'] is None

    def test_auth_status_authenticated(self, client, init_database):
        """Test auth status when logged in."""
        # Login first
        client.post(
            '/api/v1/auth/login',
            json={'username': 'testuser', 'password': 'testpass'},
            content_type='application/json'
        )

        response = client.get('/api/v1/auth/status')

        assert response.status_code == 200
        data = response.get_json()

        assert data['success'] is True
        assert data['data']['isAuthenticated'] is True
        assert data['data']['user']['username'] == 'testuser'

    def test_get_csrf_token(self, client, init_database):
        """Test CSRF token generation."""
        response = client.get('/api/v1/auth/csrf')

        assert response.status_code == 200
        data = response.get_json()

        assert data['success'] is True
        assert 'csrfToken' in data['data']
        assert len(data['data']['csrfToken']) == 64  # 32 bytes hex = 64 chars

    def test_register_success(self, client, init_database, monkeypatch):
        """Test successful registration."""
        # Mock email sending
        from services import email_service
        monkeypatch.setattr(
            email_service.EmailService, 'send_verification_email',
            lambda self, email, name: email_service.ServiceResult.success(True)
        )

        # Password must meet requirements: 8+ chars, uppercase, lowercase, number, special
        response = client.post(
            '/api/v1/auth/register',
            json={
                'name': 'New User',
                'username': 'newuser',
                'email': 'new@test.com',
                'password': 'NewPassword123!',
                'confirm_password': 'NewPassword123!'
            },
            content_type='application/json'
        )

        assert response.status_code == 201
        data = response.get_json()

        assert data['success'] is True
        assert 'user_id' in data['data']
        assert data['data']['email'] == 'new@test.com'

    def test_register_username_exists(self, client, init_database):
        """Test registration with existing username fails."""
        response = client.post(
            '/api/v1/auth/register',
            json={
                'name': 'Test User',
                'username': 'testuser',  # Already exists
                'email': 'different@test.com',
                'password': 'NewPassword123!',
                'confirm_password': 'NewPassword123!'
            },
            content_type='application/json'
        )

        assert response.status_code == 409
        data = response.get_json()

        assert data['success'] is False
        assert data['error']['code'] == 'RESOURCE_ALREADY_EXISTS'

    def test_register_email_exists(self, client, init_database):
        """Test registration with existing email fails."""
        response = client.post(
            '/api/v1/auth/register',
            json={
                'name': 'Test User',
                'username': 'uniqueuser',
                'email': 'test@test.com',  # Already exists
                'password': 'NewPassword123!',
                'confirm_password': 'NewPassword123!'
            },
            content_type='application/json'
        )

        assert response.status_code == 409
        data = response.get_json()

        assert data['success'] is False
        assert data['error']['code'] == 'RESOURCE_ALREADY_EXISTS'

    def test_register_passwords_dont_match(self, client, init_database):
        """Test registration with mismatched passwords fails."""
        response = client.post(
            '/api/v1/auth/register',
            json={
                'name': 'Test User',
                'username': 'uniqueuser',
                'email': 'unique@test.com',
                'password': 'password123',
                'confirm_password': 'differentpassword'
            },
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.get_json()

        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'

    def test_forgot_password_always_succeeds(self, client, init_database, monkeypatch):
        """Test forgot password always returns success for security."""
        # Mock email sending
        from services import email_service
        monkeypatch.setattr(
            email_service.EmailService, 'send_password_reset_email',
            lambda self, email, name: email_service.ServiceResult.success(True)
        )

        # Test with existing email
        response = client.post(
            '/api/v1/auth/forgot-password',
            json={'email': 'test@test.com'},
            content_type='application/json'
        )
        assert response.status_code == 200

        # Test with non-existing email (should still return 200)
        response = client.post(
            '/api/v1/auth/forgot-password',
            json={'email': 'nonexistent@test.com'},
            content_type='application/json'
        )
        assert response.status_code == 200

    def test_resend_verification_user_not_found(self, client, init_database):
        """Test resend verification for non-existent user."""
        response = client.post(
            '/api/v1/auth/resend-verification',
            json={'email': 'nonexistent@test.com'},
            content_type='application/json'
        )

        assert response.status_code == 404
        data = response.get_json()

        assert data['success'] is False
        assert data['error']['code'] == 'RESOURCE_NOT_FOUND'


class TestUserAPI:
    """Tests for /api/v1/user/* endpoints."""

    def _login(self, client, username='testuser', password='testpass'):
        """Helper to login a user."""
        client.post(
            '/api/v1/auth/login',
            json={'username': username, 'password': password},
            content_type='application/json'
        )

    def test_get_profile_authenticated(self, client, init_database):
        """Test getting profile when logged in."""
        self._login(client)

        response = client.get('/api/v1/user/profile')

        assert response.status_code == 200
        data = response.get_json()

        assert data['success'] is True
        assert data['data']['username'] == 'testuser'
        assert data['data']['email'] == 'test@test.com'

    def test_get_profile_not_authenticated(self, client, init_database):
        """Test getting profile when not logged in returns 401."""
        response = client.get('/api/v1/user/profile')

        assert response.status_code == 401
        data = response.get_json()

        assert data['success'] is False
        assert data['error']['code'] == 'AUTH_REQUIRED'

    def test_update_profile(self, client, init_database):
        """Test updating profile."""
        self._login(client)

        response = client.patch(
            '/api/v1/user/profile',
            json={
                'fname': 'Updated',
                'lname': 'Name',
                'city': 'New City'
            },
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data['success'] is True
        assert data['data']['fname'] == 'Updated'
        assert data['data']['lname'] == 'Name'
        assert data['data']['city'] == 'New City'

    def test_change_password(self, client, init_database):
        """Test password change."""
        self._login(client)

        # Password must meet requirements: 8+ chars, uppercase, lowercase, number, special
        response = client.put(
            '/api/v1/user/password',
            json={
                'current_password': 'testpass',
                'new_password': 'NewPassword123!',
                'confirm_password': 'NewPassword123!'
            },
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data['success'] is True
        assert 'message' in data['data']

        # Verify can login with new password
        client.post('/api/v1/auth/logout')
        login_response = client.post(
            '/api/v1/auth/login',
            json={'username': 'testuser', 'password': 'NewPassword123!'},
            content_type='application/json'
        )
        assert login_response.status_code == 200

    def test_change_password_wrong_current(self, client, init_database):
        """Test password change with wrong current password."""
        self._login(client)

        response = client.put(
            '/api/v1/user/password',
            json={
                'current_password': 'wrongpassword',
                'new_password': 'NewPassword123!',
                'confirm_password': 'NewPassword123!'
            },
            content_type='application/json'
        )

        assert response.status_code == 401
        data = response.get_json()

        assert data['success'] is False
        assert data['error']['code'] == 'AUTH_INVALID_CREDENTIALS'

    def test_get_user_tools(self, client, init_database):
        """Test getting user's tool list."""
        self._login(client)

        response = client.get('/api/v1/user/tools')

        assert response.status_code == 200
        data = response.get_json()

        assert data['success'] is True
        assert 'tools' in data['data']
        assert isinstance(data['data']['tools'], list)

    def test_get_dashboard(self, client, init_database):
        """Test getting dashboard data."""
        self._login(client)

        response = client.get('/api/v1/user/dashboard')

        assert response.status_code == 200
        data = response.get_json()

        assert data['success'] is True
        assert 'user' in data['data']
        assert 'tools' in data['data']
        assert 'usage' in data['data']


class TestToolAPI:
    """Tests for /api/v1/tools/* endpoints."""

    def _login(self, client, username='testuser', password='testpass'):
        """Helper to login a user."""
        client.post(
            '/api/v1/auth/login',
            json={'username': username, 'password': password},
            content_type='application/json'
        )

    def test_list_tools_authenticated(self, client, init_database):
        """Test listing tools when logged in."""
        self._login(client)

        response = client.get('/api/v1/tools/')

        assert response.status_code == 200
        data = response.get_json()

        assert data['success'] is True
        assert 'tools' in data['data']
        assert isinstance(data['data']['tools'], list)

        # Check tool structure
        if len(data['data']['tools']) > 0:
            tool = data['data']['tools'][0]
            assert 'id' in tool
            assert 'name' in tool
            assert 'hasAccess' in tool

    def test_list_tools_not_authenticated(self, client, init_database):
        """Test listing tools when not logged in returns 401."""
        response = client.get('/api/v1/tools/')

        assert response.status_code == 401
        data = response.get_json()

        assert data['success'] is False
        assert data['error']['code'] == 'AUTH_REQUIRED'

    def test_character_counter(self, client, init_database, app):
        """Test character counter tool."""
        # Give user access to Character Counter
        with app.app_context():
            from model import ToolAccess, Tool, User, db
            user = User.query.filter_by(username='testuser').first()
            tool = Tool(name='Character Counter', description='Count chars', route='/char_counter', is_default=True)
            db.session.add(tool)
            db.session.commit()
            access = ToolAccess(user_id=user.id, tool_name='Character Counter')
            db.session.add(access)
            db.session.commit()

        self._login(client)

        response = client.post(
            '/api/v1/tools/character-counter',
            json={
                'text': 'Hello World',
                'char_limit': 100
            },
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data['success'] is True
        assert 'total_characters' in data['data']
        assert data['data']['total_characters'] == 11

    def test_character_counter_no_access(self, client, init_database):
        """Test character counter without tool access returns 403."""
        self._login(client)

        response = client.post(
            '/api/v1/tools/character-counter',
            json={'text': 'Hello'},
            content_type='application/json'
        )

        assert response.status_code == 403
        data = response.get_json()

        assert data['success'] is False
        assert data['error']['code'] == 'PERMISSION_DENIED'


class TestAPIHealth:
    """Tests for API health endpoint."""

    def test_api_health(self, client, init_database):
        """Test API health endpoint."""
        response = client.get('/api/v1/health')

        assert response.status_code == 200
        data = response.get_json()

        assert data['success'] is True
        assert data['data']['status'] == 'healthy'
        assert data['data']['version'] == 'v1'


class TestAPIResponseFormat:
    """Tests to verify API response format consistency."""

    def test_success_response_format(self, client, init_database):
        """Test that success responses follow the standard format."""
        response = client.get('/api/v1/auth/status')
        data = response.get_json()

        # Must have success and data keys
        assert 'success' in data
        assert 'data' in data
        assert data['success'] is True
        # Should not have error key on success
        assert 'error' not in data

    def test_error_response_format(self, client, init_database):
        """Test that error responses follow the standard format."""
        response = client.post(
            '/api/v1/auth/login',
            json={'username': 'nonexistent', 'password': 'wrong'},
            content_type='application/json'
        )
        data = response.get_json()

        # Must have success and error keys
        assert 'success' in data
        assert 'error' in data
        assert data['success'] is False
        # Error must have code and message
        assert 'code' in data['error']
        assert 'message' in data['error']
        # Should not have data key on error
        assert 'data' not in data
