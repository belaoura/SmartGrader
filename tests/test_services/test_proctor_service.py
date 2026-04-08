"""Tests for proctor service."""

import os
import io
import pytest
from app.models.exam import Exam
from app.models.student import Student
from app.models.exam_session import ExamSession, ExamAssignment
from app.models.exam_attempt import ExamAttempt
from app.models.proctor import ProctorEvent, ProctorSnapshot, CaptureRequest
from app.models import db as _db
from app.services.proctor_service import (
    log_event, save_snapshot, get_proctor_status,
    get_session_events, get_session_snapshots, get_proctor_summary,
    request_capture, fulfill_capture, toggle_flag,
)


def _make_attempt(db, cheat_response="warn_escalate", warning_threshold=3):
    exam = Exam(title="E", subject="S", total_marks=10)
    db.session.add(exam)
    db.session.commit()
    session = ExamSession(
        exam_id=exam.id, start_time="2026-04-10T09:00:00Z", end_time="2026-04-10T10:00:00Z",
        display_mode="one_by_one", save_mode="auto_each", show_result="none",
        proctoring_enabled=True, cheat_response=cheat_response, warning_threshold=warning_threshold,
    )
    student = Student(name="Ali", matricule="001")
    db.session.add_all([session, student])
    db.session.commit()
    db.session.add(ExamAssignment(session_id=session.id, student_id=student.id, assigned_via="individual"))
    db.session.commit()
    attempt = ExamAttempt(session_id=session.id, student_id=student.id, status="in_progress", started_at="2026-04-10T09:01:00Z")
    db.session.add(attempt)
    db.session.commit()
    return attempt, session


def test_log_event_high_severity(db):
    attempt, session = _make_attempt(db)
    event = log_event(attempt.id, "tab_switch", "high", '{"test": true}')
    assert event.id is not None
    assert attempt.warning_count == 1


def test_log_event_low_severity_no_increment(db):
    attempt, session = _make_attempt(db)
    log_event(attempt.id, "right_click", "low")
    assert attempt.warning_count == 0


def test_auto_flag_at_threshold(db):
    attempt, session = _make_attempt(db, warning_threshold=2)
    log_event(attempt.id, "tab_switch", "high")
    assert attempt.flagged is False
    log_event(attempt.id, "no_face", "high")
    assert attempt.flagged is True


def test_log_only_mode_no_flag(db):
    attempt, session = _make_attempt(db, cheat_response="log_only", warning_threshold=1)
    log_event(attempt.id, "tab_switch", "high")
    assert attempt.warning_count == 1
    assert attempt.flagged is False


def test_save_snapshot(app, db):
    attempt, session = _make_attempt(db)
    fake_file = io.BytesIO(b"\xff\xd8\xff\xe0fake jpeg data")
    fake_file.filename = "snapshot.jpg"

    class FakeFileStorage:
        def __init__(self, stream):
            self.stream = stream
        def save(self, path):
            with open(path, "wb") as f:
                f.write(self.stream.read())

    snapshot = save_snapshot(attempt.id, FakeFileStorage(fake_file), "periodic")
    assert snapshot.id is not None
    assert os.path.exists(snapshot.file_path)
    os.remove(snapshot.file_path)


def test_get_proctor_status(db):
    attempt, session = _make_attempt(db)
    log_event(attempt.id, "tab_switch", "high")
    status = get_proctor_status(attempt.id)
    assert status["warning_count"] == 1
    assert status["flagged"] is False
    assert status["pending_capture"] is False


def test_request_and_fulfill_capture(db):
    attempt, session = _make_attempt(db)
    req = request_capture(attempt.id)
    assert req.status == "pending"
    status = get_proctor_status(attempt.id)
    assert status["pending_capture"] is True
    fulfill_capture(attempt.id)
    status = get_proctor_status(attempt.id)
    assert status["pending_capture"] is False


def test_toggle_flag(db):
    attempt, session = _make_attempt(db)
    toggle_flag(attempt.id)
    assert attempt.flagged is True
    toggle_flag(attempt.id)
    assert attempt.flagged is False


def test_get_session_events(db):
    attempt, session = _make_attempt(db)
    log_event(attempt.id, "tab_switch", "high")
    log_event(attempt.id, "right_click", "low")
    events = get_session_events(session.id)
    assert len(events) == 2


def test_get_session_events_filtered(db):
    attempt, session = _make_attempt(db)
    log_event(attempt.id, "tab_switch", "high")
    log_event(attempt.id, "right_click", "low")
    events = get_session_events(session.id, event_type="tab_switch")
    assert len(events) == 1


def test_get_session_snapshots(db):
    attempt, session = _make_attempt(db)
    db.session.add(ProctorSnapshot(attempt_id=attempt.id, file_path="a.jpg", snapshot_type="periodic"))
    db.session.add(ProctorSnapshot(attempt_id=attempt.id, file_path="b.jpg", snapshot_type="event_triggered"))
    db.session.commit()
    snaps = get_session_snapshots(session.id)
    assert len(snaps) == 2


def test_get_proctor_summary(db):
    attempt, session = _make_attempt(db)
    log_event(attempt.id, "tab_switch", "high")
    log_event(attempt.id, "no_face", "high")
    summary = get_proctor_summary(session.id)
    assert len(summary) == 1
    assert summary[0]["event_count"] == 2
    assert summary[0]["warning_count"] == 2
