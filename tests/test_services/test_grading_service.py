"""Tests for grading service."""

from app.services.exam_service import create_exam, create_question_with_choices
from app.services.grading_service import grade_mcq_answers, save_result, get_results_for_exam
from app.models.student import Student
from app.models import db


def _create_exam_with_questions(db_session):
    """Helper: create exam with 2 questions."""
    exam = create_exam(title="Grading Test", subject="Math", total_marks=10)
    create_question_with_choices(
        exam_id=exam.id, question_text="2+2?", marks=5,
        choices=[
            {"label": "A", "text": "3", "is_correct": False},
            {"label": "B", "text": "4", "is_correct": True},
        ],
    )
    create_question_with_choices(
        exam_id=exam.id, question_text="3+3?", marks=5,
        choices=[
            {"label": "A", "text": "6", "is_correct": True},
            {"label": "B", "text": "7", "is_correct": False},
        ],
    )
    return exam


def test_grade_all_correct(db):
    exam = _create_exam_with_questions(db)
    questions = exam.questions.order_by("id").all()

    detected = {
        questions[0].id: "B",
        questions[1].id: "A",
    }
    result = grade_mcq_answers(exam.id, detected)
    assert result["obtained_marks"] == 10
    assert result["percentage"] == 100.0


def test_grade_one_wrong(db):
    exam = _create_exam_with_questions(db)
    questions = exam.questions.order_by("id").all()

    detected = {
        questions[0].id: "A",
        questions[1].id: "A",
    }
    result = grade_mcq_answers(exam.id, detected)
    assert result["obtained_marks"] == 5
    assert result["percentage"] == 50.0


def test_grade_unanswered(db):
    exam = _create_exam_with_questions(db)
    questions = exam.questions.order_by("id").all()

    detected = {
        questions[0].id: "B",
    }
    result = grade_mcq_answers(exam.id, detected)
    assert result["obtained_marks"] == 5


def test_save_and_get_results(db):
    exam = _create_exam_with_questions(db)
    student = Student(name="Test", matricule="001")
    db.session.add(student)
    db.session.commit()

    save_result(student.id, exam.id, score=8, percentage=80.0)
    results = get_results_for_exam(exam.id)
    assert len(results) == 1
    assert results[0]["score"] == 8
