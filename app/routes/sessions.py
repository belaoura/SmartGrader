"""Exam session API endpoints."""

import logging
from flask import Blueprint, request, jsonify
from app.auth import require_auth, require_role
from app.services.session_service import (
    create_session, get_all_sessions, get_session_by_id,
    update_session, delete_session, assign_students,
    get_monitor_data, compute_session_status,
)

logger = logging.getLogger("smartgrader.routes.sessions")
sessions_bp = Blueprint("sessions", __name__)


@sessions_bp.route("/sessions", methods=["POST"])
@require_auth
@require_role("teacher")
def create():
    data = request.get_json()
    session = create_session(
        exam_id=data["exam_id"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        display_mode=data["display_mode"],
        save_mode=data["save_mode"],
        show_result=data["show_result"],
        randomize=data.get("randomize", False),
    )
    result = session.to_dict()
    result["status"] = compute_session_status(session)
    return jsonify(result), 201


@sessions_bp.route("/sessions", methods=["GET"])
@require_auth
@require_role("teacher")
def list_all():
    sessions = get_all_sessions()
    result = []
    for s in sessions:
        d = s.to_dict()
        d["status"] = compute_session_status(s)
        result.append(d)
    return jsonify(result)


@sessions_bp.route("/sessions/<int:session_id>", methods=["GET"])
@require_auth
@require_role("teacher")
def get_one(session_id):
    session = get_session_by_id(session_id)
    result = session.to_dict()
    result["status"] = compute_session_status(session)
    return jsonify(result)


@sessions_bp.route("/sessions/<int:session_id>", methods=["PUT"])
@require_auth
@require_role("teacher")
def update(session_id):
    data = request.get_json()
    session = update_session(session_id, **data)
    result = session.to_dict()
    result["status"] = compute_session_status(session)
    return jsonify(result)


@sessions_bp.route("/sessions/<int:session_id>", methods=["DELETE"])
@require_auth
@require_role("teacher")
def delete(session_id):
    delete_session(session_id)
    return jsonify({"message": "Session deleted"})


@sessions_bp.route("/sessions/<int:session_id>/assign", methods=["POST"])
@require_auth
@require_role("teacher")
def assign(session_id):
    data = request.get_json()
    count = assign_students(
        session_id,
        student_ids=data.get("student_ids", []),
        group_ids=data.get("group_ids", []),
    )
    return jsonify({"assigned": count})


@sessions_bp.route("/sessions/<int:session_id>/monitor", methods=["GET"])
@require_auth
@require_role("teacher")
def monitor(session_id):
    data = get_monitor_data(session_id)
    return jsonify(data)
