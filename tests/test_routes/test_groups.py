"""Tests for group API routes."""

import json
from app.models.student import Student


def test_create_group(auth_client, db):
    response = auth_client.post(
        "/api/groups",
        data=json.dumps({"name": "CS Year 3"}),
        content_type="application/json",
    )
    assert response.status_code == 201
    assert json.loads(response.data)["name"] == "CS Year 3"


def test_list_groups(auth_client, db):
    auth_client.post("/api/groups", data=json.dumps({"name": "G1"}), content_type="application/json")
    response = auth_client.get("/api/groups")
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1


def test_get_group(auth_client, db):
    resp = auth_client.post("/api/groups", data=json.dumps({"name": "G1"}), content_type="application/json")
    gid = json.loads(resp.data)["id"]
    response = auth_client.get(f"/api/groups/{gid}")
    assert response.status_code == 200
    assert json.loads(response.data)["name"] == "G1"


def test_delete_group(auth_client, db):
    resp = auth_client.post("/api/groups", data=json.dumps({"name": "Del"}), content_type="application/json")
    gid = json.loads(resp.data)["id"]
    response = auth_client.delete(f"/api/groups/{gid}")
    assert response.status_code == 200


def test_add_members(auth_client, db):
    resp = auth_client.post("/api/groups", data=json.dumps({"name": "G1"}), content_type="application/json")
    gid = json.loads(resp.data)["id"]
    s = Student(name="Ali", matricule="001")
    db.session.add(s)
    db.session.commit()
    response = auth_client.post(
        f"/api/groups/{gid}/members",
        data=json.dumps({"student_ids": [s.id]}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert json.loads(response.data)["added"] == 1


def test_remove_member(auth_client, db):
    resp = auth_client.post("/api/groups", data=json.dumps({"name": "G1"}), content_type="application/json")
    gid = json.loads(resp.data)["id"]
    s = Student(name="Ali", matricule="001")
    db.session.add(s)
    db.session.commit()
    auth_client.post(f"/api/groups/{gid}/members", data=json.dumps({"student_ids": [s.id]}), content_type="application/json")
    response = auth_client.delete(f"/api/groups/{gid}/members/{s.id}")
    assert response.status_code == 200


def test_groups_unauthenticated(client):
    response = client.get("/api/groups")
    assert response.status_code == 401
