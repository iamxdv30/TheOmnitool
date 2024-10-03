import pytest
from flask import session
from model.model import EmailTemplate, db

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_database(app):
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_add_email_template(client, init_database, app):
    with app.test_request_context():
        login(client, 'testuser', 'testpass')
        session['user_id'] = 1  # Assuming the test user has ID 1
        response = client.post('/email_templates', data=dict(
            title='Test Template',
            content='This is a test template content'
        ))
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert data['message'] == 'Email template added successfully!'

        # Verify the template was added to the database
        template = EmailTemplate.query.filter_by(title='Test Template').first()
        assert template is not None
        assert template.content == 'This is a test template content'

def test_update_email_template(client, init_database, app):
    with app.test_request_context():
        login(client, 'testuser', 'testpass')
        session['user_id'] = 1

        # First, add a template
        client.post('/email_templates', data=dict(
            title='Template to Update',
            content='Original content'
        ))

        # Get the ID of the added template
        template = EmailTemplate.query.filter_by(title='Template to Update').first()
        template_id = template.id

        # Update the template
        response = client.put(f'/email_templates/{template_id}', json=dict(
            title='Updated Template',
            content='Updated content'
        ))
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert data['message'] == 'Email template updated successfully!'

        # Verify the template was updated in the database
        updated_template = EmailTemplate.query.get(template_id)
        assert updated_template.title == 'Updated Template'
        assert updated_template.content == 'Updated content'

def test_delete_email_template(client, init_database, app):
    with app.test_request_context():
        login(client, 'testuser', 'testpass')
        session['user_id'] = 1

        # First, add a template
        client.post('/email_templates', data=dict(
            title='Template to Delete',
            content='Content to delete'
        ))

        # Get the ID of the added template
        template = EmailTemplate.query.filter_by(title='Template to Delete').first()
        template_id = template.id

        # Delete the template
        response = client.delete(f'/email_templates/{template_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert data['message'] == 'Email template deleted successfully!'

        # Verify the template was deleted from the database
        deleted_template = EmailTemplate.query.get(template_id)
        assert deleted_template is None

def test_get_email_templates(client, init_database, app):
    with app.test_request_context():
        login(client, 'testuser', 'testpass')
        session['user_id'] = 1

        # Add a couple of templates
        client.post('/email_templates', data=dict(title='Template 1', content='Content 1'))
        client.post('/email_templates', data=dict(title='Template 2', content='Content 2'))

        # Get all templates
        response = client.get('/email_templates')
        assert response.status_code == 200
        assert b'Template 1' in response.data
        assert b'Template 2' in response.data
