"""Tests for AICorrection model."""

from app.models.ai_correction import AICorrection
from app.models.exam import Exam, Question
from app.models import db


def test_create_correction(db):
    exam = Exam(title="Test", subject="S")
    db.session.add(exam)
    db.session.commit()

    q = Question(exam_id=exam.id, question_text="Q1", question_choices_number=0, marks=5)
    db.session.add(q)
    db.session.commit()

    correction = AICorrection(
        question_id=q.id,
        student_text="photosynthesis uses sunlight",
        ai_score=3.0,
        ai_feedback="Partial",
        teacher_score=4.0,
        teacher_feedback="Good understanding",
        created_at="2026-04-06T12:00:00",
    )
    db.session.add(correction)
    db.session.commit()

    assert correction.id is not None
    assert correction.question.question_text == "Q1"


def test_correction_to_dict(db):
    exam = Exam(title="Test", subject="S")
    db.session.add(exam)
    db.session.commit()

    q = Question(exam_id=exam.id, question_text="Q1", question_choices_number=0, marks=5)
    db.session.add(q)
    db.session.commit()

    c = AICorrection(
        question_id=q.id,
        student_text="test",
        ai_score=2.0,
        teacher_score=3.0,
        created_at="2026-04-06",
    )
    db.session.add(c)
    db.session.commit()

    data = c.to_dict()
    assert data["ai_score"] == 2.0
    assert data["teacher_score"] == 3.0
