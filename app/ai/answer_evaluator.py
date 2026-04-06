"""Stage 2: Evaluate student answers against reference or keywords."""

import json
import logging
import re
from app.ai.model_loader import generate
from app.ai.prompt_templates import (
    EVALUATE_MODEL_ANSWER,
    EVALUATE_KEYWORDS,
    RAG_HEADER,
    RAG_EXAMPLE,
)
from app.models.ai_correction import AICorrection

logger = logging.getLogger("smartgrader.ai.answer_evaluator")

CONFIDENCE_THRESHOLD = 0.7


def evaluate_answer(question_id, question_text, student_text, max_marks, mode, reference=None, keywords=None):
    """Grade a single student answer.

    Args:
        question_id: Question ID (for RAG lookup).
        question_text: The question text.
        student_text: Extracted student answer.
        max_marks: Maximum marks for this question.
        mode: "model_answer" or "keywords".
        reference: Reference answer (for model_answer mode).
        keywords: List of required keywords (for keywords mode).

    Returns:
        Dict with score, max, feedback, confidence, needs_review, and optional found/missing concepts.
    """
    # Fetch RAG corrections for this question
    corrections = (
        AICorrection.query
        .filter_by(question_id=question_id)
        .order_by(AICorrection.created_at.desc())
        .limit(3)
        .all()
    )
    rag_context = build_rag_context(corrections)

    if mode == "keywords":
        keywords_str = ", ".join(keywords) if keywords else ""
        prompt = EVALUATE_KEYWORDS.format(
            rag_examples=rag_context,
            question_text=question_text,
            keywords_list=keywords_str,
            student_text=student_text,
            max_marks=max_marks,
        )
    else:
        prompt = EVALUATE_MODEL_ANSWER.format(
            rag_examples=rag_context,
            question_text=question_text,
            model_answer=reference or "",
            student_text=student_text,
            max_marks=max_marks,
        )

    logger.info("Evaluating Q%d (%s mode, %d RAG examples)", question_id, mode, len(corrections))
    raw_output = generate(image=None, prompt=prompt)
    result = parse_grade_response(raw_output)

    result["question_id"] = question_id
    result["needs_review"] = result.get("confidence", 0) < CONFIDENCE_THRESHOLD

    logger.info(
        "Q%d: score=%s/%s, confidence=%.2f, needs_review=%s",
        question_id, result["score"], result["max"], result["confidence"], result["needs_review"],
    )
    return result


def build_rag_context(corrections):
    """Build RAG few-shot examples from past corrections."""
    if not corrections:
        return ""

    lines = [RAG_HEADER]
    for c in corrections:
        max_marks = c.question.marks if c.question else 5
        lines.append(RAG_EXAMPLE.format(
            student_text=c.student_text[:100],
            teacher_score=c.teacher_score,
            max_marks=max_marks,
            teacher_feedback=c.teacher_feedback or "No feedback",
        ))
    lines.append("\nNow grade this new answer:\n")
    return "".join(lines)


def parse_grade_response(raw_text):
    """Parse model grading output into structured dict."""
    text = raw_text.strip()

    # Strip markdown wrapper
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)

    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        text = text[start:end]

    try:
        data = json.loads(text)
        return {
            "score": float(data.get("score", 0)),
            "max": float(data.get("max", 0)),
            "feedback": data.get("feedback", ""),
            "confidence": float(data.get("confidence", 0)),
            "found_concepts": data.get("found_concepts"),
            "missing_concepts": data.get("missing_concepts"),
        }
    except (json.JSONDecodeError, TypeError, ValueError):
        logger.warning("Failed to parse grade response: %s", raw_text[:200])
        return {
            "score": 0,
            "max": 0,
            "feedback": "Failed to parse AI response",
            "confidence": 0.0,
        }
