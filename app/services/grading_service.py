"""Grading service for MCQ answer evaluation."""

import logging
from datetime import datetime
from app.models import db
from app.models.exam import Question, Choice
from app.models.result import Result
from app.services.exam_service import get_exam_by_id
from app.errors import GradingError

logger = logging.getLogger("smartgrader.services.grading")


def grade_mcq_answers(exam_id, detected_answers):
    """Grade detected MCQ answers against correct answers.

    Args:
        exam_id: The exam to grade.
        detected_answers: Dict mapping question_id -> detected choice label (e.g. "A", "B").

    Returns:
        Dict with grading results: obtained_marks, total_marks, percentage, details.
    """
    exam = get_exam_by_id(exam_id)
    questions = exam.questions.order_by(Question.id).all()

    if not questions:
        raise GradingError(f"Exam {exam_id} has no questions")

    total_marks = 0
    obtained_marks = 0
    details = []

    for question in questions:
        total_marks += question.marks

        correct_choice = question.choices.filter_by(is_correct=1).first()
        correct_label = correct_choice.choice_label.upper() if correct_choice else None

        detected_label = detected_answers.get(question.id)
        if detected_label:
            detected_label = detected_label.upper()

        is_correct = detected_label == correct_label if detected_label and correct_label else False
        if is_correct:
            obtained_marks += question.marks

        details.append({
            "question_id": question.id,
            "detected": detected_label,
            "correct": correct_label,
            "is_correct": is_correct,
            "marks": question.marks,
        })

    percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0

    logger.info(
        "Graded exam %d: %s/%s (%.1f%%)",
        exam_id, obtained_marks, total_marks, percentage,
    )

    return {
        "exam_id": exam_id,
        "total_marks": total_marks,
        "obtained_marks": obtained_marks,
        "percentage": round(percentage, 1),
        "answered": sum(1 for d in details if d["detected"]),
        "total_questions": len(questions),
        "details": details,
    }


def save_result(student_id, exam_id, score, percentage):
    """Save or update a grading result."""
    existing = Result.query.filter_by(student_id=student_id, exam_id=exam_id).first()

    if existing:
        existing.score = score
        existing.percentage = percentage
        existing.graded_at = datetime.utcnow().isoformat()
    else:
        result = Result(
            student_id=student_id,
            exam_id=exam_id,
            score=score,
            percentage=percentage,
            graded_at=datetime.utcnow().isoformat(),
        )
        db.session.add(result)

    db.session.commit()
    logger.info("Saved result for student %d, exam %d: %.1f%%", student_id, exam_id, percentage)


def get_results_for_exam(exam_id):
    """Get all results for an exam."""
    results = (
        Result.query
        .filter_by(exam_id=exam_id)
        .order_by(Result.percentage.desc())
        .all()
    )
    return [r.to_dict() for r in results]
