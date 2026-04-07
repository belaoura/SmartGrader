"""Grading API endpoints."""

import logging
from flask import Blueprint, request, jsonify
from app.services.grading_service import save_result, get_results_for_exam
from app.auth import require_auth, require_role

logger = logging.getLogger("smartgrader.routes.grading")
grading_bp = Blueprint("grading", __name__)


@grading_bp.route("/results/exam/<int:exam_id>", methods=["GET"])
@require_auth
@require_role("teacher")
def get_exam_results(exam_id):
    results = get_results_for_exam(exam_id)
    return jsonify(results)


@grading_bp.route("/results", methods=["POST"])
@require_auth
@require_role("teacher")
def save_grade():
    data = request.get_json()
    save_result(
        student_id=data["student_id"],
        exam_id=data["exam_id"],
        score=data["score"],
        percentage=data["percentage"],
    )
    return jsonify({"message": "Result saved"}), 201
