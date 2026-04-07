"""User model for authentication."""

from datetime import datetime, timezone
from app.models import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=True)
    role = db.Column(db.String(20), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=True)
    token_version = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.String(30), default=lambda: datetime.now(timezone.utc).isoformat())

    student = db.relationship("Student", backref="user", uselist=False)

    def to_dict(self):
        name = self.name
        if self.role == "student" and self.student:
            name = self.student.name
        return {
            "id": self.id,
            "name": name,
            "email": self.email,
            "role": self.role,
            "is_admin": self.is_admin,
            "student_id": self.student_id,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }
