"""Tests for Student and StudentAnswer models."""

import pytest
import sqlalchemy
from app.models.student import Student, StudentAnswer
from app.models.exam import Exam, Question, Choice
from app.models import db as _db


def test_create_student(db):
    s = Student(name="Ahmed", matricule="2026001", email="ahmed@univ.dz")
    db.session.add(s)
    db.session.commit()

    assert s.id is not None
    assert s.matricule == "2026001"


def test_student_unique_matricule(db):
    s1 = Student(name="A", matricule="001")
    s2 = Student(name="B", matricule="001")
    db.session.add(s1)
    db.session.commit()

    db.session.add(s2)
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_student_answer(db):
    exam = Exam(title="E", subject="S")
    db.session.add(exam)
    db.session.commit()

    q = Question(exam_id=exam.id, question_text="Q", question_choices_number=2, marks=1)
    db.session.add(q)
    db.session.commit()

    c = Choice(question_id=q.id, choice_label="A", choice_text="A", is_correct=1)
    db.session.add(c)
    db.session.commit()

    s = Student(name="X", matricule="100")
    db.session.add(s)
    db.session.commit()

    sa = StudentAnswer(student_id=s.id, question_id=q.id, selected_choice_id=c.id)
    db.session.add(sa)
    db.session.commit()

    assert sa.selected_choice.is_correct == 1
