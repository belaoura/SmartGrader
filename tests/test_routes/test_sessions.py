"""Tests for session API routes."""

import json
from datetime import datetime, timezone, timedelta
from app.models.exam import Exam
from app.models.student import Student


def _future(hours=1):
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _make_exam(db):
    exam = Exam(title="Math", subject="S", total_marks=100)
    db.session.add(exam)
    db.session.commit()
    return exam


def test_create_session(auth_client, db):
    exam = _make_exam(db)
    response = auth_client.post(
        "/api/sessions",
        data=json.dumps({
            "exam_id": exam.id, "start_time": _future(1), "end_time": _future(2),
            "display_mode": "one_by_one", "save_mode": "auto_each", "show_result": "score_only",
        }),
        content_type="application/json",
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["exam_id"] == exam.id
    assert data["status"] == "scheduled"


def test_list_sessions(auth_client, db):
    exam = _make_exam(db)
    auth_client.post("/api/sessions", data=json.dumps({
        "exam_id": exam.id, "start_time": _future(1), "end_time": _future(2),
        "display_mode": "one_by_one", "save_mode": "auto_each", "show_result": "none",
    }), content_type="application/json")
    response = auth_client.get("/api/sessions")
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1


def test_assign_students(auth_client, db):
    exam = _make_exam(db)
    resp = auth_client.post("/api/sessions", data=json.dumps({
        "exam_id": exam.id, "start_time": _future(1), "end_time": _future(2),
        "display_mode": "one_by_one", "save_mode": "auto_each", "show_result": "none",
    }), content_type="application/json")
    sid = json.loads(resp.data)["id"]
    s = Student(name="Ali", matricule="001")
    db.session.add(s)
    db.session.commit()
    response = auth_client.post(
        f"/api/sessions/{sid}/assign",
        data=json.dumps({"student_ids": [s.id], "group_ids": []}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert json.loads(response.data)["assigned"] == 1


def test_delete_session(auth_client, db):
    exam = _make_exam(db)
    resp = auth_client.post("/api/sessions", data=json.dumps({
        "exam_id": exam.id, "start_time": _future(1), "end_time": _future(2),
        "display_mode": "one_by_one", "save_mode": "auto_each", "show_result": "none",
    }), content_type="application/json")
    sid = json.loads(resp.data)["id"]
    response = auth_client.delete(f"/api/sessions/{sid}")
    assert response.status_code == 200


def test_sessions_unauthenticated(client):
    response = client.get("/api/sessions")
    assert response.status_code == 401
