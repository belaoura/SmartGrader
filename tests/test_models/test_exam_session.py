"""Tests for ExamSession, ExamAssignment models."""

from app.models.exam_session import ExamSession, ExamAssignment
from app.models.exam import Exam
from app.models.student import Student
from app.models import db as _db


def _make_exam(db):
    exam = Exam(title="Math", subject="Science", total_marks=100)
    db.session.add(exam)
    db.session.commit()
    return exam


def test_create_exam_session(db):
    exam = _make_exam(db)
    session = ExamSession(
        exam_id=exam.id, start_time="2026-04-10T09:00:00Z", end_time="2026-04-10T10:00:00Z",
        display_mode="one_by_one", save_mode="auto_each", show_result="score_only",
    )
    db.session.add(session)
    db.session.commit()
    assert session.id is not None
    assert session.randomize is False


def test_exam_session_to_dict(db):
    exam = _make_exam(db)
    session = ExamSession(
        exam_id=exam.id, start_time="2026-04-10T09:00:00Z", end_time="2026-04-10T10:00:00Z",
        display_mode="all_at_once", save_mode="manual", randomize=True, show_result="score_and_answers",
    )
    db.session.add(session)
    db.session.commit()
    d = session.to_dict()
    assert d["exam_id"] == exam.id
    assert d["display_mode"] == "all_at_once"
    assert d["randomize"] is True
    assert "exam_title" in d


def test_create_exam_assignment(db):
    exam = _make_exam(db)
    session = ExamSession(
        exam_id=exam.id, start_time="2026-04-10T09:00:00Z", end_time="2026-04-10T10:00:00Z",
        display_mode="one_by_one", save_mode="auto_each", show_result="none",
    )
    student = Student(name="Ali", matricule="001")
    db.session.add_all([session, student])
    db.session.commit()
    assignment = ExamAssignment(session_id=session.id, student_id=student.id, assigned_via="individual")
    db.session.add(assignment)
    db.session.commit()
    assert assignment.id is not None
    assert session.assignments.count() == 1


def test_session_cascade_delete(db):
    exam = _make_exam(db)
    session = ExamSession(
        exam_id=exam.id, start_time="2026-04-10T09:00:00Z", end_time="2026-04-10T10:00:00Z",
        display_mode="one_by_one", save_mode="auto_each", show_result="none",
    )
    student = Student(name="X", matricule="099")
    db.session.add_all([session, student])
    db.session.commit()
    db.session.add(ExamAssignment(session_id=session.id, student_id=student.id, assigned_via="individual"))
    db.session.commit()
    db.session.delete(session)
    db.session.commit()
    assert ExamAssignment.query.count() == 0


from app.models.exam_attempt import ExamAttempt
from app.models.online_answer import OnlineAnswer
from app.models.exam import Question, Choice


def _make_session(db):
    exam = _make_exam(db)
    session = ExamSession(
        exam_id=exam.id, start_time="2026-04-10T09:00:00Z", end_time="2026-04-10T10:00:00Z",
        display_mode="one_by_one", save_mode="auto_each", show_result="score_only",
    )
    db.session.add(session)
    db.session.commit()
    return exam, session


def test_create_exam_attempt(db):
    exam, session = _make_session(db)
    student = Student(name="Ali", matricule="100")
    db.session.add(student)
    db.session.commit()
    attempt = ExamAttempt(
        session_id=session.id, student_id=student.id,
        status="in_progress", started_at="2026-04-10T09:01:00Z",
    )
    db.session.add(attempt)
    db.session.commit()
    assert attempt.id is not None
    assert attempt.score is None


def test_create_online_answer(db):
    exam, session = _make_session(db)
    student = Student(name="Ali", matricule="100")
    db.session.add(student)
    db.session.commit()
    q = Question(exam_id=exam.id, question_text="Q1", question_choices_number=2, marks=5)
    db.session.add(q)
    db.session.commit()
    c = Choice(question_id=q.id, choice_label="A", choice_text="Answer A", is_correct=1)
    db.session.add(c)
    db.session.commit()
    attempt = ExamAttempt(
        session_id=session.id, student_id=student.id,
        status="in_progress", started_at="2026-04-10T09:01:00Z",
    )
    db.session.add(attempt)
    db.session.commit()
    answer = OnlineAnswer(
        attempt_id=attempt.id, question_id=q.id,
        selected_choice_id=c.id, answered_at="2026-04-10T09:02:00Z",
    )
    db.session.add(answer)
    db.session.commit()
    assert answer.id is not None
    assert attempt.answers.count() == 1


def test_attempt_to_dict(db):
    exam, session = _make_session(db)
    student = Student(name="Ali", matricule="100")
    db.session.add(student)
    db.session.commit()
    attempt = ExamAttempt(
        session_id=session.id, student_id=student.id,
        status="submitted", started_at="2026-04-10T09:01:00Z",
        submitted_at="2026-04-10T09:45:00Z", score=80, percentage=80.0,
    )
    db.session.add(attempt)
    db.session.commit()
    d = attempt.to_dict()
    assert d["status"] == "submitted"
    assert d["score"] == 80
    assert d["student_name"] == "Ali"
