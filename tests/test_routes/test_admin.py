"""Tests for admin API routes."""

import io
import json
from app.services.auth_service import create_teacher


def _login_admin(client, db):
    """Create an admin and log in, returning the client with auth cookies."""
    create_teacher(email="admin@univ.dz", password="adminpass1", name="Admin", is_admin=True)
    client.post(
        "/api/auth/login",
        data=json.dumps({"email": "admin@univ.dz", "password": "adminpass1"}),
        content_type="application/json",
    )
    return client


def _login_teacher(client, db):
    """Create a non-admin teacher and log in."""
    create_teacher(email="teacher@univ.dz", password="teachpass1", name="Teacher")
    client.post(
        "/api/auth/login",
        data=json.dumps({"email": "teacher@univ.dz", "password": "teachpass1"}),
        content_type="application/json",
    )
    return client


def test_create_teacher_as_admin(client, db):
    _login_admin(client, db)
    response = client.post(
        "/api/admin/teachers",
        data=json.dumps({"email": "new@univ.dz", "password": "newpass12", "name": "New Prof"}),
        content_type="application/json",
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["email"] == "new@univ.dz"


def test_create_teacher_as_non_admin(client, db):
    _login_teacher(client, db)
    response = client.post(
        "/api/admin/teachers",
        data=json.dumps({"email": "x@x.dz", "password": "password1", "name": "X"}),
        content_type="application/json",
    )
    assert response.status_code == 403


def test_create_teacher_unauthenticated(client):
    response = client.post(
        "/api/admin/teachers",
        data=json.dumps({"email": "x@x.dz", "password": "password1", "name": "X"}),
        content_type="application/json",
    )
    assert response.status_code == 401


def test_list_teachers(client, db):
    _login_admin(client, db)
    client.post(
        "/api/admin/teachers",
        data=json.dumps({"email": "t2@univ.dz", "password": "password12", "name": "T2"}),
        content_type="application/json",
    )
    response = client.get("/api/admin/teachers")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) >= 2  # admin + new teacher


def test_deactivate_teacher(client, db):
    _login_admin(client, db)
    resp = client.post(
        "/api/admin/teachers",
        data=json.dumps({"email": "del@univ.dz", "password": "password12", "name": "Del"}),
        content_type="application/json",
    )
    teacher_id = json.loads(resp.data)["id"]

    response = client.delete(f"/api/admin/teachers/{teacher_id}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["is_active"] is False


def test_csv_import_as_admin(client, db):
    _login_admin(client, db)

    csv_content = "name,matricule,email\nAli,001,ali@univ.dz\nFatima,002,fatima@univ.dz\n"
    data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "students.csv")}

    response = client.post(
        "/api/admin/students/import",
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result["created"] == 2


def test_csv_import_as_non_admin(client, db):
    _login_teacher(client, db)

    csv_content = "name,matricule,email\nAli,001,ali@univ.dz\n"
    data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "students.csv")}

    response = client.post(
        "/api/admin/students/import",
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 403
