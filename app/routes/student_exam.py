"""Student exam-taking API endpoints."""

import logging
from flask import Blueprint, request, jsonify, g
from app.auth import require_auth, require_role
from app.services.exam_take_service import (
    get_student_exams, start_attempt, save_answer, save_answers_batch,
    submit_attempt, get_exam_status, get_attempt_result,
)

logger = logging.getLogger("smartgrader.routes.student_exam")
student_exam_bp = Blueprint("student_exam", __name__)


@student_exam_bp.route("/student/exams", methods=["GET"])
@require_auth
@require_role("student")
def list_exams():
    student_id = g.current_user.student_id
    exams = get_student_exams(student_id)
    return jsonify(exams)


@student_exam_bp.route("/student/exams/<int:session_id>/start", methods=["POST"])
@require_auth
@require_role("student")
def start(session_id):
    student_id = g.current_user.student_id
    result = start_attempt(session_id, student_id)
    return jsonify(result)


@student_exam_bp.route("/student/exams/<int:session_id>/status", methods=["GET"])
@require_auth
@require_role("student")
def status(session_id):
    student_id = g.current_user.student_id
    result = get_exam_status(session_id, student_id)
    return jsonify(result)


@student_exam_bp.route("/student/exams/<int:session_id>/answer", methods=["POST"])
@require_auth
@require_role("student")
def answer_one(session_id):
    student_id = g.current_user.student_id
    data = request.get_json()
    save_answer(session_id, student_id, data["question_id"], data["choice_id"])
    return jsonify({"message": "Answer saved"})


@student_exam_bp.route("/student/exams/<int:session_id>/answers", methods=["POST"])
@require_auth
@require_role("student")
def answer_batch(session_id):
    student_id = g.current_user.student_id
    data = request.get_json()
    count = save_answers_batch(session_id, student_id, data["answers"])
    return jsonify({"saved": count})


@student_exam_bp.route("/student/exams/<int:session_id>/submit", methods=["POST"])
@require_auth
@require_role("student")
def submit(session_id):
    student_id = g.current_user.student_id
    result = submit_attempt(session_id, student_id)
    return jsonify(result)


@student_exam_bp.route("/student/exams/<int:session_id>/result", methods=["GET"])
@require_auth
@require_role("student")
def result(session_id):
    student_id = g.current_user.student_id
    result = get_attempt_result(session_id, student_id)
    return jsonify(result)
