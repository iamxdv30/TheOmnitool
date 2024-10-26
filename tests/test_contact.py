import pytest
from flask import Flask
from routes.contact_routes import contact, configure_mail
from dotenv import load_dotenv
import os

@pytest.fixture
def app():
    load_dotenv(".env")
    app = Flask(__name__)
    configure_mail(app)
    app.register_blueprint(contact)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_send_test_query(client):
    """
    Test that a user can send a test query using valid credentials
    """
    data = {
        "query_type": "General",
        "name": "Xyrus De Vera",
        "email": "mr.xyydevera@gmail.com",
        "message": "This is a test email from the Omnitool",
    }

    response = client.post("/contact", json=data)
    assert response.status_code == 200
    assert b"Message sent successfully!" in response.data

def test_send_query_missing_fields(client):
    """
    Test that sending a query with missing fields returns an error
    """
    data = {
        "name": "Xyrus De Vera",
        "email": "mr.xyydevera@gmail.com",
    }

    response = client.post("/contact", json=data)
    assert response.status_code == 400
    assert b"All fields are required." in response.data

def test_send_query_invalid_email(client):
    """
    Test that sending a query with an invalid email returns an error
    """
    data = {
        "query_type": "General",
        "name": "Xyrus De Vera",
        "email": "invalid-email",
        "message": "This is a test email from the Omnitool",
    }

    response = client.post("/contact", json=data)
    assert response.status_code == 400
    assert b"Invalid email address." in response.data