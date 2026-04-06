"""Tests for answer evaluator."""

import json
from unittest.mock import patch, MagicMock
from app.ai.answer_evaluator import evaluate_answer, parse_grade_response, build_rag_context


def test_parse_valid_grade():
    raw = '{"score": 4, "max": 5, "feedback": "Good answer", "confidence": 0.9}'
    result = parse_grade_response(raw)
    assert result["score"] == 4
    assert result["confidence"] == 0.9


def test_parse_keywords_grade():
    raw = '{"score": 3, "max": 5, "found_concepts": ["a", "b"], "missing_concepts": ["c"], "confidence": 0.7}'
    result = parse_grade_response(raw)
    assert result["score"] == 3
    assert result["found_concepts"] == ["a", "b"]


def test_parse_invalid_grade():
    raw = "Not JSON"
    result = parse_grade_response(raw)
    assert result["score"] == 0
    assert result["confidence"] == 0.0


def test_build_rag_context_empty():
    result = build_rag_context([])
    assert result == ""


def test_build_rag_context_with_corrections():
    corrections = [
        MagicMock(student_text="ans1", teacher_score=4, teacher_feedback="good", question=MagicMock(marks=5)),
        MagicMock(student_text="ans2", teacher_score=2, teacher_feedback="missing X", question=MagicMock(marks=5)),
    ]
    result = build_rag_context(corrections)
    assert "ans1" in result
    assert "ans2" in result
    assert "graded previously" in result


def test_evaluate_model_answer_mode(app):
    mock_response = '{"score": 4, "max": 5, "feedback": "Correct concept", "confidence": 0.85}'

    with app.app_context():
        with patch("app.ai.answer_evaluator.generate", return_value=mock_response):
            with patch("app.ai.answer_evaluator.AICorrection") as MockCorr:
                MockCorr.query.filter_by.return_value.order_by.return_value.limit.return_value.all.return_value = []
                result = evaluate_answer(
                    question_id=1,
                    question_text="What is photosynthesis?",
                    student_text="Plants convert sunlight to energy",
                    max_marks=5,
                    mode="model_answer",
                    reference="Process by which plants convert light energy to chemical energy",
                )

    assert result["score"] == 4
    assert result["needs_review"] is False


def test_evaluate_low_confidence_flagged(app):
    mock_response = '{"score": 3, "max": 5, "feedback": "Unclear", "confidence": 0.5}'

    with app.app_context():
        with patch("app.ai.answer_evaluator.generate", return_value=mock_response):
            with patch("app.ai.answer_evaluator.AICorrection") as MockCorr:
                MockCorr.query.filter_by.return_value.order_by.return_value.limit.return_value.all.return_value = []
                result = evaluate_answer(
                    question_id=1,
                    question_text="Q",
                    student_text="A",
                    max_marks=5,
                    mode="model_answer",
                    reference="ref",
                )

    assert result["needs_review"] is True
