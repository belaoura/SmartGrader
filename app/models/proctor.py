"""Proctoring models — events, snapshots, capture requests."""

from datetime import datetime, timezone
from app.models import db


class ProctorEvent(db.Model):
    __tablename__ = "proctor_events"

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("exam_attempts.id"), nullable=False)
    event_type = db.Column(db.String(30), nullable=False)
    severity = db.Column(db.String(10), nullable=False)
    details = db.Column(db.Text)
    snapshot_id = db.Column(db.Integer, db.ForeignKey("proctor_snapshots.id"), nullable=True)
    created_at = db.Column(db.String(30), default=lambda: datetime.now(timezone.utc).isoformat())

    snapshot = db.relationship("ProctorSnapshot", foreign_keys=[snapshot_id])

    def to_dict(self):
        return {
            "id": self.id,
            "attempt_id": self.attempt_id,
            "event_type": self.event_type,
            "severity": self.severity,
            "details": self.details,
            "snapshot_id": self.snapshot_id,
            "created_at": self.created_at,
        }


class ProctorSnapshot(db.Model):
    __tablename__ = "proctor_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("exam_attempts.id"), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    snapshot_type = db.Column(db.String(20), nullable=False)
    ai_analysis = db.Column(db.Text)
    created_at = db.Column(db.String(30), default=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self):
        return {
            "id": self.id,
            "attempt_id": self.attempt_id,
            "file_path": self.file_path,
            "snapshot_type": self.snapshot_type,
            "ai_analysis": self.ai_analysis,
            "created_at": self.created_at,
        }


class CaptureRequest(db.Model):
    __tablename__ = "capture_requests"

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("exam_attempts.id"), nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.String(30), default=lambda: datetime.now(timezone.utc).isoformat())
