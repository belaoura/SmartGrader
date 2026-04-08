"""Exam attempt model."""

from app.models import db


class ExamAttempt(db.Model):
    __tablename__ = "exam_attempts"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("exam_sessions.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="in_progress")
    started_at = db.Column(db.String(30))
    submitted_at = db.Column(db.String(30))
    question_order = db.Column(db.Text)
    score = db.Column(db.Float)
    percentage = db.Column(db.Float)
    flagged = db.Column(db.Boolean, default=False)
    warning_count = db.Column(db.Integer, default=0)

    student = db.relationship("Student")
    answers = db.relationship(
        "OnlineAnswer", backref="attempt", cascade="all, delete-orphan", lazy="dynamic"
    )
    proctor_events = db.relationship(
        "ProctorEvent", backref="attempt", cascade="all, delete-orphan", lazy="dynamic"
    )
    proctor_snapshots = db.relationship(
        "ProctorSnapshot", backref="attempt", cascade="all, delete-orphan", lazy="dynamic"
    )
    capture_requests = db.relationship(
        "CaptureRequest", backref="attempt", cascade="all, delete-orphan", lazy="dynamic"
    )

    __table_args__ = (
        db.UniqueConstraint("session_id", "student_id", name="uq_attempt_session_student"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "student_id": self.student_id,
            "student_name": self.student.name if self.student else None,
            "status": self.status,
            "started_at": self.started_at,
            "submitted_at": self.submitted_at,
            "score": self.score,
            "percentage": self.percentage,
            "flagged": self.flagged,
            "warning_count": self.warning_count,
            "answer_count": self.answers.count(),
        }
