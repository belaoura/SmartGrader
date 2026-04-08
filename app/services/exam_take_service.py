"""Exam-taking service — start, answer, submit, grade, auto-submit."""

import json
import logging
import random
from datetime import datetime, timezone
from app.models import db
from app.models.exam import Question, Choice
from app.models.exam_session import ExamSession, ExamAssignment
from app.models.exam_attempt import ExamAttempt
from app.models.online_answer import OnlineAnswer
from app.services.session_service import compute_session_status
from app.errors import NotFoundError, SmartGraderError

logger = logging.getLogger("smartgrader.services.exam_take")


def get_student_exams(student_id):
    """Get all assigned exam sessions for a student, categorized by status."""
    assignments = ExamAssignment.query.filter_by(student_id=student_id).all()
    upcoming, active, completed = [], [], []

    for a in assignments:
        session = a.session
        status = compute_session_status(session)
        attempt = ExamAttempt.query.filter_by(session_id=session.id, student_id=student_id).first()

        entry = {
            **session.to_dict(),
            "status": status,
            "attempt_status": attempt.status if attempt else None,
            "score": attempt.score if attempt else None,
            "percentage": attempt.percentage if attempt else None,
        }

        if attempt and attempt.status in ("submitted", "auto_submitted"):
            completed.append(entry)
        elif status == "active":
            active.append(entry)
        elif status == "scheduled":
            upcoming.append(entry)
        else:
            completed.append(entry)

    return {"upcoming": upcoming, "active": active, "completed": completed}


def start_attempt(session_id, student_id):
    """Start or resume an exam attempt. Returns questions and attempt info."""
    session = db.session.get(ExamSession, session_id)
    if not session:
        raise NotFoundError("ExamSession", session_id)

    assignment = ExamAssignment.query.filter_by(
        session_id=session_id, student_id=student_id
    ).first()
    if not assignment:
        raise SmartGraderError("Student is not assigned to this exam", status_code=403)

    status = compute_session_status(session)
    if status != "active":
        raise SmartGraderError("Exam session is not active", status_code=400)

    existing = ExamAttempt.query.filter_by(session_id=session_id, student_id=student_id).first()
    if existing:
        if existing.status in ("submitted", "auto_submitted"):
            raise SmartGraderError("Exam already submitted", status_code=400)
        return _build_attempt_response(existing, session)

    question_order_json = None
    if session.randomize:
        questions = Question.query.filter_by(exam_id=session.exam_id).all()
        q_ids = [q.id for q in questions]
        random.shuffle(q_ids)
        choice_order = {}
        for q in questions:
            c_ids = [c.id for c in q.choices.all()]
            random.shuffle(c_ids)
            choice_order[str(q.id)] = c_ids
        question_order_json = json.dumps({"questions": q_ids, "choices": choice_order})

    attempt = ExamAttempt(
        session_id=session_id,
        student_id=student_id,
        status="in_progress",
        started_at=datetime.now(timezone.utc).isoformat(),
        question_order=question_order_json,
    )
    db.session.add(attempt)
    db.session.commit()
    logger.info("Started attempt for student %s on session %s", student_id, session_id)

    return _build_attempt_response(attempt, session)


def _build_attempt_response(attempt, session):
    """Build the response dict for a started/resumed attempt."""
    questions = Question.query.filter_by(exam_id=session.exam_id).all()
    q_map = {q.id: q for q in questions}

    if attempt.question_order:
        order = json.loads(attempt.question_order)
        q_ids = order["questions"]
        choice_orders = order.get("choices", {})
    else:
        q_ids = [q.id for q in questions]
        choice_orders = {}

    saved_answers = {a.question_id: a.selected_choice_id for a in attempt.answers.all()}

    question_list = []
    for qid in q_ids:
        q = q_map.get(qid)
        if not q:
            continue
        choices = q.choices.all()
        c_order = choice_orders.get(str(qid))
        if c_order:
            c_map = {c.id: c for c in choices}
            choices = [c_map[cid] for cid in c_order if cid in c_map]

        question_list.append({
            "id": q.id,
            "question_text": q.question_text,
            "marks": q.marks,
            "choices": [{"id": c.id, "label": c.choice_label, "text": c.choice_text} for c in choices],
            "selected_choice_id": saved_answers.get(q.id),
        })

    now = datetime.now(timezone.utc)
    end = datetime.fromisoformat(session.end_time.replace("Z", "+00:00"))
    remaining = max(0, int((end - now).total_seconds()))

    return {
        "attempt_id": attempt.id,
        "session_id": session.id,
        "status": attempt.status,
        "display_mode": session.display_mode,
        "save_mode": session.save_mode,
        "questions": question_list,
        "remaining_seconds": remaining,
        "total_questions": len(question_list),
        "proctoring_enabled": session.proctoring_enabled,
        "lockdown_enabled": session.lockdown_enabled,
        "cheat_response": session.cheat_response,
        "warning_threshold": session.warning_threshold,
    }


def save_answer(session_id, student_id, question_id, choice_id):
    """Save or update a single answer."""
    attempt = _get_active_attempt(session_id, student_id)

    existing = OnlineAnswer.query.filter_by(
        attempt_id=attempt.id, question_id=question_id
    ).first()

    if existing:
        existing.selected_choice_id = choice_id
        existing.answered_at = datetime.now(timezone.utc).isoformat()
        db.session.commit()
        return existing

    answer = OnlineAnswer(
        attempt_id=attempt.id,
        question_id=question_id,
        selected_choice_id=choice_id,
        answered_at=datetime.now(timezone.utc).isoformat(),
    )
    db.session.add(answer)
    db.session.commit()
    return answer


def save_answers_batch(session_id, student_id, answers):
    """Save a batch of answers. Returns count saved."""
    attempt = _get_active_attempt(session_id, student_id)
    count = 0
    for a in answers:
        existing = OnlineAnswer.query.filter_by(
            attempt_id=attempt.id, question_id=a["question_id"]
        ).first()
        if existing:
            existing.selected_choice_id = a["choice_id"]
            existing.answered_at = datetime.now(timezone.utc).isoformat()
        else:
            db.session.add(OnlineAnswer(
                attempt_id=attempt.id,
                question_id=a["question_id"],
                selected_choice_id=a["choice_id"],
                answered_at=datetime.now(timezone.utc).isoformat(),
            ))
        count += 1
    db.session.commit()
    return count


def submit_attempt(session_id, student_id):
    """Submit and grade an exam attempt."""
    attempt = ExamAttempt.query.filter_by(session_id=session_id, student_id=student_id).first()
    if not attempt:
        raise NotFoundError("ExamAttempt")
    if attempt.status in ("submitted", "auto_submitted"):
        raise SmartGraderError("Exam already submitted", status_code=400)

    score, percentage = _grade_attempt(attempt)
    attempt.status = "submitted"
    attempt.submitted_at = datetime.now(timezone.utc).isoformat()
    attempt.score = score
    attempt.percentage = percentage
    db.session.commit()

    logger.info("Submitted attempt %s: score=%s, pct=%s", attempt.id, score, percentage)

    session = db.session.get(ExamSession, session_id)
    return _build_result(attempt, session)


def get_exam_status(session_id, student_id):
    """Get current exam status for polling."""
    session = db.session.get(ExamSession, session_id)
    if not session:
        raise NotFoundError("ExamSession", session_id)

    if compute_session_status(session) == "ended":
        auto_submit_expired(session_id)

    attempt = ExamAttempt.query.filter_by(session_id=session_id, student_id=student_id).first()

    now = datetime.now(timezone.utc)
    end = datetime.fromisoformat(session.end_time.replace("Z", "+00:00"))
    remaining = max(0, int((end - now).total_seconds()))

    return {
        "remaining_seconds": remaining,
        "status": attempt.status if attempt else "not_started",
        "total_questions": Question.query.filter_by(exam_id=session.exam_id).count(),
        "answered_count": attempt.answers.count() if attempt else 0,
    }


def get_attempt_result(session_id, student_id):
    """Get exam result, respecting show_result setting."""
    session = db.session.get(ExamSession, session_id)
    if not session:
        raise NotFoundError("ExamSession", session_id)

    attempt = ExamAttempt.query.filter_by(session_id=session_id, student_id=student_id).first()
    if not attempt:
        raise NotFoundError("ExamAttempt")

    if attempt.status not in ("submitted", "auto_submitted"):
        raise SmartGraderError("Exam not yet submitted", status_code=400)

    return _build_result(attempt, session)


def auto_submit_expired(session_id):
    """Auto-submit all expired in-progress attempts for a session."""
    session = db.session.get(ExamSession, session_id)
    if not session:
        return

    if compute_session_status(session) != "ended":
        return

    in_progress = ExamAttempt.query.filter_by(
        session_id=session_id, status="in_progress"
    ).all()

    for attempt in in_progress:
        score, percentage = _grade_attempt(attempt)
        attempt.status = "auto_submitted"
        attempt.submitted_at = session.end_time
        attempt.score = score
        attempt.percentage = percentage
        logger.info("Auto-submitted attempt %s", attempt.id)

    db.session.commit()


def _get_active_attempt(session_id, student_id):
    """Get the in-progress attempt or raise error."""
    attempt = ExamAttempt.query.filter_by(
        session_id=session_id, student_id=student_id
    ).first()
    if not attempt:
        raise NotFoundError("ExamAttempt")
    if attempt.status != "in_progress":
        raise SmartGraderError("Exam already submitted", status_code=400)
    return attempt


def _grade_attempt(attempt):
    """Grade all answers in an attempt. Returns (score, percentage)."""
    session = db.session.get(ExamSession, attempt.session_id)
    questions = Question.query.filter_by(exam_id=session.exam_id).all()
    total_marks = sum(q.marks for q in questions)

    answers = {a.question_id: a.selected_choice_id for a in attempt.answers.all()}
    obtained = 0
    for q in questions:
        choice_id = answers.get(q.id)
        if choice_id:
            choice = db.session.get(Choice, choice_id)
            if choice and choice.is_correct:
                obtained += q.marks

    percentage = (obtained / total_marks * 100) if total_marks > 0 else 0
    return obtained, round(percentage, 2)


def _build_result(attempt, session):
    """Build result dict based on show_result setting."""
    if session.show_result == "none":
        return {"message": "Results are not available yet", "status": attempt.status}

    result = {
        "score": attempt.score,
        "percentage": attempt.percentage,
        "status": attempt.status,
        "total_questions": Question.query.filter_by(exam_id=session.exam_id).count(),
    }

    if session.show_result == "score_and_answers":
        questions = Question.query.filter_by(exam_id=session.exam_id).all()
        answers_map = {a.question_id: a.selected_choice_id for a in attempt.answers.all()}
        answer_details = []
        for q in questions:
            correct_choice = Choice.query.filter_by(question_id=q.id, is_correct=1).first()
            selected_id = answers_map.get(q.id)
            answer_details.append({
                "question_id": q.id,
                "question_text": q.question_text,
                "selected_choice_id": selected_id,
                "correct_choice_id": correct_choice.id if correct_choice else None,
                "is_correct": selected_id == correct_choice.id if correct_choice and selected_id else False,
                "marks": q.marks,
            })
        result["answers"] = answer_details

    return result
