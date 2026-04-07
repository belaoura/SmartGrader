"""Exam API endpoints."""

import logging
from flask import Blueprint, request, jsonify
from app.services.exam_service import (
    create_exam, get_all_exams, get_exam_by_id,
    update_exam, delete_exam, get_exam_statistics,
)
from app.auth import require_auth, require_role

logger = logging.getLogger("smartgrader.routes.exams")
exams_bp = Blueprint("exams", __name__)


@exams_bp.route("/exams", methods=["GET"])
@require_auth
@require_role("teacher")
def list_exams():
    exams = get_all_exams()
    return jsonify([e.to_dict() for e in exams])


@exams_bp.route("/exams", methods=["POST"])
@require_auth
@require_role("teacher")
def create():
    data = request.get_json()
    exam = create_exam(
        title=data["title"],
        subject=data.get("subject"),
        date=data.get("date"),
        total_marks=data.get("total_marks"),
    )
    return jsonify(exam.to_dict()), 201


@exams_bp.route("/exams/<int:exam_id>", methods=["GET"])
@require_auth
@require_role("teacher")
def get_exam(exam_id):
    exam = get_exam_by_id(exam_id)
    data = exam.to_dict()
    data["statistics"] = get_exam_statistics(exam_id)
    return jsonify(data)


@exams_bp.route("/exams/<int:exam_id>", methods=["PUT"])
@require_auth
@require_role("teacher")
def update(exam_id):
    data = request.get_json()
    exam = update_exam(exam_id, **data)
    return jsonify(exam.to_dict())


@exams_bp.route("/exams/<int:exam_id>", methods=["DELETE"])
@require_auth
@require_role("teacher")
def delete(exam_id):
    delete_exam(exam_id)
    return jsonify({"message": "Exam deleted"}), 200
