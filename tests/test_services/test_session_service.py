"""Tests for session service."""

import pytest
from datetime import datetime, timezone, timedelta
from app.models.exam import Exam
from app.models.student import Student
from app.models.exam_session import ExamSession, ExamAssignment
from app.services.group_service import create_group, add_members
from app.services.session_service import (
    create_session, get_all_sessions, get_session_by_id,
    update_session, delete_session, assign_students,
    get_monitor_data, compute_session_status,
)
from app.errors import NotFoundError


def _make_exam(db):
    exam = Exam(title="Math", subject="Science", total_marks=100)
    db.session.add(exam)
    db.session.commit()
    return exam


def _future(hours=1):
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _past(hours=1):
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()


def test_create_session(db):
    exam = _make_exam(db)
    session = create_session(
        exam_id=exam.id, start_time=_future(1), end_time=_future(2),
        display_mode="one_by_one", save_mode="auto_each", show_result="score_only",
    )
    assert session.id is not None
    assert session.exam_id == exam.id


def test_create_session_invalid_exam(db):
    with pytest.raises(NotFoundError):
        create_session(
            exam_id=999, start_time=_future(1), end_time=_future(2),
            display_mode="one_by_one", save_mode="auto_each", show_result="none",
        )


def test_get_all_sessions(db):
    exam = _make_exam(db)
    create_session(exam_id=exam.id, start_time=_future(1), end_time=_future(2),
                   display_mode="one_by_one", save_mode="auto_each", show_result="none")
    sessions = get_all_sessions()
    assert len(sessions) == 1


def test_compute_session_status_scheduled(db):
    exam = _make_exam(db)
    session = create_session(exam_id=exam.id, start_time=_future(1), end_time=_future(2),
                             display_mode="one_by_one", save_mode="auto_each", show_result="none")
    assert compute_session_status(session) == "scheduled"


def test_compute_session_status_active(db):
    exam = _make_exam(db)
    session = create_session(exam_id=exam.id, start_time=_past(1), end_time=_future(1),
                             display_mode="one_by_one", save_mode="auto_each", show_result="none")
    assert compute_session_status(session) == "active"


def test_compute_session_status_ended(db):
    exam = _make_exam(db)
    session = create_session(exam_id=exam.id, start_time=_past(2), end_time=_past(1),
                             display_mode="one_by_one", save_mode="auto_each", show_result="none")
    assert compute_session_status(session) == "ended"


def test_update_session(db):
    exam = _make_exam(db)
    session = create_session(exam_id=exam.id, start_time=_future(1), end_time=_future(2),
                             display_mode="one_by_one", save_mode="auto_each", show_result="none")
    updated = update_session(session.id, display_mode="all_at_once")
    assert updated.display_mode == "all_at_once"


def test_delete_session(db):
    exam = _make_exam(db)
    session = create_session(exam_id=exam.id, start_time=_future(1), end_time=_future(2),
                             display_mode="one_by_one", save_mode="auto_each", show_result="none")
    delete_session(session.id)
    assert ExamSession.query.count() == 0


def test_assign_students_individual(db):
    exam = _make_exam(db)
    session = create_session(exam_id=exam.id, start_time=_future(1), end_time=_future(2),
                             display_mode="one_by_one", save_mode="auto_each", show_result="none")
    s1 = Student(name="A", matricule="001")
    s2 = Student(name="B", matricule="002")
    db.session.add_all([s1, s2])
    db.session.commit()
    count = assign_students(session.id, student_ids=[s1.id, s2.id], group_ids=[])
    assert count == 2


def test_assign_students_via_group(db):
    exam = _make_exam(db)
    session = create_session(exam_id=exam.id, start_time=_future(1), end_time=_future(2),
                             display_mode="one_by_one", save_mode="auto_each", show_result="none")
    s1 = Student(name="A", matricule="001")
    s2 = Student(name="B", matricule="002")
    db.session.add_all([s1, s2])
    db.session.commit()
    group = create_group("G1")
    add_members(group.id, [s1.id, s2.id])
    count = assign_students(session.id, student_ids=[], group_ids=[group.id])
    assert count == 2


def test_assign_students_skip_duplicates(db):
    exam = _make_exam(db)
    session = create_session(exam_id=exam.id, start_time=_future(1), end_time=_future(2),
                             display_mode="one_by_one", save_mode="auto_each", show_result="none")
    s1 = Student(name="A", matricule="001")
    db.session.add(s1)
    db.session.commit()
    assign_students(session.id, student_ids=[s1.id], group_ids=[])
    count = assign_students(session.id, student_ids=[s1.id], group_ids=[])
    assert count == 0
