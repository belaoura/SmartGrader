"""Tests for student exam API routes."""

import json
from datetime import datetime, timezone, timedelta
from app.models.exam import Exam, Question, Choice
from app.models.exam_session import ExamSession, ExamAssignment
from app.models import db as _db


def _past(hours=1):
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()


def _future(hours=1):
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _setup(db, student):
    exam = Exam(title="Test", subject="S", total_marks=10)
    db.session.add(exam)
    db.session.commit()
    q = Question(exam_id=exam.id, question_text="Q1", question_choices_number=2, marks=10)
    db.session.add(q)
    db.session.commit()
    c1 = Choice(question_id=q.id, choice_label="A", choice_text="Right", is_correct=1)
    c2 = Choice(question_id=q.id, choice_label="B", choice_text="Wrong", is_correct=0)
    db.session.add_all([c1, c2])
    db.session.commit()
    session = ExamSession(
        exam_id=exam.id, start_time=_past(1), end_time=_future(1),
        display_mode="one_by_one", save_mode="auto_each", show_result="score_only",
    )
    db.session.add(session)
    db.session.commit()
    db.session.add(ExamAssignment(session_id=session.id, student_id=student.id, assigned_via="individual"))
    db.session.commit()
    return session, q, c1, c2


def test_list_student_exams(student_client, db):
    client, student = student_client
    _setup(db, student)
    response = client.get("/api/student/exams")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["active"]) == 1


def test_start_exam(student_client, db):
    client, student = student_client
    session, q, c1, c2 = _setup(db, student)
    response = client.post(f"/api/student/exams/{session.id}/start")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["attempt_id"] is not None
    assert len(data["questions"]) == 1


def test_save_answer(student_client, db):
    client, student = student_client
    session, q, c1, c2 = _setup(db, student)
    client.post(f"/api/student/exams/{session.id}/start")
    response = client.post(
        f"/api/student/exams/{session.id}/answer",
        data=json.dumps({"question_id": q.id, "choice_id": c1.id}),
        content_type="application/json",
    )
    assert response.status_code == 200


def test_submit_exam(student_client, db):
    client, student = student_client
    session, q, c1, c2 = _setup(db, student)
    client.post(f"/api/student/exams/{session.id}/start")
    client.post(
        f"/api/student/exams/{session.id}/answer",
        data=json.dumps({"question_id": q.id, "choice_id": c1.id}),
        content_type="application/json",
    )
    response = client.post(f"/api/student/exams/{session.id}/submit")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["score"] == 10


def test_get_result(student_client, db):
    client, student = student_client
    session, q, c1, c2 = _setup(db, student)
    client.post(f"/api/student/exams/{session.id}/start")
    client.post(f"/api/student/exams/{session.id}/submit")
    response = client.get(f"/api/student/exams/{session.id}/result")
    assert response.status_code == 200


def test_student_exams_unauthenticated(client):
    response = client.get("/api/student/exams")
    assert response.status_code == 401


def test_teacher_cannot_access_student_routes(auth_client, db):
    response = auth_client.get("/api/student/exams")
    assert response.status_code == 403
