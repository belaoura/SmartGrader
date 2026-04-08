# Phase 3: Anti-Cheat System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add proctoring and anti-cheat to the online exam system — browser-side face detection via TensorFlow.js BlazeFace, DOM event tracking, webcam snapshots, optional server-side AI verification, configurable cheat response, and a teacher proctoring dashboard.

**Architecture:** Hybrid approach — browser-side AI (BlazeFace) runs real-time face detection, DOM listeners track suspicious events. Periodic + event-triggered webcam snapshots upload to server via REST. Server stores events/snapshots in new ProctorEvent/ProctorSnapshot models, handles warning escalation, and optionally runs Qwen vision model for deeper analysis. Teacher monitors via enhanced SessionDetail page.

**Tech Stack:** Flask + SQLAlchemy (backend), React 19 + TensorFlow.js + BlazeFace (frontend) — zero new Python dependencies.

---

## File Structure

```
NEW FILES:
  app/models/proctor.py               — ProctorEvent, ProctorSnapshot, CaptureRequest
  app/services/proctor_service.py      — proctoring business logic
  app/routes/proctoring.py             — student + teacher proctoring endpoints
  tests/test_models/test_proctor.py
  tests/test_services/test_proctor_service.py
  tests/test_routes/test_proctoring.py
  frontend/src/components/ProctorEngine.jsx
  frontend/src/components/FullscreenLockdown.jsx
  frontend/src/components/ProctorWarningBanner.jsx
  frontend/src/hooks/use-proctor.js

MODIFIED FILES:
  app/models/exam_session.py    — add 4 proctoring columns
  app/models/exam_attempt.py    — add flagged, warning_count
  app/models/__init__.py        — export new models
  app/routes/__init__.py        — register proctoring blueprint
  frontend/package.json         — add @tensorflow/tfjs, @tensorflow-models/blazeface
  frontend/src/pages/TakeExam.jsx      — mount proctoring components
  frontend/src/pages/CreateSession.jsx — add proctoring settings
  frontend/src/pages/SessionDetail.jsx — add proctoring tab
```

---

## Task 1: Modify ExamSession & ExamAttempt Models + New Proctor Models

**Files:**
- Modify: `app/models/exam_session.py`
- Modify: `app/models/exam_attempt.py`
- Create: `app/models/proctor.py`
- Modify: `app/models/__init__.py`
- Create: `tests/test_models/test_proctor.py`

- [ ] **Step 1: Add proctoring columns to ExamSession**

In `app/models/exam_session.py`, add these columns to the `ExamSession` class after `show_result`:

```python
    proctoring_enabled = db.Column(db.Boolean, default=False)
    lockdown_enabled = db.Column(db.Boolean, default=False)
    cheat_response = db.Column(db.String(20), default="log_only")
    warning_threshold = db.Column(db.Integer, default=3)
```

Update `to_dict()` to include the new fields — add these to the return dict:

```python
            "proctoring_enabled": self.proctoring_enabled,
            "lockdown_enabled": self.lockdown_enabled,
            "cheat_response": self.cheat_response,
            "warning_threshold": self.warning_threshold,
```

- [ ] **Step 2: Add proctoring fields to ExamAttempt**

In `app/models/exam_attempt.py`, add after `percentage`:

```python
    flagged = db.Column(db.Boolean, default=False)
    warning_count = db.Column(db.Integer, default=0)
```

Add relationships for proctoring:

```python
    proctor_events = db.relationship(
        "ProctorEvent", backref="attempt", cascade="all, delete-orphan", lazy="dynamic"
    )
    proctor_snapshots = db.relationship(
        "ProctorSnapshot", backref="attempt", cascade="all, delete-orphan", lazy="dynamic"
    )
    capture_requests = db.relationship(
        "CaptureRequest", backref="attempt", cascade="all, delete-orphan", lazy="dynamic"
    )
```

Update `to_dict()` — add to the return dict:

```python
            "flagged": self.flagged,
            "warning_count": self.warning_count,
```

- [ ] **Step 3: Write failing tests**

Create `tests/test_models/test_proctor.py`:

```python
"""Tests for ProctorEvent, ProctorSnapshot, CaptureRequest models."""

from app.models.proctor import ProctorEvent, ProctorSnapshot, CaptureRequest
from app.models.exam_session import ExamSession
from app.models.exam_attempt import ExamAttempt
from app.models.exam import Exam
from app.models.student import Student
from app.models import db as _db


def _make_attempt(db):
    exam = Exam(title="E", subject="S", total_marks=10)
    db.session.add(exam)
    db.session.commit()
    session = ExamSession(
        exam_id=exam.id, start_time="2026-04-10T09:00:00Z", end_time="2026-04-10T10:00:00Z",
        display_mode="one_by_one", save_mode="auto_each", show_result="none",
        proctoring_enabled=True, cheat_response="warn_escalate", warning_threshold=3,
    )
    student = Student(name="Ali", matricule="001")
    db.session.add_all([session, student])
    db.session.commit()
    attempt = ExamAttempt(session_id=session.id, student_id=student.id, status="in_progress", started_at="2026-04-10T09:01:00Z")
    db.session.add(attempt)
    db.session.commit()
    return attempt, session


def test_exam_session_proctoring_fields(db):
    exam = Exam(title="E", subject="S", total_marks=10)
    db.session.add(exam)
    db.session.commit()
    session = ExamSession(
        exam_id=exam.id, start_time="2026-04-10T09:00:00Z", end_time="2026-04-10T10:00:00Z",
        display_mode="one_by_one", save_mode="auto_each", show_result="none",
        proctoring_enabled=True, lockdown_enabled=True, cheat_response="warn", warning_threshold=5,
    )
    db.session.add(session)
    db.session.commit()
    d = session.to_dict()
    assert d["proctoring_enabled"] is True
    assert d["lockdown_enabled"] is True
    assert d["cheat_response"] == "warn"
    assert d["warning_threshold"] == 5


def test_exam_attempt_proctoring_fields(db):
    attempt, _ = _make_attempt(db)
    assert attempt.flagged is False
    assert attempt.warning_count == 0
    attempt.warning_count = 3
    attempt.flagged = True
    db.session.commit()
    d = attempt.to_dict()
    assert d["flagged"] is True
    assert d["warning_count"] == 3


def test_create_proctor_event(db):
    attempt, _ = _make_attempt(db)
    event = ProctorEvent(
        attempt_id=attempt.id, event_type="tab_switch", severity="high",
        details='{"duration": 5}', created_at="2026-04-10T09:05:00Z",
    )
    db.session.add(event)
    db.session.commit()
    assert event.id is not None
    assert attempt.proctor_events.count() == 1


def test_create_proctor_snapshot(db):
    attempt, _ = _make_attempt(db)
    snapshot = ProctorSnapshot(
        attempt_id=attempt.id, file_path="uploads/proctor/1/1/snap.jpg",
        snapshot_type="periodic", created_at="2026-04-10T09:05:00Z",
    )
    db.session.add(snapshot)
    db.session.commit()
    assert snapshot.id is not None
    assert attempt.proctor_snapshots.count() == 1


def test_event_with_snapshot(db):
    attempt, _ = _make_attempt(db)
    snapshot = ProctorSnapshot(
        attempt_id=attempt.id, file_path="uploads/proctor/1/1/snap.jpg",
        snapshot_type="event_triggered", created_at="2026-04-10T09:05:00Z",
    )
    db.session.add(snapshot)
    db.session.commit()
    event = ProctorEvent(
        attempt_id=attempt.id, event_type="no_face", severity="high",
        snapshot_id=snapshot.id, created_at="2026-04-10T09:05:00Z",
    )
    db.session.add(event)
    db.session.commit()
    assert event.snapshot_id == snapshot.id


def test_create_capture_request(db):
    attempt, _ = _make_attempt(db)
    req = CaptureRequest(attempt_id=attempt.id, status="pending", created_at="2026-04-10T09:06:00Z")
    db.session.add(req)
    db.session.commit()
    assert req.id is not None
    assert req.status == "pending"


def test_proctor_event_to_dict(db):
    attempt, _ = _make_attempt(db)
    event = ProctorEvent(
        attempt_id=attempt.id, event_type="multiple_faces", severity="high",
        details='{"face_count": 2}', created_at="2026-04-10T09:05:00Z",
    )
    db.session.add(event)
    db.session.commit()
    d = event.to_dict()
    assert d["event_type"] == "multiple_faces"
    assert d["severity"] == "high"
    assert d["attempt_id"] == attempt.id
```

- [ ] **Step 4: Create proctor models**

Create `app/models/proctor.py`:

```python
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
```

- [ ] **Step 5: Export in models/__init__.py**

Add at the end of `app/models/__init__.py`:

```python
from app.models.proctor import ProctorEvent, ProctorSnapshot, CaptureRequest  # noqa: E402, F401
```

- [ ] **Step 6: Run tests, full suite, commit**

Run: `pytest tests/test_models/test_proctor.py -v`
Then: `pytest tests/ -v --tb=short`

```bash
git add app/models/exam_session.py app/models/exam_attempt.py app/models/proctor.py app/models/__init__.py tests/test_models/test_proctor.py
git commit -m "feat(proctor): add proctoring models and update ExamSession/ExamAttempt"
```

---

## Task 2: Proctor Service

**Files:**
- Create: `app/services/proctor_service.py`
- Create: `tests/test_services/test_proctor_service.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_services/test_proctor_service.py`:

```python
"""Tests for proctor service."""

import os
import io
import pytest
from app.models.exam import Exam
from app.models.student import Student
from app.models.exam_session import ExamSession, ExamAssignment
from app.models.exam_attempt import ExamAttempt
from app.models.proctor import ProctorEvent, ProctorSnapshot, CaptureRequest
from app.models import db as _db
from app.services.proctor_service import (
    log_event, save_snapshot, get_proctor_status,
    get_session_events, get_session_snapshots, get_proctor_summary,
    request_capture, fulfill_capture, toggle_flag,
)


def _make_attempt(db, cheat_response="warn_escalate", warning_threshold=3):
    exam = Exam(title="E", subject="S", total_marks=10)
    db.session.add(exam)
    db.session.commit()
    session = ExamSession(
        exam_id=exam.id, start_time="2026-04-10T09:00:00Z", end_time="2026-04-10T10:00:00Z",
        display_mode="one_by_one", save_mode="auto_each", show_result="none",
        proctoring_enabled=True, cheat_response=cheat_response, warning_threshold=warning_threshold,
    )
    student = Student(name="Ali", matricule="001")
    db.session.add_all([session, student])
    db.session.commit()
    attempt = ExamAttempt(session_id=session.id, student_id=student.id, status="in_progress", started_at="2026-04-10T09:01:00Z")
    db.session.add(attempt)
    db.session.commit()
    return attempt, session


def test_log_event_high_severity(db):
    attempt, session = _make_attempt(db)
    event = log_event(attempt.id, "tab_switch", "high", '{"test": true}')
    assert event.id is not None
    assert attempt.warning_count == 1


def test_log_event_low_severity_no_increment(db):
    attempt, session = _make_attempt(db)
    log_event(attempt.id, "right_click", "low")
    assert attempt.warning_count == 0


def test_auto_flag_at_threshold(db):
    attempt, session = _make_attempt(db, warning_threshold=2)
    log_event(attempt.id, "tab_switch", "high")
    assert attempt.flagged is False
    log_event(attempt.id, "no_face", "high")
    assert attempt.flagged is True


def test_log_only_mode_no_flag(db):
    attempt, session = _make_attempt(db, cheat_response="log_only", warning_threshold=1)
    log_event(attempt.id, "tab_switch", "high")
    assert attempt.warning_count == 1
    assert attempt.flagged is False


def test_save_snapshot(app, db):
    attempt, session = _make_attempt(db)
    fake_file = io.BytesIO(b"\xff\xd8\xff\xe0fake jpeg data")
    fake_file.filename = "snapshot.jpg"
    snapshot = save_snapshot(attempt.id, fake_file, "periodic")
    assert snapshot.id is not None
    assert os.path.exists(snapshot.file_path)
    # cleanup
    os.remove(snapshot.file_path)


def test_get_proctor_status(db):
    attempt, session = _make_attempt(db)
    log_event(attempt.id, "tab_switch", "high")
    status = get_proctor_status(attempt.id)
    assert status["warning_count"] == 1
    assert status["flagged"] is False
    assert status["pending_capture"] is False


def test_request_and_fulfill_capture(db):
    attempt, session = _make_attempt(db)
    req = request_capture(attempt.id)
    assert req.status == "pending"

    status = get_proctor_status(attempt.id)
    assert status["pending_capture"] is True

    fulfill_capture(attempt.id)
    status = get_proctor_status(attempt.id)
    assert status["pending_capture"] is False


def test_toggle_flag(db):
    attempt, session = _make_attempt(db)
    toggle_flag(attempt.id)
    assert attempt.flagged is True
    toggle_flag(attempt.id)
    assert attempt.flagged is False


def test_get_session_events(db):
    attempt, session = _make_attempt(db)
    log_event(attempt.id, "tab_switch", "high")
    log_event(attempt.id, "right_click", "low")
    events = get_session_events(session.id)
    assert len(events) == 2


def test_get_session_events_filtered(db):
    attempt, session = _make_attempt(db)
    log_event(attempt.id, "tab_switch", "high")
    log_event(attempt.id, "right_click", "low")
    events = get_session_events(session.id, event_type="tab_switch")
    assert len(events) == 1


def test_get_session_snapshots(db):
    attempt, session = _make_attempt(db)
    db.session.add(ProctorSnapshot(attempt_id=attempt.id, file_path="a.jpg", snapshot_type="periodic"))
    db.session.add(ProctorSnapshot(attempt_id=attempt.id, file_path="b.jpg", snapshot_type="event_triggered"))
    db.session.commit()
    snaps = get_session_snapshots(session.id)
    assert len(snaps) == 2


def test_get_proctor_summary(db):
    attempt, session = _make_attempt(db)
    log_event(attempt.id, "tab_switch", "high")
    log_event(attempt.id, "no_face", "high")
    summary = get_proctor_summary(session.id)
    assert len(summary) == 1
    assert summary[0]["event_count"] == 2
    assert summary[0]["warning_count"] == 2
```

- [ ] **Step 2: Create the service**

Create `app/services/proctor_service.py`:

```python
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
    """Log a proctor event. Increments warning_count for medium/high severity. Auto-flags if threshold reached."""
    attempt = db.session.get(ExamAttempt, attempt_id)
    if not attempt:
        raise NotFoundError("ExamAttempt", attempt_id)

    event = ProctorEvent(
        attempt_id=attempt_id,
        event_type=event_type,
        severity=severity,
        details=details,
        snapshot_id=snapshot_id,
    )
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
    """Save a webcam snapshot to disk and create a DB record."""
    attempt = db.session.get(ExamAttempt, attempt_id)
    if not attempt:
        raise NotFoundError("ExamAttempt", attempt_id)

    dir_path = os.path.join("uploads", "proctor", str(attempt.session_id), str(attempt_id))
    os.makedirs(dir_path, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{snapshot_type}_{timestamp}.jpg"
    file_path = os.path.join(dir_path, filename)

    file.save(file_path)

    snapshot = ProctorSnapshot(
        attempt_id=attempt_id,
        file_path=file_path,
        snapshot_type=snapshot_type,
    )
    db.session.add(snapshot)
    db.session.commit()

    logger.info("Saved snapshot: %s for attempt %s", file_path, attempt_id)
    return snapshot


def get_proctor_status(attempt_id):
    """Get proctoring status for a student's attempt."""
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
    """List proctor events for a session with optional filters."""
    session = db.session.get(ExamSession, session_id)
    if not session:
        raise NotFoundError("ExamSession", session_id)

    attempt_ids = [a.id for a in session.attempts.all()]
    query = ProctorEvent.query.filter(ProctorEvent.attempt_id.in_(attempt_ids))

    if student_id:
        student_attempts = [a.id for a in session.attempts.filter_by(student_id=student_id).all()]
        query = ProctorEvent.query.filter(ProctorEvent.attempt_id.in_(student_attempts))

    if event_type:
        query = query.filter_by(event_type=event_type)

    return [e.to_dict() for e in query.order_by(ProctorEvent.created_at.desc()).all()]


def get_session_snapshots(session_id, student_id=None):
    """List snapshots for a session with optional student filter."""
    session = db.session.get(ExamSession, session_id)
    if not session:
        raise NotFoundError("ExamSession", session_id)

    attempt_ids = [a.id for a in session.attempts.all()]
    if student_id:
        attempt_ids = [a.id for a in session.attempts.filter_by(student_id=student_id).all()]

    snapshots = ProctorSnapshot.query.filter(
        ProctorSnapshot.attempt_id.in_(attempt_ids)
    ).order_by(ProctorSnapshot.created_at.desc()).all()

    return [s.to_dict() for s in snapshots]


def get_proctor_summary(session_id):
    """Get aggregated proctoring stats per student."""
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
    """Create a pending capture request for on-demand snapshot."""
    attempt = db.session.get(ExamAttempt, attempt_id)
    if not attempt:
        raise NotFoundError("ExamAttempt", attempt_id)

    req = CaptureRequest(attempt_id=attempt_id, status="pending")
    db.session.add(req)
    db.session.commit()
    logger.info("Capture requested for attempt %s", attempt_id)
    return req


def fulfill_capture(attempt_id):
    """Mark pending capture requests as fulfilled."""
    pending = CaptureRequest.query.filter_by(attempt_id=attempt_id, status="pending").all()
    for req in pending:
        req.status = "fulfilled"
    db.session.commit()


def toggle_flag(attempt_id):
    """Toggle the flagged status on an attempt."""
    attempt = db.session.get(ExamAttempt, attempt_id)
    if not attempt:
        raise NotFoundError("ExamAttempt", attempt_id)
    attempt.flagged = not attempt.flagged
    db.session.commit()
    logger.info("Toggled flag on attempt %s: %s", attempt_id, attempt.flagged)


def analyze_snapshot(snapshot_id):
    """Optional: Run server-side AI analysis on a snapshot. Skips gracefully if model not loaded."""
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

    # AI analysis would go here using the existing Qwen model
    # For now, this is a hook point — the model integration depends on
    # the AI service's interface which varies by deployment
    logger.info("AI analysis placeholder for snapshot %s", snapshot_id)
```

- [ ] **Step 3: Run tests, full suite, commit**

Run: `pytest tests/test_services/test_proctor_service.py -v`
Then: `pytest tests/ -v --tb=short`

```bash
git add app/services/proctor_service.py tests/test_services/test_proctor_service.py
git commit -m "feat(proctor): add proctor service with event logging, snapshots, warning escalation"
```

---

## Task 3: Proctoring Routes

**Files:**
- Create: `app/routes/proctoring.py`
- Modify: `app/routes/__init__.py`
- Create: `tests/test_routes/test_proctoring.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_routes/test_proctoring.py`:

```python
"""Tests for proctoring API routes."""

import io
import json
from datetime import datetime, timezone, timedelta
from app.models.exam import Exam
from app.models.student import Student
from app.models.exam_session import ExamSession, ExamAssignment
from app.models.exam_attempt import ExamAttempt
from app.models import db as _db


def _past(hours=1):
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()


def _future(hours=1):
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _setup(db, student):
    exam = Exam(title="Test", subject="S", total_marks=10)
    db.session.add(exam)
    db.session.commit()
    session = ExamSession(
        exam_id=exam.id, start_time=_past(1), end_time=_future(1),
        display_mode="one_by_one", save_mode="auto_each", show_result="none",
        proctoring_enabled=True, cheat_response="warn_escalate", warning_threshold=3,
    )
    db.session.add(session)
    db.session.commit()
    db.session.add(ExamAssignment(session_id=session.id, student_id=student.id, assigned_via="individual"))
    db.session.commit()
    attempt = ExamAttempt(session_id=session.id, student_id=student.id, status="in_progress", started_at=_past(0.5))
    db.session.add(attempt)
    db.session.commit()
    return session, attempt


def test_student_log_event(student_client, db):
    client, student = student_client
    session, attempt = _setup(db, student)
    response = client.post(
        f"/api/student/exams/{session.id}/proctor/event",
        data=json.dumps({"event_type": "tab_switch", "severity": "high"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["warning_count"] == 1


def test_student_upload_snapshot(student_client, db):
    client, student = student_client
    session, attempt = _setup(db, student)
    response = client.post(
        f"/api/student/exams/{session.id}/proctor/snapshot",
        data={"file": (io.BytesIO(b"\xff\xd8\xff\xe0fake"), "snap.jpg"), "snapshot_type": "periodic"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert json.loads(response.data)["snapshot_id"] is not None


def test_student_proctor_status(student_client, db):
    client, student = student_client
    session, attempt = _setup(db, student)
    response = client.get(f"/api/student/exams/{session.id}/proctor/status")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["warning_count"] == 0
    assert data["pending_capture"] is False


def test_teacher_list_events(auth_client, db):
    # Create a student + attempt for the session
    student = Student(name="Ali", matricule="001")
    db.session.add(student)
    db.session.commit()
    session, attempt = _setup(db, student)
    # Log an event directly
    from app.services.proctor_service import log_event
    log_event(attempt.id, "tab_switch", "high")

    response = auth_client.get(f"/api/sessions/{session.id}/proctor/events")
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1


def test_teacher_proctor_summary(auth_client, db):
    student = Student(name="Ali", matricule="001")
    db.session.add(student)
    db.session.commit()
    session, attempt = _setup(db, student)

    response = auth_client.get(f"/api/sessions/{session.id}/proctor/summary")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1


def test_teacher_request_capture(auth_client, db):
    student = Student(name="Ali", matricule="001")
    db.session.add(student)
    db.session.commit()
    session, attempt = _setup(db, student)

    response = auth_client.post(f"/api/sessions/{session.id}/proctor/capture/{student.id}")
    assert response.status_code == 200


def test_teacher_toggle_flag(auth_client, db):
    student = Student(name="Ali", matricule="001")
    db.session.add(student)
    db.session.commit()
    session, attempt = _setup(db, student)

    response = auth_client.post(f"/api/sessions/{session.id}/proctor/flag/{attempt.id}")
    assert response.status_code == 200
    assert json.loads(response.data)["flagged"] is True


def test_proctor_event_unauthenticated(client):
    response = client.post("/api/student/exams/1/proctor/event")
    assert response.status_code == 401


def test_teacher_events_unauthenticated(client):
    response = client.get("/api/sessions/1/proctor/events")
    assert response.status_code == 401
```

- [ ] **Step 2: Create the route**

Create `app/routes/proctoring.py`:

```python
"""Proctoring API endpoints — student + teacher."""

import logging
from flask import Blueprint, request, jsonify, g, send_file
from app.auth import require_auth, require_role
from app.services.proctor_service import (
    log_event, save_snapshot, get_proctor_status,
    get_session_events, get_session_snapshots, get_proctor_summary,
    request_capture, fulfill_capture, toggle_flag,
)
from app.models.exam_attempt import ExamAttempt
from app.models.proctor import ProctorSnapshot

logger = logging.getLogger("smartgrader.routes.proctoring")
proctoring_bp = Blueprint("proctoring", __name__)


# --- Student endpoints ---

@proctoring_bp.route("/student/exams/<int:session_id>/proctor/event", methods=["POST"])
@require_auth
@require_role("student")
def student_log_event(session_id):
    student_id = g.current_user.student_id
    attempt = ExamAttempt.query.filter_by(session_id=session_id, student_id=student_id).first()
    if not attempt:
        return jsonify({"error": "No active attempt"}), 404

    data = request.get_json()
    event = log_event(
        attempt_id=attempt.id,
        event_type=data["event_type"],
        severity=data["severity"],
        details=data.get("details"),
    )
    return jsonify({"event_id": event.id, "warning_count": attempt.warning_count})


@proctoring_bp.route("/student/exams/<int:session_id>/proctor/snapshot", methods=["POST"])
@require_auth
@require_role("student")
def student_upload_snapshot(session_id):
    student_id = g.current_user.student_id
    attempt = ExamAttempt.query.filter_by(session_id=session_id, student_id=student_id).first()
    if not attempt:
        return jsonify({"error": "No active attempt"}), 404

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    snapshot_type = request.form.get("snapshot_type", "event_triggered")
    snapshot = save_snapshot(attempt.id, request.files["file"], snapshot_type)

    # Fulfill any pending capture requests if this is on-demand
    if snapshot_type == "on_demand":
        fulfill_capture(attempt.id)

    return jsonify({"snapshot_id": snapshot.id})


@proctoring_bp.route("/student/exams/<int:session_id>/proctor/status", methods=["GET"])
@require_auth
@require_role("student")
def student_proctor_status(session_id):
    student_id = g.current_user.student_id
    attempt = ExamAttempt.query.filter_by(session_id=session_id, student_id=student_id).first()
    if not attempt:
        return jsonify({"error": "No active attempt"}), 404

    status = get_proctor_status(attempt.id)
    return jsonify(status)


# --- Teacher endpoints ---

@proctoring_bp.route("/sessions/<int:session_id>/proctor/events", methods=["GET"])
@require_auth
@require_role("teacher")
def teacher_list_events(session_id):
    student_id = request.args.get("student_id", type=int)
    event_type = request.args.get("event_type")
    events = get_session_events(session_id, student_id=student_id, event_type=event_type)
    return jsonify(events)


@proctoring_bp.route("/sessions/<int:session_id>/proctor/snapshots", methods=["GET"])
@require_auth
@require_role("teacher")
def teacher_list_snapshots(session_id):
    student_id = request.args.get("student_id", type=int)
    snapshots = get_session_snapshots(session_id, student_id=student_id)
    return jsonify(snapshots)


@proctoring_bp.route("/sessions/<int:session_id>/proctor/snapshots/<int:snapshot_id>/image", methods=["GET"])
@require_auth
@require_role("teacher")
def teacher_serve_snapshot(session_id, snapshot_id):
    snapshot = ProctorSnapshot.query.get(snapshot_id)
    if not snapshot:
        return jsonify({"error": "Snapshot not found"}), 404
    return send_file(snapshot.file_path, mimetype="image/jpeg")


@proctoring_bp.route("/sessions/<int:session_id>/proctor/capture/<int:student_id>", methods=["POST"])
@require_auth
@require_role("teacher")
def teacher_request_capture(session_id, student_id):
    attempt = ExamAttempt.query.filter_by(session_id=session_id, student_id=student_id).first()
    if not attempt:
        return jsonify({"error": "No attempt found"}), 404
    req = request_capture(attempt.id)
    return jsonify({"request_id": req.id, "status": req.status})


@proctoring_bp.route("/sessions/<int:session_id>/proctor/summary", methods=["GET"])
@require_auth
@require_role("teacher")
def teacher_proctor_summary(session_id):
    summary = get_proctor_summary(session_id)
    return jsonify(summary)


@proctoring_bp.route("/sessions/<int:session_id>/proctor/flag/<int:attempt_id>", methods=["POST"])
@require_auth
@require_role("teacher")
def teacher_toggle_flag(session_id, attempt_id):
    toggle_flag(attempt_id)
    attempt = ExamAttempt.query.get(attempt_id)
    return jsonify({"attempt_id": attempt_id, "flagged": attempt.flagged})
```

- [ ] **Step 3: Register blueprint**

Add to `app/routes/__init__.py`:

```python
    from app.routes.proctoring import proctoring_bp
    app.register_blueprint(proctoring_bp, url_prefix="/api")
```

- [ ] **Step 4: Run tests, full suite, commit**

Run: `pytest tests/test_routes/test_proctoring.py -v`
Then: `pytest tests/ -v --tb=short`

```bash
git add app/routes/proctoring.py app/routes/__init__.py tests/test_routes/test_proctoring.py
git commit -m "feat(proctor): add proctoring routes — student events/snapshots, teacher monitoring"
```

---

## Task 4: Database Migration

- [ ] **Step 1: Generate migration**

Run: `flask db migrate -m "add proctoring models and columns"`

- [ ] **Step 2: Apply migration**

Run: `flask db upgrade`

- [ ] **Step 3: Commit**

```bash
git add migrations/
git commit -m "feat(proctor): add database migration for proctoring"
```

---

## Task 5: Frontend — Install Dependencies & Proctoring Hooks

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/src/hooks/use-proctor.js`

- [ ] **Step 1: Install TensorFlow.js and BlazeFace**

Run: `cd frontend && npm install @tensorflow/tfjs @tensorflow-models/blazeface`

- [ ] **Step 2: Create use-proctor.js**

Create `frontend/src/hooks/use-proctor.js`:

```javascript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAPI, uploadFile } from "@/lib/api";

// Student hooks
export function useProctorStatus(sessionId, enabled = true) {
  return useQuery({
    queryKey: ["proctor-status", sessionId],
    queryFn: () => fetchAPI(`/student/exams/${sessionId}/proctor/status`),
    enabled: !!sessionId && enabled,
    refetchInterval: 15000,
  });
}

export function useLogEvent() {
  return useMutation({
    mutationFn: ({ sessionId, eventType, severity, details }) =>
      fetchAPI(`/student/exams/${sessionId}/proctor/event`, {
        method: "POST",
        body: JSON.stringify({ event_type: eventType, severity, details }),
      }),
  });
}

export function useUploadSnapshot() {
  return useMutation({
    mutationFn: ({ sessionId, file, snapshotType }) => {
      const formData = new FormData();
      formData.append("file", file, "snapshot.jpg");
      formData.append("snapshot_type", snapshotType);
      return uploadFile(`/student/exams/${sessionId}/proctor/snapshot`, formData);
    },
  });
}

// Teacher hooks
export function useProctorEvents(sessionId, enabled = true) {
  return useQuery({
    queryKey: ["proctor-events", sessionId],
    queryFn: () => fetchAPI(`/sessions/${sessionId}/proctor/events`),
    enabled: !!sessionId && enabled,
    refetchInterval: 10000,
  });
}

export function useProctorSnapshots(sessionId, enabled = true) {
  return useQuery({
    queryKey: ["proctor-snapshots", sessionId],
    queryFn: () => fetchAPI(`/sessions/${sessionId}/proctor/snapshots`),
    enabled: !!sessionId && enabled,
    refetchInterval: 10000,
  });
}

export function useProctorSummary(sessionId, enabled = true) {
  return useQuery({
    queryKey: ["proctor-summary", sessionId],
    queryFn: () => fetchAPI(`/sessions/${sessionId}/proctor/summary`),
    enabled: !!sessionId && enabled,
    refetchInterval: 10000,
  });
}

export function useRequestCapture() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ sessionId, studentId }) =>
      fetchAPI(`/sessions/${sessionId}/proctor/capture/${studentId}`, { method: "POST" }),
    onSuccess: (_, { sessionId }) => qc.invalidateQueries({ queryKey: ["proctor-snapshots", sessionId] }),
  });
}

export function useToggleFlag() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ sessionId, attemptId }) =>
      fetchAPI(`/sessions/${sessionId}/proctor/flag/${attemptId}`, { method: "POST" }),
    onSuccess: (_, { sessionId }) => qc.invalidateQueries({ queryKey: ["proctor-summary", sessionId] }),
  });
}
```

- [ ] **Step 3: Commit**

```bash
cd frontend && git add package.json package-lock.json src/hooks/use-proctor.js
git commit -m "feat(proctor): add TensorFlow.js deps and proctoring hooks"
```

---

## Task 6: Frontend — ProctorEngine, FullscreenLockdown, ProctorWarningBanner

**Files:**
- Create: `frontend/src/components/ProctorEngine.jsx`
- Create: `frontend/src/components/FullscreenLockdown.jsx`
- Create: `frontend/src/components/ProctorWarningBanner.jsx`

- [ ] **Step 1: Create ProctorEngine.jsx**

This is the core invisible component. Key behaviors:
- Mounts hidden `<video>` element, requests webcam via `getUserMedia`
- Loads BlazeFace model once on mount
- Runs face detection every 2s: 0 faces → "no_face" (high), 2+ faces → "multiple_faces" (high)
- Tracks consecutive off-gaze detections: 5+ consecutive (10s) → "gaze_away" (medium)
- Registers DOM event listeners for: visibilitychange, blur, copy/cut/paste, contextmenu, keydown (Ctrl+C/V/A, PrintScreen)
- Event throttling: Map of `eventType → lastSentTime`, skip if < 10s
- On each suspicious event: capture webcam frame via `canvas.toBlob("image/jpeg")`, upload with `useUploadSnapshot`
- Periodic snapshot: `setInterval(60000)` → capture + upload as "periodic"
- All events sent via `useLogEvent` mutation
- Props: `sessionId`, `onError` (called if camera denied)
- Cleanup: stop webcam stream and clear all intervals on unmount

- [ ] **Step 2: Create FullscreenLockdown.jsx**

```jsx
import { useEffect, useState, useCallback } from "react";

export default function FullscreenLockdown({ onViolation }) {
  const [exited, setExited] = useState(false);

  useEffect(() => {
    document.documentElement.requestFullscreen?.().catch(() => {});

    const handleChange = () => {
      if (!document.fullscreenElement) {
        setExited(true);
        onViolation?.();
      } else {
        setExited(false);
      }
    };

    document.addEventListener("fullscreenchange", handleChange);
    return () => document.removeEventListener("fullscreenchange", handleChange);
  }, [onViolation]);

  const reenter = useCallback(() => {
    document.documentElement.requestFullscreen?.().catch(() => {});
  }, []);

  if (!exited) return null;

  return (
    <div className="fixed inset-0 z-[100] bg-black/90 flex items-center justify-center">
      <div className="text-center space-y-4">
        <div className="text-xl font-bold text-white">Full-Screen Required</div>
        <p className="text-muted-foreground">Please return to full-screen mode to continue your exam.</p>
        <button
          onClick={reenter}
          className="rounded-lg bg-primary px-6 py-3 text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
        >
          Re-enter Full Screen
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Create ProctorWarningBanner.jsx**

```jsx
import { useProctorStatus } from "@/hooks/use-proctor";

export default function ProctorWarningBanner({ sessionId, onCaptureRequest }) {
  const { data: status } = useProctorStatus(sessionId);

  if (!status) return null;

  // Trigger capture if server requests it
  if (status.pending_capture && onCaptureRequest) {
    onCaptureRequest();
  }

  if (status.flagged) {
    return (
      <div className="fixed top-16 left-0 right-0 z-50 bg-destructive/90 text-destructive-foreground text-center py-2 text-sm font-medium">
        Your exam has been flagged for review
      </div>
    );
  }

  if (status.warning_count > 0) {
    return (
      <div className="fixed top-16 left-0 right-0 z-50 bg-yellow-500/90 text-black text-center py-2 text-sm font-medium">
        Suspicious activity detected — Warning {status.warning_count} of {status.warning_threshold}
      </div>
    );
  }

  return null;
}
```

- [ ] **Step 4: Verify build**

Run: `cd frontend && npm run build`

- [ ] **Step 5: Commit**

```bash
cd frontend && git add src/components/ProctorEngine.jsx src/components/FullscreenLockdown.jsx src/components/ProctorWarningBanner.jsx
git commit -m "feat(proctor): add ProctorEngine, FullscreenLockdown, ProctorWarningBanner components"
```

---

## Task 7: Frontend — Update TakeExam, CreateSession, SessionDetail

**Files:**
- Modify: `frontend/src/pages/TakeExam.jsx`
- Modify: `frontend/src/pages/CreateSession.jsx`
- Modify: `frontend/src/pages/SessionDetail.jsx`

- [ ] **Step 1: Update TakeExam.jsx**

Add conditional mounting of proctoring components. After the exam data is loaded (from `useStartAttempt`), check the session settings:

```jsx
import ProctorEngine from "@/components/ProctorEngine";
import FullscreenLockdown from "@/components/FullscreenLockdown";
import ProctorWarningBanner from "@/components/ProctorWarningBanner";
```

Inside the component, after loading exam data:
```jsx
{examData?.proctoring_enabled && (
  <ProctorEngine sessionId={sessionId} onError={(msg) => setError(msg)} />
)}
{examData?.lockdown_enabled && (
  <FullscreenLockdown onViolation={() => {/* ProctorEngine handles logging */}} />
)}
{examData?.proctoring_enabled && examData?.cheat_response !== "log_only" && (
  <ProctorWarningBanner sessionId={sessionId} onCaptureRequest={handleCaptureRequest} />
)}
```

The `handleCaptureRequest` function captures current webcam frame and uploads it as "on_demand". This requires ProctorEngine to expose a `captureFrame()` method via ref or callback.

IMPORTANT: The start_attempt response needs to include proctoring settings. Read the current `_build_attempt_response` in `exam_take_service.py` and add these fields to the response:
```python
"proctoring_enabled": session.proctoring_enabled,
"lockdown_enabled": session.lockdown_enabled,
"cheat_response": session.cheat_response,
"warning_threshold": session.warning_threshold,
```

- [ ] **Step 2: Update CreateSession.jsx**

Add a proctoring settings section to the form after the existing settings:

```jsx
{/* Proctoring Settings */}
<div className="space-y-3">
  <h3 className="font-medium">Proctoring</h3>
  <label className="flex items-center gap-2">
    <input type="checkbox" checked={form.proctoring_enabled} onChange={...} />
    <span className="text-sm">Enable Proctoring (webcam + event tracking)</span>
  </label>
  {form.proctoring_enabled && (
    <>
      <label className="flex items-center gap-2">
        <input type="checkbox" checked={form.lockdown_enabled} onChange={...} />
        <span className="text-sm">Full-Screen Lockdown</span>
      </label>
      <div>
        <label className="text-sm font-medium">Cheat Response</label>
        {/* Radio buttons: log_only, warn, warn_escalate */}
      </div>
      {form.cheat_response === "warn_escalate" && (
        <div>
          <label className="text-sm font-medium">Warning Threshold</label>
          <input type="number" min="1" value={form.warning_threshold} onChange={...} />
        </div>
      )}
    </>
  )}
</div>
```

Add default values to form state: `proctoring_enabled: false, lockdown_enabled: false, cheat_response: "log_only", warning_threshold: 3`.

- [ ] **Step 3: Update SessionDetail.jsx**

Add a "Proctoring" tab that shows when `proctoring_enabled` is true:

- Use `useProctorSummary(sessionId)` for the overview table
- Use `useProctorEvents(sessionId)` for event timeline (expandable per student)
- Use `useProctorSnapshots(sessionId)` for snapshot gallery
- Add "Capture Now" button per student using `useRequestCapture()`
- Add "Flag/Unflag" toggle per student using `useToggleFlag()`
- Color-code warnings: green (0-1), yellow (2+), red (flagged)

- [ ] **Step 4: Update exam_take_service.py**

In `app/services/exam_take_service.py`, update the `_build_attempt_response` function to include proctoring settings in the return dict. Add these 4 fields:

```python
"proctoring_enabled": session.proctoring_enabled,
"lockdown_enabled": session.lockdown_enabled,
"cheat_response": session.cheat_response,
"warning_threshold": session.warning_threshold,
```

- [ ] **Step 5: Verify build**

Run: `cd frontend && npm run build`
Run: `pytest tests/ -v --tb=short`

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/TakeExam.jsx frontend/src/pages/CreateSession.jsx frontend/src/pages/SessionDetail.jsx app/services/exam_take_service.py
git commit -m "feat(proctor): integrate proctoring into TakeExam, CreateSession, SessionDetail"
```

---

## Task 8: End-to-End Verification

- [ ] **Step 1: Run full backend test suite**

Run: `pytest tests/ -v --tb=short`
Expected: all tests pass

- [ ] **Step 2: Run frontend build**

Run: `cd frontend && npm run build`
Expected: build succeeds

- [ ] **Step 3: Manual smoke test**

Start the app and test:
1. Create an exam session with proctoring enabled, lockdown on, cheat_response=warn_escalate, threshold=3
2. Login as student → start exam → verify webcam prompt appears
3. Switch tabs → verify warning banner appears
4. Login as teacher → check SessionDetail proctoring tab → events and snapshot should appear
5. Click "Capture Now" → verify student's browser sends snapshot
6. Trigger 3+ events → verify student gets flagged

- [ ] **Step 4: Final commit if fixes needed**

```bash
git add -A
git commit -m "fix(proctor): address issues found during smoke testing"
```

---

## Summary

| Task | Description | Tests |
|------|-------------|-------|
| 1 | Proctor models + ExamSession/ExamAttempt updates | 7 |
| 2 | Proctor service | 13 |
| 3 | Proctoring routes | 9 |
| 4 | Database migration | - |
| 5 | Frontend deps + hooks | - |
| 6 | ProctorEngine, Lockdown, WarningBanner | - |
| 7 | Update TakeExam, CreateSession, SessionDetail | - |
| 8 | E2E verification | manual |

**Total: 8 tasks, ~29 automated tests, 8 commits**
