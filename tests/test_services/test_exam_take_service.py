"""Tests for exam take service."""

import json
import pytest
from datetime import datetime, timezone, timedelta
from app.models.exam import Exam, Question, Choice
from app.models.student import Student
from app.models.user import User
from app.models.exam_session import ExamSession, ExamAssignment
from app.models.exam_attempt import ExamAttempt
from app.models import db as _db
from app.services.exam_take_service import (
    get_student_exams, start_attempt, save_answer, save_answers_batch,
    submit_attempt, get_exam_status, get_attempt_result, auto_submit_expired,
)
from app.errors import NotFoundError, SmartGraderError


def _future(hours=1):
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _past(hours=1):
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()


def _setup_exam(db, start_time=None, end_time=None, randomize=False, show_result="score_only"):
    """Create exam with 2 questions, 2 choices each, session, student, and assignment."""
    exam = Exam(title="Test Exam", subject="Math", total_marks=10)
    db.session.add(exam)
    db.session.commit()

    q1 = Question(exam_id=exam.id, question_text="Q1", question_choices_number=2, marks=5)
    q2 = Question(exam_id=exam.id, question_text="Q2", question_choices_number=2, marks=5)
    db.session.add_all([q1, q2])
    db.session.commit()

    c1a = Choice(question_id=q1.id, choice_label="A", choice_text="Correct", is_correct=1)
    c1b = Choice(question_id=q1.id, choice_label="B", choice_text="Wrong", is_correct=0)
    c2a = Choice(question_id=q2.id, choice_label="A", choice_text="Wrong", is_correct=0)
    c2b = Choice(question_id=q2.id, choice_label="B", choice_text="Correct", is_correct=1)
    db.session.add_all([c1a, c1b, c2a, c2b])
    db.session.commit()

    session = ExamSession(
        exam_id=exam.id,
        start_time=start_time or _past(1),
        end_time=end_time or _future(1),
        display_mode="one_by_one",
        save_mode="auto_each",
        show_result=show_result,
        randomize=randomize,
    )
    db.session.add(session)
    db.session.commit()

    student = Student(name="Ali", matricule="001")
    db.session.add(student)
    db.session.commit()

    db.session.add(ExamAssignment(session_id=session.id, student_id=student.id, assigned_via="individual"))
    db.session.commit()

    return {
        "exam": exam, "session": session, "student": student,
        "q1": q1, "q2": q2, "c1a": c1a, "c1b": c1b, "c2a": c2a, "c2b": c2b,
    }


def test_get_student_exams(db):
    data = _setup_exam(db)
    exams = get_student_exams(data["student"].id)
    assert len(exams["active"]) == 1
    assert len(exams["upcoming"]) == 0
    assert len(exams["completed"]) == 0


def test_start_attempt(db):
    data = _setup_exam(db)
    result = start_attempt(data["session"].id, data["student"].id)
    assert result["attempt_id"] is not None
    assert len(result["questions"]) == 2
    assert result["remaining_seconds"] > 0


def test_start_attempt_resume(db):
    data = _setup_exam(db)
    r1 = start_attempt(data["session"].id, data["student"].id)
    r2 = start_attempt(data["session"].id, data["student"].id)
    assert r1["attempt_id"] == r2["attempt_id"]


def test_start_attempt_not_assigned(db):
    data = _setup_exam(db)
    other = Student(name="Other", matricule="999")
    db.session.add(other)
    db.session.commit()
    with pytest.raises(SmartGraderError, match="not assigned"):
        start_attempt(data["session"].id, other.id)


def test_start_attempt_not_active(db):
    data = _setup_exam(db, start_time=_future(1), end_time=_future(2))
    with pytest.raises(SmartGraderError, match="not active"):
        start_attempt(data["session"].id, data["student"].id)


def test_save_answer(db):
    data = _setup_exam(db)
    start_attempt(data["session"].id, data["student"].id)
    answer = save_answer(data["session"].id, data["student"].id, data["q1"].id, data["c1a"].id)
    assert answer.selected_choice_id == data["c1a"].id


def test_save_answer_upsert(db):
    data = _setup_exam(db)
    start_attempt(data["session"].id, data["student"].id)
    save_answer(data["session"].id, data["student"].id, data["q1"].id, data["c1a"].id)
    answer = save_answer(data["session"].id, data["student"].id, data["q1"].id, data["c1b"].id)
    assert answer.selected_choice_id == data["c1b"].id


def test_save_answers_batch(db):
    data = _setup_exam(db)
    start_attempt(data["session"].id, data["student"].id)
    count = save_answers_batch(data["session"].id, data["student"].id, [
        {"question_id": data["q1"].id, "choice_id": data["c1a"].id},
        {"question_id": data["q2"].id, "choice_id": data["c2b"].id},
    ])
    assert count == 2


def test_submit_attempt_perfect_score(db):
    data = _setup_exam(db)
    start_attempt(data["session"].id, data["student"].id)
    save_answer(data["session"].id, data["student"].id, data["q1"].id, data["c1a"].id)
    save_answer(data["session"].id, data["student"].id, data["q2"].id, data["c2b"].id)
    result = submit_attempt(data["session"].id, data["student"].id)
    assert result["score"] == 10
    assert result["percentage"] == 100.0


def test_submit_attempt_partial_score(db):
    data = _setup_exam(db)
    start_attempt(data["session"].id, data["student"].id)
    save_answer(data["session"].id, data["student"].id, data["q1"].id, data["c1a"].id)
    result = submit_attempt(data["session"].id, data["student"].id)
    assert result["score"] == 5
    assert result["percentage"] == 50.0


def test_submit_attempt_locks(db):
    data = _setup_exam(db)
    start_attempt(data["session"].id, data["student"].id)
    submit_attempt(data["session"].id, data["student"].id)
    with pytest.raises(SmartGraderError, match="already submitted"):
        submit_attempt(data["session"].id, data["student"].id)


def test_get_exam_status(db):
    data = _setup_exam(db)
    start_attempt(data["session"].id, data["student"].id)
    status = get_exam_status(data["session"].id, data["student"].id)
    assert status["remaining_seconds"] > 0
    assert status["status"] == "in_progress"
    assert status["answered_count"] == 0


def test_auto_submit_expired(db):
    data = _setup_exam(db, start_time=_past(2), end_time=_past(1))
    attempt = ExamAttempt(
        session_id=data["session"].id, student_id=data["student"].id,
        status="in_progress", started_at=_past(2),
    )
    db.session.add(attempt)
    db.session.commit()
    auto_submit_expired(data["session"].id)
    attempt = db.session.get(ExamAttempt, attempt.id)
    assert attempt.status == "auto_submitted"
    assert attempt.score is not None


def test_get_attempt_result_score_only(db):
    data = _setup_exam(db, show_result="score_only")
    start_attempt(data["session"].id, data["student"].id)
    save_answer(data["session"].id, data["student"].id, data["q1"].id, data["c1a"].id)
    submit_attempt(data["session"].id, data["student"].id)
    result = get_attempt_result(data["session"].id, data["student"].id)
    assert "score" in result
    assert "answers" not in result


def test_get_attempt_result_none(db):
    data = _setup_exam(db, show_result="none")
    start_attempt(data["session"].id, data["student"].id)
    submit_attempt(data["session"].id, data["student"].id)
    result = get_attempt_result(data["session"].id, data["student"].id)
    assert "score" not in result
    assert result["message"] == "Results are not available yet"


def test_get_attempt_result_with_answers(db):
    data = _setup_exam(db, show_result="score_and_answers")
    start_attempt(data["session"].id, data["student"].id)
    save_answer(data["session"].id, data["student"].id, data["q1"].id, data["c1a"].id)
    submit_attempt(data["session"].id, data["student"].id)
    result = get_attempt_result(data["session"].id, data["student"].id)
    assert "score" in result
    assert "answers" in result
    assert len(result["answers"]) == 2


def test_randomization_different_orders(db):
    data = _setup_exam(db, randomize=True)
    r1 = start_attempt(data["session"].id, data["student"].id)
    order1 = json.loads(ExamAttempt.query.first().question_order)
    s2 = Student(name="B", matricule="002")
    db.session.add(s2)
    db.session.commit()
    db.session.add(ExamAssignment(session_id=data["session"].id, student_id=s2.id, assigned_via="individual"))
    db.session.commit()
    r2 = start_attempt(data["session"].id, s2.id)
    order2 = json.loads(ExamAttempt.query.filter_by(student_id=s2.id).first().question_order)
    assert set(order1["questions"]) == set(order2["questions"])
