"""Tests for Exam, Question, Choice models."""

from app.models.exam import Exam, Question, Choice


def test_create_exam(db):
    exam = Exam(title="Math Final", subject="Mathematics", total_marks=100)
    db.session.add(exam)
    db.session.commit()

    assert exam.id is not None
    assert exam.title == "Math Final"


def test_exam_to_dict(db):
    exam = Exam(title="Physics", subject="Science", date="2026-04-06", total_marks=50)
    db.session.add(exam)
    db.session.commit()

    data = exam.to_dict()
    assert data["title"] == "Physics"
    assert data["total_marks"] == 50


def test_exam_question_relationship(db):
    exam = Exam(title="Test", subject="Test")
    db.session.add(exam)
    db.session.commit()

    q = Question(exam_id=exam.id, question_text="What is 2+2?", question_choices_number=4, marks=5)
    db.session.add(q)
    db.session.commit()

    assert exam.questions.count() == 1
    assert q.exam.title == "Test"


def test_question_choice_relationship(db):
    exam = Exam(title="Test", subject="Test")
    db.session.add(exam)
    db.session.commit()

    q = Question(exam_id=exam.id, question_text="Q1", question_choices_number=2, marks=1)
    db.session.add(q)
    db.session.commit()

    c1 = Choice(question_id=q.id, choice_label="A", choice_text="Yes", is_correct=1)
    c2 = Choice(question_id=q.id, choice_label="B", choice_text="No", is_correct=0)
    db.session.add_all([c1, c2])
    db.session.commit()

    assert q.choices.count() == 2
    assert c1.to_dict()["is_correct"] is True


def test_cascade_delete(db):
    exam = Exam(title="Delete Me", subject="Test")
    db.session.add(exam)
    db.session.commit()

    q = Question(exam_id=exam.id, question_text="Q1", question_choices_number=2, marks=1)
    db.session.add(q)
    db.session.commit()

    c = Choice(question_id=q.id, choice_label="A", choice_text="A", is_correct=0)
    db.session.add(c)
    db.session.commit()

    db.session.delete(exam)
    db.session.commit()

    assert Question.query.count() == 0
    assert Choice.query.count() == 0
