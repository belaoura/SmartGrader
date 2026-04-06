"""Tests for exam service CRUD operations."""

from app.services.exam_service import (
    create_exam,
    get_all_exams,
    get_exam_by_id,
    update_exam,
    delete_exam,
    create_question_with_choices,
    get_questions_for_exam,
    get_exam_statistics,
)


def test_create_exam(db):
    exam = create_exam(title="Math", subject="Science", total_marks=100)
    assert exam.id is not None
    assert exam.title == "Math"


def test_get_all_exams(db):
    create_exam(title="A", subject="S")
    create_exam(title="B", subject="S")
    exams = get_all_exams()
    assert len(exams) == 2


def test_get_exam_by_id(db):
    exam = create_exam(title="Find Me", subject="Test")
    found = get_exam_by_id(exam.id)
    assert found.title == "Find Me"


def test_get_exam_not_found(db):
    from app.errors import NotFoundError
    import pytest
    with pytest.raises(NotFoundError):
        get_exam_by_id(999)


def test_update_exam(db):
    exam = create_exam(title="Old", subject="S")
    updated = update_exam(exam.id, title="New")
    assert updated.title == "New"


def test_delete_exam(db):
    exam = create_exam(title="Delete", subject="S")
    delete_exam(exam.id)
    from app.models.exam import Exam
    assert Exam.query.count() == 0


def test_create_question_with_choices(db):
    exam = create_exam(title="E", subject="S")
    question = create_question_with_choices(
        exam_id=exam.id,
        question_text="What is 1+1?",
        marks=5,
        choices=[
            {"label": "A", "text": "1", "is_correct": False},
            {"label": "B", "text": "2", "is_correct": True},
            {"label": "C", "text": "3", "is_correct": False},
        ],
    )
    assert question.id is not None
    assert question.choices.count() == 3
    assert question.question_choices_number == 3


def test_get_questions_for_exam(db):
    exam = create_exam(title="E", subject="S")
    create_question_with_choices(
        exam_id=exam.id,
        question_text="Q1",
        marks=1,
        choices=[{"label": "A", "text": "A", "is_correct": True}],
    )
    questions = get_questions_for_exam(exam.id)
    assert len(questions) == 1
    assert questions[0]["choices"][0]["is_correct"] is True


def test_get_exam_statistics(db):
    exam = create_exam(title="E", subject="S")
    create_question_with_choices(
        exam_id=exam.id,
        question_text="Q1",
        marks=10,
        choices=[{"label": "A", "text": "A", "is_correct": True}],
    )
    create_question_with_choices(
        exam_id=exam.id,
        question_text="Q2",
        marks=20,
        choices=[{"label": "A", "text": "A", "is_correct": True}],
    )
    stats = get_exam_statistics(exam.id)
    assert stats["question_count"] == 2
    assert stats["total_marks"] == 30
