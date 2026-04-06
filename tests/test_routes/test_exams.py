"""Tests for exam API routes."""

import json


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "ok"


def test_create_exam(client):
    response = client.post(
        "/api/exams",
        data=json.dumps({"title": "Math", "subject": "Science", "total_marks": 100}),
        content_type="application/json",
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["title"] == "Math"
    assert data["id"] is not None


def test_list_exams(client):
    client.post(
        "/api/exams",
        data=json.dumps({"title": "A", "subject": "S"}),
        content_type="application/json",
    )
    response = client.get("/api/exams")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1


def test_get_exam(client):
    resp = client.post(
        "/api/exams",
        data=json.dumps({"title": "Find", "subject": "S"}),
        content_type="application/json",
    )
    exam_id = json.loads(resp.data)["id"]

    response = client.get(f"/api/exams/{exam_id}")
    assert response.status_code == 200
    assert json.loads(response.data)["title"] == "Find"


def test_get_exam_not_found(client):
    response = client.get("/api/exams/999")
    assert response.status_code == 404


def test_update_exam(client):
    resp = client.post(
        "/api/exams",
        data=json.dumps({"title": "Old", "subject": "S"}),
        content_type="application/json",
    )
    exam_id = json.loads(resp.data)["id"]

    response = client.put(
        f"/api/exams/{exam_id}",
        data=json.dumps({"title": "New"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert json.loads(response.data)["title"] == "New"


def test_delete_exam(client):
    resp = client.post(
        "/api/exams",
        data=json.dumps({"title": "Delete", "subject": "S"}),
        content_type="application/json",
    )
    exam_id = json.loads(resp.data)["id"]

    response = client.delete(f"/api/exams/{exam_id}")
    assert response.status_code == 200

    response = client.get(f"/api/exams/{exam_id}")
    assert response.status_code == 404


def test_create_question_with_choices(client):
    resp = client.post(
        "/api/exams",
        data=json.dumps({"title": "E", "subject": "S"}),
        content_type="application/json",
    )
    exam_id = json.loads(resp.data)["id"]

    response = client.post(
        f"/api/exams/{exam_id}/questions",
        data=json.dumps({
            "question_text": "What is 1+1?",
            "marks": 5,
            "choices": [
                {"label": "A", "text": "1", "is_correct": False},
                {"label": "B", "text": "2", "is_correct": True},
            ],
        }),
        content_type="application/json",
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert len(data["choices"]) == 2
