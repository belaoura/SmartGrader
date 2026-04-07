"""Shared test fixtures."""

import json
import pytest
from app import create_app
from app.models import db as _db
from app.services.auth_service import create_teacher


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def db(app):
    """Provide database session."""
    with app.app_context():
        yield _db


@pytest.fixture
def client(app):
    """Provide Flask test client."""
    return app.test_client()


@pytest.fixture
def auth_client(client, db):
    """Provide an authenticated test client (teacher role)."""
    create_teacher(email="test@univ.dz", password="testpass1", name="Test Teacher")
    client.post(
        "/api/auth/login",
        data=json.dumps({"email": "test@univ.dz", "password": "testpass1"}),
        content_type="application/json",
    )
    return client
