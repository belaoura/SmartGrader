"""Proctoring API endpoints — student + teacher."""

import logging
from flask import Blueprint, request, jsonify, g, send_file
from app.auth import require_auth, require_role
from app.services.proctor_service import (
    log_event, save_snapshot, get_proctor_status,
    get_session_events, get_session_snapshots, get_proctor_summary,
    request_capture, fulfill_capture, toggle_flag,
)
from app.models.exam_attempt import ExamAttempt
from app.models.proctor import ProctorSnapshot

logger = logging.getLogger("smartgrader.routes.proctoring")
proctoring_bp = Blueprint("proctoring", __name__)


@proctoring_bp.route("/student/exams/<int:session_id>/proctor/event", methods=["POST"])
@require_auth
@require_role("student")
def student_log_event(session_id):
    student_id = g.current_user.student_id
    attempt = ExamAttempt.query.filter_by(session_id=session_id, student_id=student_id).first()
    if not attempt:
        return jsonify({"error": "No active attempt"}), 404
    data = request.get_json()
    event = log_event(attempt_id=attempt.id, event_type=data["event_type"], severity=data["severity"], details=data.get("details"))
    return jsonify({"event_id": event.id, "warning_count": attempt.warning_count})


@proctoring_bp.route("/student/exams/<int:session_id>/proctor/snapshot", methods=["POST"])
@require_auth
@require_role("student")
def student_upload_snapshot(session_id):
    student_id = g.current_user.student_id
    attempt = ExamAttempt.query.filter_by(session_id=session_id, student_id=student_id).first()
    if not attempt:
        return jsonify({"error": "No active attempt"}), 404
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    snapshot_type = request.form.get("snapshot_type", "event_triggered")
    snapshot = save_snapshot(attempt.id, request.files["file"], snapshot_type)
    if snapshot_type == "on_demand":
        fulfill_capture(attempt.id)
    return jsonify({"snapshot_id": snapshot.id})


@proctoring_bp.route("/student/exams/<int:session_id>/proctor/status", methods=["GET"])
@require_auth
@require_role("student")
def student_proctor_status(session_id):
    student_id = g.current_user.student_id
    attempt = ExamAttempt.query.filter_by(session_id=session_id, student_id=student_id).first()
    if not attempt:
        return jsonify({"error": "No active attempt"}), 404
    status = get_proctor_status(attempt.id)
    return jsonify(status)


@proctoring_bp.route("/sessions/<int:session_id>/proctor/events", methods=["GET"])
@require_auth
@require_role("teacher")
def teacher_list_events(session_id):
    student_id = request.args.get("student_id", type=int)
    event_type = request.args.get("event_type")
    events = get_session_events(session_id, student_id=student_id, event_type=event_type)
    return jsonify(events)


@proctoring_bp.route("/sessions/<int:session_id>/proctor/snapshots", methods=["GET"])
@require_auth
@require_role("teacher")
def teacher_list_snapshots(session_id):
    student_id = request.args.get("student_id", type=int)
    snapshots = get_session_snapshots(session_id, student_id=student_id)
    return jsonify(snapshots)


@proctoring_bp.route("/sessions/<int:session_id>/proctor/snapshots/<int:snapshot_id>/image", methods=["GET"])
@require_auth
@require_role("teacher")
def teacher_serve_snapshot(session_id, snapshot_id):
    snapshot = ProctorSnapshot.query.get(snapshot_id)
    if not snapshot:
        return jsonify({"error": "Snapshot not found"}), 404
    return send_file(snapshot.file_path, mimetype="image/jpeg")


@proctoring_bp.route("/sessions/<int:session_id>/proctor/capture/<int:student_id>", methods=["POST"])
@require_auth
@require_role("teacher")
def teacher_request_capture(session_id, student_id):
    attempt = ExamAttempt.query.filter_by(session_id=session_id, student_id=student_id).first()
    if not attempt:
        return jsonify({"error": "No attempt found"}), 404
    req = request_capture(attempt.id)
    return jsonify({"request_id": req.id, "status": req.status})


@proctoring_bp.route("/sessions/<int:session_id>/proctor/summary", methods=["GET"])
@require_auth
@require_role("teacher")
def teacher_proctor_summary(session_id):
    summary = get_proctor_summary(session_id)
    return jsonify(summary)


@proctoring_bp.route("/sessions/<int:session_id>/proctor/flag/<int:attempt_id>", methods=["POST"])
@require_auth
@require_role("teacher")
def teacher_toggle_flag(session_id, attempt_id):
    toggle_flag(attempt_id)
    attempt = ExamAttempt.query.get(attempt_id)
    return jsonify({"attempt_id": attempt_id, "flagged": attempt.flagged})
