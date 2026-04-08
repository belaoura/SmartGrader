"""Shared test fixtures."""

import json
import pytest
from app import create_app
from app.models import db as _db
from app.services.auth_service import create_teacher
from app.models.student import Student
from app.models.user import User


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


@pytest.fixture
def student_client(client, db):
    """Provide an authenticated test client (student role)."""
    student = Student(name="Test Student", matricule="TEST001")
    db.session.add(student)
    db.session.commit()
    user = User(role="student", student_id=student.id)
    db.session.add(user)
    db.session.commit()
    client.post(
        "/api/auth/scan",
        data=json.dumps({"matricule": "TEST001"}),
        content_type="application/json",
    )
    return client, student
