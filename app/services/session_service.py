"""Exam session management service."""

import logging
from datetime import datetime, timezone
from app.models import db
from app.models.exam import Exam
from app.models.exam_session import ExamSession, ExamAssignment
from app.models.exam_attempt import ExamAttempt
from app.models.group import StudentGroupMember
from app.errors import NotFoundError, SmartGraderError

logger = logging.getLogger("smartgrader.services.session")


def compute_session_status(session):
    """Compute session status from current time vs start/end times."""
    now = datetime.now(timezone.utc).isoformat()
    if now < session.start_time:
        return "scheduled"
    elif now <= session.end_time:
        return "active"
    else:
        return "ended"


def create_session(exam_id, start_time, end_time, display_mode, save_mode, show_result, randomize=False):
    """Create a new exam session."""
    exam = db.session.get(Exam, exam_id)
    if not exam:
        raise NotFoundError("Exam", exam_id)

    session = ExamSession(
        exam_id=exam_id,
        start_time=start_time,
        end_time=end_time,
        display_mode=display_mode,
        save_mode=save_mode,
        show_result=show_result,
        randomize=randomize,
    )
    db.session.add(session)
    db.session.commit()
    logger.info("Created exam session %s for exam %s", session.id, exam_id)
    return session


def get_all_sessions():
    """List all exam sessions."""
    return ExamSession.query.order_by(ExamSession.id.desc()).all()


def get_session_by_id(session_id):
    """Get session by ID. Raises NotFoundError."""
    session = db.session.get(ExamSession, session_id)
    if not session:
        raise NotFoundError("ExamSession", session_id)
    return session


def update_session(session_id, **kwargs):
    """Update session settings. Only if not yet started."""
    session = get_session_by_id(session_id)
    status = compute_session_status(session)
    if status != "scheduled":
        raise SmartGraderError("Cannot modify an active or ended session", status_code=400)

    for key, value in kwargs.items():
        if hasattr(session, key) and key not in ("id", "exam_id", "created_at"):
            setattr(session, key, value)
    db.session.commit()
    logger.info("Updated session %s", session_id)
    return session


def delete_session(session_id):
    """Delete session. Only if not yet started."""
    session = get_session_by_id(session_id)
    status = compute_session_status(session)
    if status != "scheduled":
        raise SmartGraderError("Cannot delete an active or ended session", status_code=400)

    db.session.delete(session)
    db.session.commit()
    logger.info("Deleted session %s", session_id)


def assign_students(session_id, student_ids, group_ids):
    """Assign students to a session. Expands groups. Skips duplicates. Returns count."""
    session = get_session_by_id(session_id)

    all_student_ids = set(student_ids or [])
    for gid in (group_ids or []):
        members = StudentGroupMember.query.filter_by(group_id=gid).all()
        for m in members:
            all_student_ids.add(m.student_id)

    existing = {a.student_id for a in session.assignments.all()}
    added = 0
    for sid in all_student_ids:
        if sid not in existing:
            via = "group" if sid not in set(student_ids or []) else "individual"
            db.session.add(ExamAssignment(session_id=session.id, student_id=sid, assigned_via=via))
            existing.add(sid)
            added += 1
    db.session.commit()
    logger.info("Assigned %d students to session %s", added, session_id)
    return added


def get_monitor_data(session_id):
    """Get monitoring data for a session: all assigned students with attempt info."""
    session = get_session_by_id(session_id)

    if compute_session_status(session) == "ended":
        try:
            from app.services.exam_take_service import auto_submit_expired
            auto_submit_expired(session_id)
        except ImportError:
            pass

    assignments = session.assignments.all()
    attempts_by_student = {
        a.student_id: a for a in session.attempts.all()
    }

    result = []
    for assignment in assignments:
        attempt = attempts_by_student.get(assignment.student_id)
        result.append({
            "student_id": assignment.student_id,
            "student_name": assignment.student.name,
            "matricule": assignment.student.matricule,
            "status": attempt.status if attempt else "not_started",
            "answer_count": attempt.answers.count() if attempt else 0,
            "score": attempt.score if attempt else None,
            "percentage": attempt.percentage if attempt else None,
        })
    return result
