"""Proctoring service — event logging, snapshots, warning escalation."""

import os
import logging
from datetime import datetime, timezone
from app.models import db
from app.models.proctor import ProctorEvent, ProctorSnapshot, CaptureRequest
from app.models.exam_attempt import ExamAttempt
from app.models.exam_session import ExamSession, ExamAssignment
from app.errors import NotFoundError

logger = logging.getLogger("smartgrader.services.proctor")


def log_event(attempt_id, event_type, severity, details=None, snapshot_id=None):
    attempt = db.session.get(ExamAttempt, attempt_id)
    if not attempt:
        raise NotFoundError("ExamAttempt", attempt_id)
    event = ProctorEvent(attempt_id=attempt_id, event_type=event_type, severity=severity, details=details, snapshot_id=snapshot_id)
    db.session.add(event)
    if severity in ("medium", "high"):
        attempt.warning_count += 1
        session = db.session.get(ExamSession, attempt.session_id)
        if session and session.cheat_response == "warn_escalate":
            if attempt.warning_count >= session.warning_threshold:
                attempt.flagged = True
    db.session.commit()
    logger.info("Proctor event: %s (%s) for attempt %s", event_type, severity, attempt_id)
    return event


def save_snapshot(attempt_id, file, snapshot_type):
    attempt = db.session.get(ExamAttempt, attempt_id)
    if not attempt:
        raise NotFoundError("ExamAttempt", attempt_id)
    dir_path = os.path.join("uploads", "proctor", str(attempt.session_id), str(attempt_id))
    os.makedirs(dir_path, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{snapshot_type}_{timestamp}.jpg"
    file_path = os.path.join(dir_path, filename)
    file.save(file_path)
    snapshot = ProctorSnapshot(attempt_id=attempt_id, file_path=file_path, snapshot_type=snapshot_type)
    db.session.add(snapshot)
    db.session.commit()
    logger.info("Saved snapshot: %s for attempt %s", file_path, attempt_id)
    return snapshot


def get_proctor_status(attempt_id):
    attempt = db.session.get(ExamAttempt, attempt_id)
    if not attempt:
        raise NotFoundError("ExamAttempt", attempt_id)
    pending = CaptureRequest.query.filter_by(attempt_id=attempt_id, status="pending").first()
    session = db.session.get(ExamSession, attempt.session_id)
    return {
        "warning_count": attempt.warning_count,
        "flagged": attempt.flagged,
        "pending_capture": pending is not None,
        "cheat_response": session.cheat_response if session else "log_only",
        "warning_threshold": session.warning_threshold if session else 3,
    }


def get_session_events(session_id, student_id=None, event_type=None):
    session = db.session.get(ExamSession, session_id)
    if not session:
        raise NotFoundError("ExamSession", session_id)
    attempt_ids = [a.id for a in session.attempts.all()]
    if student_id:
        attempt_ids = [a.id for a in session.attempts.filter_by(student_id=student_id).all()]
    query = ProctorEvent.query.filter(ProctorEvent.attempt_id.in_(attempt_ids))
    if event_type:
        query = query.filter_by(event_type=event_type)
    return [e.to_dict() for e in query.order_by(ProctorEvent.created_at.desc()).all()]


def get_session_snapshots(session_id, student_id=None):
    session = db.session.get(ExamSession, session_id)
    if not session:
        raise NotFoundError("ExamSession", session_id)
    attempt_ids = [a.id for a in session.attempts.all()]
    if student_id:
        attempt_ids = [a.id for a in session.attempts.filter_by(student_id=student_id).all()]
    snapshots = ProctorSnapshot.query.filter(ProctorSnapshot.attempt_id.in_(attempt_ids)).order_by(ProctorSnapshot.created_at.desc()).all()
    return [s.to_dict() for s in snapshots]


def get_proctor_summary(session_id):
    session = db.session.get(ExamSession, session_id)
    if not session:
        raise NotFoundError("ExamSession", session_id)
    assignments = session.assignments.all()
    attempts_map = {a.student_id: a for a in session.attempts.all()}
    result = []
    for assignment in assignments:
        attempt = attempts_map.get(assignment.student_id)
        event_count = attempt.proctor_events.count() if attempt else 0
        result.append({
            "student_id": assignment.student_id,
            "student_name": assignment.student.name,
            "matricule": assignment.student.matricule,
            "event_count": event_count,
            "warning_count": attempt.warning_count if attempt else 0,
            "flagged": attempt.flagged if attempt else False,
        })
    return result


def request_capture(attempt_id):
    attempt = db.session.get(ExamAttempt, attempt_id)
    if not attempt:
        raise NotFoundError("ExamAttempt", attempt_id)
    req = CaptureRequest(attempt_id=attempt_id, status="pending")
    db.session.add(req)
    db.session.commit()
    logger.info("Capture requested for attempt %s", attempt_id)
    return req


def fulfill_capture(attempt_id):
    pending = CaptureRequest.query.filter_by(attempt_id=attempt_id, status="pending").all()
    for req in pending:
        req.status = "fulfilled"
    db.session.commit()


def toggle_flag(attempt_id):
    attempt = db.session.get(ExamAttempt, attempt_id)
    if not attempt:
        raise NotFoundError("ExamAttempt", attempt_id)
    attempt.flagged = not attempt.flagged
    db.session.commit()
    logger.info("Toggled flag on attempt %s: %s", attempt_id, attempt.flagged)


def analyze_snapshot(snapshot_id):
    snapshot = db.session.get(ProctorSnapshot, snapshot_id)
    if not snapshot:
        return
    try:
        from app.services.ai_service import get_ai_status
        status = get_ai_status()
        if not status.get("loaded"):
            return
    except (ImportError, Exception):
        return
    logger.info("AI analysis placeholder for snapshot %s", snapshot_id)
