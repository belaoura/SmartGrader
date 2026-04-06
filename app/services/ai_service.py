"""AI service orchestrating OCR, evaluation, and corrections."""

import logging
import os
from datetime import datetime
from PIL import Image
from app.models import db
from app.models.ai_correction import AICorrection
from app.ai.ocr_pipeline import extract_answers
from app.ai.answer_evaluator import evaluate_answer
from app.ai.model_loader import get_status, is_loaded
from app.errors import AIModelError

logger = logging.getLogger("smartgrader.services.ai")


def run_ocr(file_path, question_ids):
    """Run OCR on a scanned exam page.

    Args:
        file_path: Path to the image file.
        question_ids: List of question IDs to extract.

    Returns:
        List of dicts: [{"question_id": int, "text": str}, ...]
    """
    image = Image.open(file_path).convert("RGB")
    logger.info("Running OCR on %s for %d questions", file_path, len(question_ids))

    extracted = extract_answers(image, question_ids)

    return [
        {"question_id": qid, "text": extracted.get(qid, "")}
        for qid in question_ids
    ]


def run_evaluation(answers_data):
    """Run AI evaluation on extracted answers.

    Args:
        answers_data: List of dicts with keys:
            question_id, text, question_text, max_marks, mode, reference, keywords

    Returns:
        List of grade dicts.
    """
    grades = []
    for item in answers_data:
        grade = evaluate_answer(
            question_id=item["question_id"],
            question_text=item["question_text"],
            student_text=item["text"],
            max_marks=item["max_marks"],
            mode=item["mode"],
            reference=item.get("reference"),
            keywords=item.get("keywords"),
        )
        grades.append(grade)

    logger.info("Evaluated %d answers", len(grades))
    return grades


def save_correction(question_id, student_text, ai_score, ai_feedback, teacher_score, teacher_feedback):
    """Save a teacher correction for RAG feedback."""
    correction = AICorrection(
        question_id=question_id,
        student_text=student_text,
        ai_score=ai_score,
        ai_feedback=ai_feedback,
        teacher_score=teacher_score,
        teacher_feedback=teacher_feedback,
        created_at=datetime.utcnow().isoformat(),
    )
    db.session.add(correction)
    db.session.commit()
    logger.info("Saved correction for Q%d (AI: %.1f -> Teacher: %.1f)", question_id, ai_score, teacher_score)
    return correction


def get_corrections(question_id):
    """Get all corrections for a question."""
    corrections = (
        AICorrection.query
        .filter_by(question_id=question_id)
        .order_by(AICorrection.created_at.desc())
        .all()
    )
    return [c.to_dict() for c in corrections]


def get_ai_status():
    """Return AI model status."""
    return get_status()
