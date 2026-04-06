"""AI grading API endpoints."""

import os
import json
import logging
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.services.ai_service import (
    run_ocr, run_evaluation, save_correction, get_corrections, get_ai_status,
)
from app.errors import SmartGraderError

logger = logging.getLogger("smartgrader.routes.ai")
ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/ai/status", methods=["GET"])
def status():
    return jsonify(get_ai_status())


@ai_bp.route("/ai/ocr", methods=["POST"])
def ocr():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    question_ids_raw = request.form.get("question_ids", "[]")
    try:
        question_ids = json.loads(question_ids_raw)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid question_ids format"}), 400

    if not question_ids:
        return jsonify({"error": "question_ids is required"}), 400

    upload_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    try:
        answers = run_ocr(filepath, question_ids)
        return jsonify({"answers": answers})
    except SmartGraderError as e:
        return jsonify({"error": e.message}), e.status_code
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


@ai_bp.route("/ai/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json()
    if not data or "answers" not in data:
        return jsonify({"error": "answers array is required"}), 400

    try:
        grades = run_evaluation(data["answers"])
        return jsonify({"grades": grades})
    except SmartGraderError as e:
        return jsonify({"error": e.message}), e.status_code


@ai_bp.route("/ai/correct", methods=["POST"])
def correct():
    data = request.get_json()
    required = ["question_id", "student_text", "ai_score", "teacher_score"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    correction = save_correction(
        question_id=data["question_id"],
        student_text=data["student_text"],
        ai_score=data["ai_score"],
        ai_feedback=data.get("ai_feedback", ""),
        teacher_score=data["teacher_score"],
        teacher_feedback=data.get("teacher_feedback", ""),
    )
    return jsonify({"message": "Correction saved", "id": correction.id}), 201


@ai_bp.route("/ai/corrections/<int:question_id>", methods=["GET"])
def list_corrections(question_id):
    corrections = get_corrections(question_id)
    return jsonify(corrections)
