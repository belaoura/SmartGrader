"""Student API endpoints."""

import logging
from flask import Blueprint, request, jsonify
from app.models import db
from app.models.student import Student
from app.errors import NotFoundError

logger = logging.getLogger("smartgrader.routes.students")
students_bp = Blueprint("students", __name__)


@students_bp.route("/students", methods=["GET"])
def list_students():
    students = Student.query.order_by(Student.name).all()
    return jsonify([s.to_dict() for s in students])


@students_bp.route("/students", methods=["POST"])
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
def get_student(student_id):
    student = Student.query.get(student_id)
    if student is None:
        raise NotFoundError("Student", student_id)
    return jsonify(student.to_dict())
