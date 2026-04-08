"""Tests for proctoring API routes."""

import io
import json
from datetime import datetime, timezone, timedelta
from app.models.exam import Exam
from app.models.student import Student
from app.models.exam_session import ExamSession, ExamAssignment
from app.models.exam_attempt import ExamAttempt
from app.models import db as _db


def _past(hours=1):
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

def _future(hours=1):
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()

def _setup(db, student):
    exam = Exam(title="Test", subject="S", total_marks=10)
    db.session.add(exam)
    db.session.commit()
    session = ExamSession(
        exam_id=exam.id, start_time=_past(1), end_time=_future(1),
        display_mode="one_by_one", save_mode="auto_each", show_result="none",
        proctoring_enabled=True, cheat_response="warn_escalate", warning_threshold=3,
    )
    db.session.add(session)
    db.session.commit()
    db.session.add(ExamAssignment(session_id=session.id, student_id=student.id, assigned_via="individual"))
    db.session.commit()
    attempt = ExamAttempt(session_id=session.id, student_id=student.id, status="in_progress", started_at=_past(0.5))
    db.session.add(attempt)
    db.session.commit()
    return session, attempt


def test_student_log_event(student_client, db):
    client, student = student_client
    session, attempt = _setup(db, student)
    response = client.post(
        f"/api/student/exams/{session.id}/proctor/event",
        data=json.dumps({"event_type": "tab_switch", "severity": "high"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["warning_count"] == 1


def test_student_upload_snapshot(student_client, db):
    client, student = student_client
    session, attempt = _setup(db, student)
    response = client.post(
        f"/api/student/exams/{session.id}/proctor/snapshot",
        data={"file": (io.BytesIO(b"\xff\xd8\xff\xe0fake"), "snap.jpg"), "snapshot_type": "periodic"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert json.loads(response.data)["snapshot_id"] is not None


def test_student_proctor_status(student_client, db):
    client, student = student_client
    session, attempt = _setup(db, student)
    response = client.get(f"/api/student/exams/{session.id}/proctor/status")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["warning_count"] == 0
    assert data["pending_capture"] is False


def test_teacher_list_events(auth_client, db):
    student = Student(name="Ali", matricule="001")
    db.session.add(student)
    db.session.commit()
    session, attempt = _setup(db, student)
    from app.services.proctor_service import log_event
    log_event(attempt.id, "tab_switch", "high")
    response = auth_client.get(f"/api/sessions/{session.id}/proctor/events")
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1


def test_teacher_proctor_summary(auth_client, db):
    student = Student(name="Ali", matricule="001")
    db.session.add(student)
    db.session.commit()
    session, attempt = _setup(db, student)
    response = auth_client.get(f"/api/sessions/{session.id}/proctor/summary")
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1


def test_teacher_request_capture(auth_client, db):
    student = Student(name="Ali", matricule="001")
    db.session.add(student)
    db.session.commit()
    session, attempt = _setup(db, student)
    response = auth_client.post(f"/api/sessions/{session.id}/proctor/capture/{student.id}")
    assert response.status_code == 200


def test_teacher_toggle_flag(auth_client, db):
    student = Student(name="Ali", matricule="001")
    db.session.add(student)
    db.session.commit()
    session, attempt = _setup(db, student)
    response = auth_client.post(f"/api/sessions/{session.id}/proctor/flag/{attempt.id}")
    assert response.status_code == 200
    assert json.loads(response.data)["flagged"] is True


def test_proctor_event_unauthenticated(client):
    response = client.post("/api/student/exams/1/proctor/event")
    assert response.status_code == 401


def test_teacher_events_unauthenticated(client):
    response = client.get("/api/sessions/1/proctor/events")
    assert response.status_code == 401
