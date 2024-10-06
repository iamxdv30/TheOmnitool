import pytest
from flask import session
from model.model import EmailTemplate, db, User, Tool, ToolAccess
from sqlalchemy.exc import IntegrityError

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_database(app):
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def logged_in_user(client, app, init_database):
    with app.app_context():
        username = "usertesting"
        email = "usertesting@test.com"
        
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(
                username=username,
                email=email,
                fname="User",
                lname="Testing",
                address="123 Test St",
                city="Testville",
                state="TS",
                zip="12345",
            )
            user.set_password("testpass")
            db.session.add(user)
            db.session.commit()

        # Ensure Email Templates tool exists and user has access
        tool = Tool.query.filter_by(name="Email Templates").first()
        if not tool:
            tool = Tool(name="Email Templates", description="Email template tool", is_default=True)
            db.session.add(tool)
            db.session.commit()

        if not ToolAccess.query.filter_by(user_id=user.id, tool_name="Email Templates").first():
            tool_access = ToolAccess(user_id=user.id, tool_name="Email Templates")
            db.session.add(tool_access)
            db.session.commit()

        login(client, username, "testpass")
        
        # Return the user object
        yield User.query.get(user.id)
        
    logout(client)

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get("/logout", follow_redirects=True)

@pytest.fixture
def email_template_access(app, logged_in_user):
    def _check_access(user_id):
        with app.app_context():
            user = User.query.get(user_id)
            if not user:
                return False

            if not ToolAccess.query.filter_by(user_id=user.id, tool_name="Email Templates").first():
                tool_access = ToolAccess(user_id=user.id, tool_name="Email Templates")
                db.session.add(tool_access)
                db.session.commit()
        
        return True
    return _check_access

def test_add_email_template(client, init_database, app, logged_in_user, email_template_access):
    with app.app_context():
        # Refresh the user object within this context
        user = User.query.get(logged_in_user.id)
        assert user is not None, "User not found in the database"
        
        assert email_template_access(user.id), "User should have access to Email Templates"
        
        response = client.post('/email_templates', data=dict(
            title='Test Template',
            content='This is a test template content'
        ))
        assert response.status_code == 200

        data = response.get_json()
        assert "message" in data
        assert data["message"] == "Email template added successfully!"

        # Verify the template was added to the database
        template = EmailTemplate.query.filter_by(title="Test Template").first()
        assert template is not None
        assert template.content == "This is a test template content"

def test_update_email_template(client, init_database, app, logged_in_user, email_template_access):
    with app.app_context():
        assert email_template_access(logged_in_user.id), "User should have access to Email Templates"
        
        # First, add a template
        response = client.post(
            "/email_templates",
            data=dict(title="Template to Update", content="Original content"),
        )
        assert response.status_code == 200

        # Get the ID of the added template
        template = EmailTemplate.query.filter_by(title="Template to Update").first()
        assert template is not None, "Template was not created successfully"
        template_id = template.id

        # Update the template
        response = client.put(
            f"/email_templates/{template_id}",
            json=dict(title="Updated Template", content="Updated content"),
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "message" in data
        assert data["message"] == "Email template updated successfully!"

        # Verify the template was updated in the database
        updated_template = EmailTemplate.query.get(template_id)
        assert updated_template is not None, f"Template with id {template_id} not found"
        assert updated_template.title == "Updated Template"
        assert updated_template.content == "Updated content"

def test_delete_email_template(client, init_database, app, logged_in_user, email_template_access):
    with app.app_context():
        assert email_template_access(logged_in_user.id), "User should have access to Email Templates"
        
        # First, add a template
        response = client.post(
            "/email_templates",
            data=dict(title="Template to Delete", content="Content to delete"),
        )
        assert response.status_code == 200

        # Get the ID of the added template
        template = EmailTemplate.query.filter_by(title="Template to Delete").first()
        assert template is not None, "Template was not created successfully"
        template_id = template.id

        # Delete the template
        response = client.delete(f"/email_templates/{template_id}")
        assert response.status_code == 200
        data = response.get_json()
        assert "message" in data
        assert data["message"] == "Email template deleted successfully!"

        # Verify the template was deleted from the database
        deleted_template = EmailTemplate.query.get(template_id)
        assert deleted_template is None

def test_get_email_templates(client, init_database, app, logged_in_user, email_template_access):
    with app.app_context():
        assert email_template_access(logged_in_user.id), "User should have access to Email Templates"
        
        # Add a couple of templates
        response1 = client.post(
            "/email_templates", data=dict(title="Template 1", content="Content 1")
        )
        assert response1.status_code == 200
        response2 = client.post(
            "/email_templates", data=dict(title="Template 2", content="Content 2")
        )
        assert response2.status_code == 200

        # Get all templates
        response = client.get("/email_templates")
        assert response.status_code == 200
        assert b"Template 1" in response.data
        assert b"Template 2" in response.data

def test_email_template_access(app, logged_in_user, email_template_access):
    with app.app_context():
        assert email_template_access(logged_in_user.id), "User should have access to Email Templates"