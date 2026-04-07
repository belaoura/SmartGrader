"""Admin API endpoints."""

import logging
from flask import Blueprint, request, jsonify

from app.auth import require_auth, require_admin
from app.services.auth_service import create_teacher
from app.services.import_service import import_students_csv
from app.models.user import User

logger = logging.getLogger("smartgrader.routes.admin")
admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/teachers", methods=["POST"])
@require_auth
@require_admin
def create_teacher_account():
    """Create a new teacher account (admin only)."""
    data = request.get_json()
    user = create_teacher(
        email=data.get("email"),
        password=data.get("password"),
        name=data.get("name"),
        is_admin=data.get("is_admin", False),
    )
    return jsonify(user.to_dict()), 201


@admin_bp.route("/admin/teachers", methods=["GET"])
@require_auth
@require_admin
def list_teachers():
    """List all teacher accounts (admin only)."""
    teachers = User.query.filter_by(role="teacher").all()
    return jsonify([t.to_dict() for t in teachers])


@admin_bp.route("/admin/teachers/<int:user_id>", methods=["DELETE"])
@require_auth
@require_admin
def deactivate_teacher(user_id):
    """Deactivate a teacher account (admin only)."""
    from app.models import db

    user = User.query.get(user_id)
    if not user or user.role != "teacher":
        return jsonify({"error": "Teacher not found"}), 404

    user.is_active = False
    user.token_version += 1  # force logout
    db.session.commit()

    logger.info("Deactivated teacher: %s", user.email)
    return jsonify(user.to_dict())


@admin_bp.route("/admin/students/import", methods=["POST"])
@require_auth
@require_admin
def import_students():
    """Import students from CSV file (admin only)."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename.endswith(".csv"):
        return jsonify({"error": "File must be a CSV"}), 400

    result = import_students_csv(file)
    return jsonify(result)
