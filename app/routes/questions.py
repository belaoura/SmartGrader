"""Question API endpoints."""

import logging
from flask import Blueprint, request, jsonify
from app.services.exam_service import create_question_with_choices, get_questions_for_exam
from app.auth import require_auth, require_role

logger = logging.getLogger("smartgrader.routes.questions")
questions_bp = Blueprint("questions", __name__)


@questions_bp.route("/exams/<int:exam_id>/questions", methods=["GET"])
@require_auth
@require_role("teacher")
def list_questions(exam_id):
    questions = get_questions_for_exam(exam_id)
    return jsonify(questions)


@questions_bp.route("/exams/<int:exam_id>/questions", methods=["POST"])
@require_auth
@require_role("teacher")
def create_question(exam_id):
    data = request.get_json()
    question = create_question_with_choices(
        exam_id=exam_id,
        question_text=data["question_text"],
        marks=data["marks"],
        choices=data["choices"],
    )
    return jsonify(question.to_dict(include_choices=True)), 201
