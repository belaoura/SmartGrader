"""Exam CRUD service layer."""

import logging
from app.models import db
from app.models.exam import Exam, Question, Choice
from app.errors import NotFoundError

logger = logging.getLogger("smartgrader.services.exam")


def create_exam(title, subject=None, date=None, total_marks=None):
    """Create a new exam."""
    exam = Exam(title=title, subject=subject, date=date, total_marks=total_marks)
    db.session.add(exam)
    db.session.commit()
    logger.info("Created exam %d: %s", exam.id, title)
    return exam


def get_all_exams():
    """Return all exams ordered by id descending."""
    return Exam.query.order_by(Exam.id.desc()).all()


def get_exam_by_id(exam_id):
    """Return exam by id or raise NotFoundError."""
    exam = Exam.query.get(exam_id)
    if exam is None:
        raise NotFoundError("Exam", exam_id)
    return exam


def update_exam(exam_id, **kwargs):
    """Update exam fields. Only updates provided non-None values."""
    exam = get_exam_by_id(exam_id)
    for key, value in kwargs.items():
        if value is not None and hasattr(exam, key):
            setattr(exam, key, value)
    db.session.commit()
    logger.info("Updated exam %d", exam_id)
    return exam


def delete_exam(exam_id):
    """Delete exam and all related data (cascade)."""
    exam = get_exam_by_id(exam_id)
    db.session.delete(exam)
    db.session.commit()
    logger.info("Deleted exam %d", exam_id)


def create_question_with_choices(exam_id, question_text, marks, choices):
    """Create a question with its choices in one transaction.

    Args:
        exam_id: ID of the parent exam.
        question_text: The question text.
        marks: Points for this question.
        choices: List of dicts with keys: label, text, is_correct.
    """
    get_exam_by_id(exam_id)  # Validate exam exists

    question = Question(
        exam_id=exam_id,
        question_text=question_text,
        question_choices_number=len(choices),
        marks=marks,
    )
    db.session.add(question)
    db.session.flush()  # Get question.id before adding choices

    for choice_data in choices:
        choice = Choice(
            question_id=question.id,
            choice_label=choice_data["label"],
            choice_text=choice_data["text"],
            is_correct=int(choice_data.get("is_correct", False)),
        )
        db.session.add(choice)

    db.session.commit()
    logger.info("Created question %d for exam %d with %d choices", question.id, exam_id, len(choices))
    return question


def get_questions_for_exam(exam_id):
    """Return all questions with choices for an exam."""
    get_exam_by_id(exam_id)  # Validate exam exists
    questions = Question.query.filter_by(exam_id=exam_id).order_by(Question.id).all()
    return [q.to_dict(include_choices=True) for q in questions]


def get_exam_statistics(exam_id):
    """Return statistics about an exam."""
    exam = get_exam_by_id(exam_id)
    questions = exam.questions.all()

    question_count = len(questions)
    total_marks = sum(q.marks for q in questions) if questions else 0
    avg_marks = total_marks / question_count if question_count > 0 else 0

    results = exam.results.all()
    student_count = len(results)
    avg_score = sum(r.percentage for r in results) / student_count if student_count > 0 else 0

    return {
        "question_count": question_count,
        "total_marks": total_marks,
        "average_marks": round(avg_marks, 2),
        "student_count": student_count,
        "average_score": round(avg_score, 2),
    }
