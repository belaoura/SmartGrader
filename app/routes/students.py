"""Student API endpoints."""

import logging
from flask import Blueprint, request, jsonify
from app.models import db
from app.models.student import Student
from app.errors import NotFoundError
from app.auth import require_auth, require_role

logger = logging.getLogger("smartgrader.routes.students")
students_bp = Blueprint("students", __name__)


@students_bp.route("/students", methods=["GET"])
@require_auth
@require_role("teacher")
def list_students():
    students = Student.query.order_by(Student.name).all()
    return jsonify([s.to_dict() for s in students])


@students_bp.route("/students", methods=["POST"])
@require_auth
@require_role("teacher")
def create_student():
    data = request.get_json()
    student = Student(
        name=data["name"],
        matricule=data["matricule"],
        email=data.get("email"),
    )
    db.session.add(student)
    db.session.commit()
    return jsonify(student.to_dict()), 201


@students_bp.route("/students/<int:student_id>", methods=["GET"])
@require_auth
@require_role("teacher")
def get_student(student_id):
    student = Student.query.get(student_id)
    if student is None:
        raise NotFoundError("Student", student_id)
    return jsonify(student.to_dict())


@students_bp.route("/students/<int:student_id>", methods=["PUT"])
@require_auth
@require_role("teacher")
def update_student(student_id):
    """Update a student's information."""
    student = Student.query.get_or_404(student_id)
    data = request.get_json()

    if "name" in data:
        student.name = data["name"]
    if "matricule" in data:
        student.matricule = data["matricule"]
    if "email" in data:
        student.email = data["email"]

    db.session.commit()
    return jsonify(student.to_dict())
