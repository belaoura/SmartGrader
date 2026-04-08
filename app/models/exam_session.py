"""Exam session and assignment models."""

from datetime import datetime, timezone
from app.models import db


class ExamSession(db.Model):
    __tablename__ = "exam_sessions"

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False)
    start_time = db.Column(db.String(30), nullable=False)
    end_time = db.Column(db.String(30), nullable=False)
    display_mode = db.Column(db.String(20), nullable=False)
    save_mode = db.Column(db.String(20), nullable=False)
    randomize = db.Column(db.Boolean, default=False)
    show_result = db.Column(db.String(20), nullable=False)
    proctoring_enabled = db.Column(db.Boolean, default=False)
    lockdown_enabled = db.Column(db.Boolean, default=False)
    cheat_response = db.Column(db.String(20), default="log_only")
    warning_threshold = db.Column(db.Integer, default=3)
    created_at = db.Column(db.String(30), default=lambda: datetime.now(timezone.utc).isoformat())

    exam = db.relationship("Exam", backref="sessions")
    assignments = db.relationship(
        "ExamAssignment", backref="session", cascade="all, delete-orphan", lazy="dynamic"
    )
    attempts = db.relationship(
        "ExamAttempt", backref="session", cascade="all, delete-orphan", lazy="dynamic"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "exam_id": self.exam_id,
            "exam_title": self.exam.title if self.exam else None,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "display_mode": self.display_mode,
            "save_mode": self.save_mode,
            "randomize": self.randomize,
            "show_result": self.show_result,
            "proctoring_enabled": self.proctoring_enabled,
            "lockdown_enabled": self.lockdown_enabled,
            "cheat_response": self.cheat_response,
            "warning_threshold": self.warning_threshold,
            "assignment_count": self.assignments.count(),
            "created_at": self.created_at,
        }


class ExamAssignment(db.Model):
    __tablename__ = "exam_assignments"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("exam_sessions.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    assigned_via = db.Column(db.String(20), default="individual")

    student = db.relationship("Student")

    __table_args__ = (
        db.UniqueConstraint("session_id", "student_id", name="uq_session_student"),
    )
