"""Tests for auth API routes."""

import json
from app.models.user import User
from app.models.student import Student
from app.models import db as _db
from app.services.auth_service import create_teacher


def _create_teacher(db, email="prof@univ.dz", password="password123", name="Prof", is_admin=False):
    """Helper to create a teacher in the DB."""
    return create_teacher(email=email, password=password, name=name, is_admin=is_admin)


def _create_student_with_user(db):
    """Helper to create a student + linked user."""
    student = Student(name="Ali", matricule="2026001", email="ali@univ.dz")
    db.session.add(student)
    db.session.commit()
    user = User(role="student", student_id=student.id)
    db.session.add(user)
    db.session.commit()
    return student, user


def test_teacher_login_success(client, db):
    _create_teacher(db)
    response = client.post(
        "/api/auth/login",
        data=json.dumps({"email": "prof@univ.dz", "password": "password123"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["user"]["email"] == "prof@univ.dz"
    assert data["user"]["role"] == "teacher"
    assert "access_token" in response.headers.get("Set-Cookie", "")


def test_teacher_login_wrong_password(client, db):
    _create_teacher(db)
    response = client.post(
        "/api/auth/login",
        data=json.dumps({"email": "prof@univ.dz", "password": "wrongpass"}),
        content_type="application/json",
    )
    assert response.status_code == 401


def test_student_scan_login(client, db):
    _create_student_with_user(db)
    response = client.post(
        "/api/auth/scan",
        data=json.dumps({"matricule": "2026001"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["user"]["role"] == "student"
    assert data["user"]["name"] == "Ali"


def test_student_scan_unknown_matricule(client, db):
    response = client.post(
        "/api/auth/scan",
        data=json.dumps({"matricule": "UNKNOWN"}),
        content_type="application/json",
    )
    assert response.status_code == 404


def test_get_me_authenticated(client, db):
    _create_teacher(db)
    client.post(
        "/api/auth/login",
        data=json.dumps({"email": "prof@univ.dz", "password": "password123"}),
        content_type="application/json",
    )
    response = client.get("/api/auth/me")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["user"]["email"] == "prof@univ.dz"


def test_get_me_unauthenticated(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_logout(client, db):
    _create_teacher(db)
    client.post(
        "/api/auth/login",
        data=json.dumps({"email": "prof@univ.dz", "password": "password123"}),
        content_type="application/json",
    )
    response = client.post("/api/auth/logout")
    assert response.status_code == 200

    # After logout, /me should fail
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_refresh_token(client, db):
    _create_teacher(db)
    client.post(
        "/api/auth/login",
        data=json.dumps({"email": "prof@univ.dz", "password": "password123"}),
        content_type="application/json",
    )
    response = client.post("/api/auth/refresh")
    assert response.status_code == 200
    assert "access_token" in response.headers.get("Set-Cookie", "")


def test_single_session_enforcement(client, db):
    _create_teacher(db)

    # First login
    client.post(
        "/api/auth/login",
        data=json.dumps({"email": "prof@univ.dz", "password": "password123"}),
        content_type="application/json",
    )
    response = client.get("/api/auth/me")
    assert response.status_code == 200

    # Simulate another device logging in (bumps token_version)
    user = User.query.filter_by(email="prof@univ.dz").first()
    user.token_version += 1
    _db.session.commit()

    # Old session should now be invalid
    response = client.get("/api/auth/me")
    assert response.status_code == 401
