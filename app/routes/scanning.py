"""Scanning API endpoints."""

import os
import logging
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.services.scanner_service import scan_and_grade
from app.errors import SmartGraderError

logger = logging.getLogger("smartgrader.routes.scanning")
scanning_bp = Blueprint("scanning", __name__)


def _allowed_file(filename):
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"pdf", "png", "jpg", "jpeg"})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


@scanning_bp.route("/scan/upload", methods=["POST"])
def upload_and_scan():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    exam_id = request.form.get("exam_id", type=int)
    if exam_id is None:
        return jsonify({"error": "exam_id is required"}), 400

    upload_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    try:
        fill_threshold = current_app.config.get("FILL_THRESHOLD", 50)
        result = scan_and_grade(filepath, exam_id, fill_threshold=fill_threshold)
        return jsonify(result)
    except SmartGraderError as e:
        return jsonify({"error": e.message}), e.status_code
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
