"""
Admin API Integration Tests

Tests for /api/v1/admin/* endpoints: user management, role changes,
tool-access grants, and tool catalog CRUD.
"""

import pytest


def login(client, username, password):
    return client.post(
        '/api/v1/auth/login',
        json={'username': username, 'password': password},
        content_type='application/json'
    )


class TestAdminUsersAccessControl:
    def test_regular_user_forbidden(self, client, init_database):
        login(client, 'testuser', 'testpass')
        response = client.get('/api/v1/admin/users')
        assert response.status_code == 403
        assert response.get_json()['error']['code'] == 'PERMISSION_DENIED'

    def test_unauthenticated_rejected(self, client, init_database):
        response = client.get('/api/v1/admin/users')
        assert response.status_code == 401

    def test_admin_can_list_users(self, client, init_database):
        login(client, 'adminuser', 'adminpass')
        response = client.get('/api/v1/admin/users')
        assert response.status_code == 200
        data = response.get_json()['data']
        assert data['total'] >= 3
        usernames = {u['username'] for u in data['users']}
        assert 'testuser' in usernames


class TestAdminUsersCRUD:
    def test_admin_create_user(self, client, init_database):
        login(client, 'adminuser', 'adminpass')
        response = client.post(
            '/api/v1/admin/users',
            json={
                'username': 'newuser1',
                'email': 'newuser1@test.com',
                'password': 'newpassword123',
                'fname': 'New',
                'lname': 'User',
                'role': 'user',
            },
            content_type='application/json'
        )
        assert response.status_code == 201
        data = response.get_json()['data']
        assert data['username'] == 'newuser1'
        assert data['role'] == 'user'

    def test_admin_cannot_create_admin(self, client, init_database):
        login(client, 'adminuser', 'adminpass')
        response = client.post(
            '/api/v1/admin/users',
            json={
                'username': 'sneaky_admin',
                'email': 'sneaky@test.com',
                'password': 'newpassword123',
                'role': 'admin',
            },
            content_type='application/json'
        )
        assert response.status_code == 403
        assert response.get_json()['error']['code'] == 'PERMISSION_DENIED'

    def test_superadmin_can_create_admin(self, client, init_database):
        login(client, 'superadmin', 'superpass')
        response = client.post(
            '/api/v1/admin/users',
            json={
                'username': 'newadmin1',
                'email': 'newadmin1@test.com',
                'password': 'newpassword123',
                'role': 'admin',
            },
            content_type='application/json'
        )
        assert response.status_code == 201
        assert response.get_json()['data']['role'] == 'admin'

    def test_create_user_duplicate_username(self, client, init_database):
        login(client, 'adminuser', 'adminpass')
        response = client.post(
            '/api/v1/admin/users',
            json={
                'username': 'testuser',
                'email': 'unique@test.com',
                'password': 'newpassword123',
                'role': 'user',
            },
            content_type='application/json'
        )
        assert response.status_code == 409
        assert response.get_json()['error']['code'] == 'RESOURCE_ALREADY_EXISTS'

    def test_admin_update_regular_user(self, client, init_database):
        login(client, 'adminuser', 'adminpass')
        response = client.put(
            '/api/v1/admin/users/1',
            json={'fname': 'Updated'},
            content_type='application/json'
        )
        assert response.status_code == 200
        assert response.get_json()['data']['fname'] == 'Updated'

    def test_admin_cannot_update_admin(self, client, init_database):
        login(client, 'adminuser', 'adminpass')
        # user id 2 is the admin fixture itself
        response = client.put(
            '/api/v1/admin/users/2',
            json={'fname': 'Nope'},
            content_type='application/json'
        )
        assert response.status_code == 403

    def test_admin_delete_regular_user(self, client, init_database):
        login(client, 'adminuser', 'adminpass')
        response = client.delete('/api/v1/admin/users/1')
        assert response.status_code == 204

    def test_admin_cannot_delete_superadmin(self, client, init_database):
        login(client, 'adminuser', 'adminpass')
        response = client.delete('/api/v1/admin/users/3')
        assert response.status_code == 403


class TestChangeRole:
    def test_admin_cannot_change_role(self, client, init_database):
        login(client, 'adminuser', 'adminpass')
        response = client.post(
            '/api/v1/admin/change-role/1',
            json={'role': 'admin'},
            content_type='application/json'
        )
        assert response.status_code == 403

    def test_superadmin_promotes_user_to_admin(self, client, init_database):
        login(client, 'superadmin', 'superpass')
        response = client.post(
            '/api/v1/admin/change-role/1',
            json={'role': 'admin'},
            content_type='application/json'
        )
        assert response.status_code == 200
        assert response.get_json()['data']['role'] == 'admin'

    def test_superadmin_promotes_user_to_superadmin(self, client, init_database):
        login(client, 'superadmin', 'superpass')
        response = client.post(
            '/api/v1/admin/change-role/1',
            json={'role': 'superadmin'},
            content_type='application/json'
        )
        assert response.status_code == 200
        assert response.get_json()['data']['role'] == 'superadmin'


class TestToolAccess:
    def test_grant_and_revoke_tool_access(self, client, init_database):
        login(client, 'adminuser', 'adminpass')

        grant = client.post(
            '/api/v1/admin/grant-tool-access',
            json={'user_id': 1, 'tool_name': 'Test Tool 2'},
            content_type='application/json'
        )
        assert grant.status_code == 200

        users = client.get('/api/v1/admin/users').get_json()['data']['users']
        user1 = next(u for u in users if u['id'] == 1)
        assert 'Test Tool 2' in user1['tools']

        revoke = client.post(
            '/api/v1/admin/revoke-tool-access',
            json={'user_id': 1, 'tool_name': 'Test Tool 2'},
            content_type='application/json'
        )
        assert revoke.status_code == 200

        users = client.get('/api/v1/admin/users').get_json()['data']['users']
        user1 = next(u for u in users if u['id'] == 1)
        assert 'Test Tool 2' not in user1['tools']


class TestToolCatalog:
    def test_admin_can_list_tools(self, client, init_database):
        login(client, 'adminuser', 'adminpass')
        response = client.get('/api/v1/admin/tools')
        assert response.status_code == 200
        names = {t['name'] for t in response.get_json()['data']['tools']}
        assert 'Test Tool 1' in names

    def test_admin_cannot_create_tool(self, client, init_database):
        login(client, 'adminuser', 'adminpass')
        response = client.post(
            '/api/v1/admin/tools',
            json={
                'name': 'new-tool',
                'display_name': 'New Tool',
                'description': 'desc',
                'route': '/tools/new-tool',
                'is_default': False,
            },
            content_type='application/json'
        )
        assert response.status_code == 403

    def test_superadmin_tool_crud(self, client, init_database):
        login(client, 'superadmin', 'superpass')

        create = client.post(
            '/api/v1/admin/tools',
            json={
                'name': 'new-tool',
                'display_name': 'New Tool',
                'description': 'desc',
                'route': '/tools/new-tool',
                'is_default': False,
            },
            content_type='application/json'
        )
        assert create.status_code == 201
        tool_id = create.get_json()['data']['id']

        update = client.put(
            f'/api/v1/admin/tools/{tool_id}',
            json={'display_name': 'Renamed Tool', 'is_default': True},
            content_type='application/json'
        )
        assert update.status_code == 200
        assert update.get_json()['data']['display_name'] == 'Renamed Tool'

        delete = client.delete(f'/api/v1/admin/tools/{tool_id}')
        assert delete.status_code == 204
