"""Tests for ProctorEvent, ProctorSnapshot, CaptureRequest models."""

from app.models.proctor import ProctorEvent, ProctorSnapshot, CaptureRequest
from app.models.exam_session import ExamSession
from app.models.exam_attempt import ExamAttempt
from app.models.exam import Exam
from app.models.student import Student
from app.models import db as _db


def _make_attempt(db):
    exam = Exam(title="E", subject="S", total_marks=10)
    db.session.add(exam)
    db.session.commit()
    session = ExamSession(
        exam_id=exam.id, start_time="2026-04-10T09:00:00Z", end_time="2026-04-10T10:00:00Z",
        display_mode="one_by_one", save_mode="auto_each", show_result="none",
        proctoring_enabled=True, cheat_response="warn_escalate", warning_threshold=3,
    )
    student = Student(name="Ali", matricule="001")
    db.session.add_all([session, student])
    db.session.commit()
    attempt = ExamAttempt(session_id=session.id, student_id=student.id, status="in_progress", started_at="2026-04-10T09:01:00Z")
    db.session.add(attempt)
    db.session.commit()
    return attempt, session


def test_exam_session_proctoring_fields(db):
    exam = Exam(title="E", subject="S", total_marks=10)
    db.session.add(exam)
    db.session.commit()
    session = ExamSession(
        exam_id=exam.id, start_time="2026-04-10T09:00:00Z", end_time="2026-04-10T10:00:00Z",
        display_mode="one_by_one", save_mode="auto_each", show_result="none",
        proctoring_enabled=True, lockdown_enabled=True, cheat_response="warn", warning_threshold=5,
    )
    db.session.add(session)
    db.session.commit()
    d = session.to_dict()
    assert d["proctoring_enabled"] is True
    assert d["lockdown_enabled"] is True
    assert d["cheat_response"] == "warn"
    assert d["warning_threshold"] == 5


def test_exam_attempt_proctoring_fields(db):
    attempt, _ = _make_attempt(db)
    assert attempt.flagged is False
    assert attempt.warning_count == 0
    attempt.warning_count = 3
    attempt.flagged = True
    db.session.commit()
    d = attempt.to_dict()
    assert d["flagged"] is True
    assert d["warning_count"] == 3


def test_create_proctor_event(db):
    attempt, _ = _make_attempt(db)
    event = ProctorEvent(
        attempt_id=attempt.id, event_type="tab_switch", severity="high",
        details='{"duration": 5}', created_at="2026-04-10T09:05:00Z",
    )
    db.session.add(event)
    db.session.commit()
    assert event.id is not None
    assert attempt.proctor_events.count() == 1


def test_create_proctor_snapshot(db):
    attempt, _ = _make_attempt(db)
    snapshot = ProctorSnapshot(
        attempt_id=attempt.id, file_path="uploads/proctor/1/1/snap.jpg",
        snapshot_type="periodic", created_at="2026-04-10T09:05:00Z",
    )
    db.session.add(snapshot)
    db.session.commit()
    assert snapshot.id is not None
    assert attempt.proctor_snapshots.count() == 1


def test_event_with_snapshot(db):
    attempt, _ = _make_attempt(db)
    snapshot = ProctorSnapshot(
        attempt_id=attempt.id, file_path="uploads/proctor/1/1/snap.jpg",
        snapshot_type="event_triggered", created_at="2026-04-10T09:05:00Z",
    )
    db.session.add(snapshot)
    db.session.commit()
    event = ProctorEvent(
        attempt_id=attempt.id, event_type="no_face", severity="high",
        snapshot_id=snapshot.id, created_at="2026-04-10T09:05:00Z",
    )
    db.session.add(event)
    db.session.commit()
    assert event.snapshot_id == snapshot.id


def test_create_capture_request(db):
    attempt, _ = _make_attempt(db)
    req = CaptureRequest(attempt_id=attempt.id, status="pending", created_at="2026-04-10T09:06:00Z")
    db.session.add(req)
    db.session.commit()
    assert req.id is not None
    assert req.status == "pending"


def test_proctor_event_to_dict(db):
    attempt, _ = _make_attempt(db)
    event = ProctorEvent(
        attempt_id=attempt.id, event_type="multiple_faces", severity="high",
        details='{"face_count": 2}', created_at="2026-04-10T09:05:00Z",
    )
    db.session.add(event)
    db.session.commit()
    d = event.to_dict()
    assert d["event_type"] == "multiple_faces"
    assert d["severity"] == "high"
    assert d["attempt_id"] == attempt.id
