# Phase 2: Online Exam Engine — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an online exam-taking system where teachers schedule exam sessions with configurable settings and students take MCQ exams digitally through the browser with countdown timers, answer persistence, and auto-submit.

**Architecture:** REST + polling approach. New models (StudentGroup, ExamSession, ExamAttempt, OnlineAnswer) store exam state. Services handle group management, session scheduling, and the exam-taking flow (start → answer → submit → grade). Frontend adds teacher management pages and a student exam-taking UI with two display modes. Status is computed from timestamps, auto-submit is lazy (no background scheduler).

**Tech Stack:** Flask + SQLAlchemy (backend), React 19 + React Query + React Router 7 (frontend) — zero new dependencies.

---

## File Structure

```
NEW FILES:
  app/models/group.py                — StudentGroup, StudentGroupMember
  app/models/exam_session.py         — ExamSession, ExamAssignment
  app/models/exam_attempt.py         — ExamAttempt
  app/models/online_answer.py        — OnlineAnswer
  app/services/group_service.py      — group CRUD + member management
  app/services/session_service.py    — session CRUD, assignment, monitoring, status
  app/services/exam_take_service.py  — exam flow: start, answer, submit, grade, auto-submit
  app/routes/groups.py               — /api/groups/* blueprint (teacher)
  app/routes/sessions.py             — /api/sessions/* blueprint (teacher)
  app/routes/student_exam.py         — /api/student/exams/* blueprint (student)
  tests/test_models/test_group.py
  tests/test_models/test_exam_session.py
  tests/test_services/test_group_service.py
  tests/test_services/test_session_service.py
  tests/test_services/test_exam_take_service.py
  tests/test_routes/test_groups.py
  tests/test_routes/test_sessions.py
  tests/test_routes/test_student_exam.py
  frontend/src/components/layout/StudentLayout.jsx
  frontend/src/pages/StudentGroups.jsx
  frontend/src/pages/ExamSessions.jsx
  frontend/src/pages/CreateSession.jsx
  frontend/src/pages/SessionDetail.jsx
  frontend/src/pages/StudentDashboard.jsx
  frontend/src/pages/TakeExam.jsx
  frontend/src/pages/ExamResult.jsx
  frontend/src/hooks/use-groups.js
  frontend/src/hooks/use-sessions.js
  frontend/src/hooks/use-student-exam.js

MODIFIED FILES:
  app/models/__init__.py             — export new models
  app/routes/__init__.py             — register 3 new blueprints
  tests/conftest.py                  — add student_client fixture
  frontend/src/App.jsx               — add student routes + new teacher routes
  frontend/src/components/layout/Sidebar.jsx — add Groups + Online Exams nav items
```

---

## Task 1: StudentGroup & StudentGroupMember Models

**Files:**
- Create: `app/models/group.py`
- Modify: `app/models/__init__.py`
- Create: `tests/test_models/test_group.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_models/test_group.py`:

```python
"""Tests for StudentGroup and StudentGroupMember models."""

from app.models.group import StudentGroup, StudentGroupMember
from app.models.student import Student
from app.models import db as _db


def test_create_group(db):
    group = StudentGroup(name="CS Year 3 Group A")
    db.session.add(group)
    db.session.commit()

    assert group.id is not None
    assert group.name == "CS Year 3 Group A"
    assert group.created_at is not None


def test_add_member_to_group(db):
    group = StudentGroup(name="G1")
    student = Student(name="Ali", matricule="001")
    db.session.add_all([group, student])
    db.session.commit()

    member = StudentGroupMember(group_id=group.id, student_id=student.id)
    db.session.add(member)
    db.session.commit()

    assert member.id is not None
    assert group.members.count() == 1


def test_group_to_dict(db):
    group = StudentGroup(name="Test Group")
    db.session.add(group)
    db.session.commit()

    s1 = Student(name="A", matricule="001")
    s2 = Student(name="B", matricule="002")
    db.session.add_all([s1, s2])
    db.session.commit()

    db.session.add_all([
        StudentGroupMember(group_id=group.id, student_id=s1.id),
        StudentGroupMember(group_id=group.id, student_id=s2.id),
    ])
    db.session.commit()

    d = group.to_dict()
    assert d["name"] == "Test Group"
    assert d["member_count"] == 2

    d_full = group.to_dict(include_members=True)
    assert len(d_full["members"]) == 2
    assert d_full["members"][0]["name"] in ("A", "B")


def test_group_cascade_delete(db):
    group = StudentGroup(name="Del")
    student = Student(name="X", matricule="099")
    db.session.add_all([group, student])
    db.session.commit()

    db.session.add(StudentGroupMember(group_id=group.id, student_id=student.id))
    db.session.commit()

    db.session.delete(group)
    db.session.commit()

    assert StudentGroupMember.query.count() == 0
    assert Student.query.count() == 1  # student not deleted
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_models/test_group.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.models.group'`

- [ ] **Step 3: Create the models**

Create `app/models/group.py`:

```python
"""Student group models."""

from datetime import datetime, timezone
from app.models import db


class StudentGroup(db.Model):
    __tablename__ = "student_groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.String(30), default=lambda: datetime.now(timezone.utc).isoformat())

    members = db.relationship(
        "StudentGroupMember", backref="group", cascade="all, delete-orphan", lazy="dynamic"
    )

    def to_dict(self, include_members=False):
        data = {
            "id": self.id,
            "name": self.name,
            "member_count": self.members.count(),
            "created_at": self.created_at,
        }
        if include_members:
            data["members"] = [
                {"id": m.student.id, "name": m.student.name, "matricule": m.student.matricule}
                for m in self.members.all()
            ]
        return data


class StudentGroupMember(db.Model):
    __tablename__ = "student_group_members"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("student_groups.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)

    student = db.relationship("Student")

    __table_args__ = (
        db.UniqueConstraint("group_id", "student_id", name="uq_group_student"),
    )
```

- [ ] **Step 4: Export in models/__init__.py**

Add at the end of `app/models/__init__.py`:

```python
from app.models.group import StudentGroup, StudentGroupMember  # noqa: E402, F401
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_models/test_group.py -v`
Expected: all 4 tests PASS

- [ ] **Step 6: Run full test suite**

Run: `pytest tests/ -v --tb=short`
Expected: all tests pass

- [ ] **Step 7: Commit**

```bash
git add app/models/group.py app/models/__init__.py tests/test_models/test_group.py
git commit -m "feat(exam): add StudentGroup and StudentGroupMember models"
```

---

## Task 2: ExamSession & ExamAssignment Models

**Files:**
- Create: `app/models/exam_session.py`
- Modify: `app/models/__init__.py`
- Create: `tests/test_models/test_exam_session.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_models/test_exam_session.py`:

```python
"""Tests for ExamSession, ExamAssignment, ExamAttempt, OnlineAnswer models."""

from app.models.exam_session import ExamSession, ExamAssignment
from app.models.exam import Exam
from app.models.student import Student
from app.models import db as _db


def _make_exam(db):
    exam = Exam(title="Math", subject="Science", total_marks=100)
    db.session.add(exam)
    db.session.commit()
    return exam


def test_create_exam_session(db):
    exam = _make_exam(db)
    session = ExamSession(
        exam_id=exam.id,
        start_time="2026-04-10T09:00:00Z",
        end_time="2026-04-10T10:00:00Z",
        display_mode="one_by_one",
        save_mode="auto_each",
        show_result="score_only",
    )
    db.session.add(session)
    db.session.commit()

    assert session.id is not None
    assert session.randomize is False
    assert session.display_mode == "one_by_one"


def test_exam_session_to_dict(db):
    exam = _make_exam(db)
    session = ExamSession(
        exam_id=exam.id,
        start_time="2026-04-10T09:00:00Z",
        end_time="2026-04-10T10:00:00Z",
        display_mode="all_at_once",
        save_mode="manual",
        randomize=True,
        show_result="score_and_answers",
    )
    db.session.add(session)
    db.session.commit()

    d = session.to_dict()
    assert d["exam_id"] == exam.id
    assert d["display_mode"] == "all_at_once"
    assert d["save_mode"] == "manual"
    assert d["randomize"] is True
    assert d["show_result"] == "score_and_answers"
    assert "exam_title" in d


def test_create_exam_assignment(db):
    exam = _make_exam(db)
    session = ExamSession(
        exam_id=exam.id,
        start_time="2026-04-10T09:00:00Z",
        end_time="2026-04-10T10:00:00Z",
        display_mode="one_by_one",
        save_mode="auto_each",
        show_result="none",
    )
    student = Student(name="Ali", matricule="001")
    db.session.add_all([session, student])
    db.session.commit()

    assignment = ExamAssignment(
        session_id=session.id,
        student_id=student.id,
        assigned_via="individual",
    )
    db.session.add(assignment)
    db.session.commit()

    assert assignment.id is not None
    assert session.assignments.count() == 1


def test_session_cascade_delete(db):
    exam = _make_exam(db)
    session = ExamSession(
        exam_id=exam.id,
        start_time="2026-04-10T09:00:00Z",
        end_time="2026-04-10T10:00:00Z",
        display_mode="one_by_one",
        save_mode="auto_each",
        show_result="none",
    )
    student = Student(name="X", matricule="099")
    db.session.add_all([session, student])
    db.session.commit()

    db.session.add(ExamAssignment(session_id=session.id, student_id=student.id, assigned_via="individual"))
    db.session.commit()

    db.session.delete(session)
    db.session.commit()

    assert ExamAssignment.query.count() == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_models/test_exam_session.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Create the models**

Create `app/models/exam_session.py`:

```python
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
```

- [ ] **Step 4: Export in models/__init__.py**

Add at the end of `app/models/__init__.py`:

```python
from app.models.exam_session import ExamSession, ExamAssignment  # noqa: E402, F401
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_models/test_exam_session.py -v`
Expected: all 4 tests PASS

- [ ] **Step 6: Run full suite, commit**

Run: `pytest tests/ -v --tb=short`

```bash
git add app/models/exam_session.py app/models/__init__.py tests/test_models/test_exam_session.py
git commit -m "feat(exam): add ExamSession and ExamAssignment models"
```

---

## Task 3: ExamAttempt & OnlineAnswer Models

**Files:**
- Create: `app/models/exam_attempt.py`
- Create: `app/models/online_answer.py`
- Modify: `app/models/__init__.py`

- [ ] **Step 1: Write failing tests**

Add to the bottom of `tests/test_models/test_exam_session.py`:

```python
from app.models.exam_attempt import ExamAttempt
from app.models.online_answer import OnlineAnswer
from app.models.exam import Question, Choice


def _make_session(db):
    exam = _make_exam(db)
    session = ExamSession(
        exam_id=exam.id,
        start_time="2026-04-10T09:00:00Z",
        end_time="2026-04-10T10:00:00Z",
        display_mode="one_by_one",
        save_mode="auto_each",
        show_result="score_only",
    )
    db.session.add(session)
    db.session.commit()
    return exam, session


def test_create_exam_attempt(db):
    exam, session = _make_session(db)
    student = Student(name="Ali", matricule="100")
    db.session.add(student)
    db.session.commit()

    attempt = ExamAttempt(
        session_id=session.id,
        student_id=student.id,
        status="in_progress",
        started_at="2026-04-10T09:01:00Z",
    )
    db.session.add(attempt)
    db.session.commit()

    assert attempt.id is not None
    assert attempt.score is None
    assert attempt.question_order is None


def test_create_online_answer(db):
    exam, session = _make_session(db)
    student = Student(name="Ali", matricule="100")
    db.session.add(student)
    db.session.commit()

    q = Question(exam_id=exam.id, question_text="Q1", question_choices_number=2, marks=5)
    db.session.add(q)
    db.session.commit()
    c = Choice(question_id=q.id, choice_label="A", choice_text="Answer A", is_correct=1)
    db.session.add(c)
    db.session.commit()

    attempt = ExamAttempt(
        session_id=session.id, student_id=student.id,
        status="in_progress", started_at="2026-04-10T09:01:00Z",
    )
    db.session.add(attempt)
    db.session.commit()

    answer = OnlineAnswer(
        attempt_id=attempt.id, question_id=q.id,
        selected_choice_id=c.id, answered_at="2026-04-10T09:02:00Z",
    )
    db.session.add(answer)
    db.session.commit()

    assert answer.id is not None
    assert attempt.answers.count() == 1


def test_attempt_to_dict(db):
    exam, session = _make_session(db)
    student = Student(name="Ali", matricule="100")
    db.session.add(student)
    db.session.commit()

    attempt = ExamAttempt(
        session_id=session.id, student_id=student.id,
        status="submitted", started_at="2026-04-10T09:01:00Z",
        submitted_at="2026-04-10T09:45:00Z", score=80, percentage=80.0,
    )
    db.session.add(attempt)
    db.session.commit()

    d = attempt.to_dict()
    assert d["status"] == "submitted"
    assert d["score"] == 80
    assert d["student_name"] == "Ali"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_models/test_exam_session.py -v`
Expected: FAIL — ModuleNotFoundError for exam_attempt/online_answer

- [ ] **Step 3: Create ExamAttempt model**

Create `app/models/exam_attempt.py`:

```python
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

    student = db.relationship("Student")
    answers = db.relationship(
        "OnlineAnswer", backref="attempt", cascade="all, delete-orphan", lazy="dynamic"
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
            "answer_count": self.answers.count(),
        }
```

- [ ] **Step 4: Create OnlineAnswer model**

Create `app/models/online_answer.py`:

```python
"""Online answer model."""

from app.models import db


class OnlineAnswer(db.Model):
    __tablename__ = "online_answers"

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("exam_attempts.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    selected_choice_id = db.Column(db.Integer, db.ForeignKey("choices.id"), nullable=True)
    answered_at = db.Column(db.String(30))

    question = db.relationship("Question")
    selected_choice = db.relationship("Choice")

    __table_args__ = (
        db.UniqueConstraint("attempt_id", "question_id", name="uq_answer_attempt_question"),
    )
```

- [ ] **Step 5: Export in models/__init__.py**

Add at the end of `app/models/__init__.py`:

```python
from app.models.exam_attempt import ExamAttempt  # noqa: E402, F401
from app.models.online_answer import OnlineAnswer  # noqa: E402, F401
```

- [ ] **Step 6: Run tests, full suite, commit**

Run: `pytest tests/test_models/test_exam_session.py -v`
Then: `pytest tests/ -v --tb=short`

```bash
git add app/models/exam_attempt.py app/models/online_answer.py app/models/__init__.py tests/test_models/test_exam_session.py
git commit -m "feat(exam): add ExamAttempt and OnlineAnswer models"
```

---

## Task 4: Group Service

**Files:**
- Create: `app/services/group_service.py`
- Create: `tests/test_services/test_group_service.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_services/test_group_service.py`:

```python
"""Tests for group service."""

import pytest
from app.models.student import Student
from app.models.group import StudentGroup, StudentGroupMember
from app.services.group_service import (
    create_group, get_all_groups, get_group_by_id,
    delete_group, add_members, remove_member,
)
from app.errors import NotFoundError


def test_create_group(db):
    group = create_group("CS Year 3")
    assert group.id is not None
    assert group.name == "CS Year 3"


def test_get_all_groups(db):
    create_group("G1")
    create_group("G2")
    groups = get_all_groups()
    assert len(groups) == 2


def test_get_group_by_id(db):
    group = create_group("G1")
    found = get_group_by_id(group.id)
    assert found.name == "G1"


def test_get_group_not_found(db):
    with pytest.raises(NotFoundError):
        get_group_by_id(999)


def test_delete_group(db):
    group = create_group("Del")
    delete_group(group.id)
    assert StudentGroup.query.count() == 0


def test_add_members(db):
    group = create_group("G1")
    s1 = Student(name="A", matricule="001")
    s2 = Student(name="B", matricule="002")
    db.session.add_all([s1, s2])
    db.session.commit()

    count = add_members(group.id, [s1.id, s2.id])
    assert count == 2
    assert group.members.count() == 2


def test_add_members_skip_duplicates(db):
    group = create_group("G1")
    s1 = Student(name="A", matricule="001")
    db.session.add(s1)
    db.session.commit()

    add_members(group.id, [s1.id])
    count = add_members(group.id, [s1.id])
    assert count == 0
    assert group.members.count() == 1


def test_remove_member(db):
    group = create_group("G1")
    s1 = Student(name="A", matricule="001")
    db.session.add(s1)
    db.session.commit()

    add_members(group.id, [s1.id])
    remove_member(group.id, s1.id)
    assert group.members.count() == 0
```

- [ ] **Step 2: Create the service**

Create `app/services/group_service.py`:

```python
"""Student group management service."""

import logging
from app.models import db
from app.models.group import StudentGroup, StudentGroupMember
from app.errors import NotFoundError

logger = logging.getLogger("smartgrader.services.group")


def create_group(name):
    """Create a new student group."""
    group = StudentGroup(name=name)
    db.session.add(group)
    db.session.commit()
    logger.info("Created group: %s", name)
    return group


def get_all_groups():
    """List all student groups."""
    return StudentGroup.query.order_by(StudentGroup.name).all()


def get_group_by_id(group_id):
    """Get a group by ID. Raises NotFoundError if not found."""
    group = db.session.get(StudentGroup, group_id)
    if not group:
        raise NotFoundError("Group", group_id)
    return group


def delete_group(group_id):
    """Delete a group and all its memberships."""
    group = get_group_by_id(group_id)
    db.session.delete(group)
    db.session.commit()
    logger.info("Deleted group: %s", group_id)


def add_members(group_id, student_ids):
    """Add students to a group. Skips duplicates. Returns count added."""
    group = get_group_by_id(group_id)
    existing = {m.student_id for m in group.members.all()}
    added = 0
    for sid in student_ids:
        if sid not in existing:
            db.session.add(StudentGroupMember(group_id=group.id, student_id=sid))
            existing.add(sid)
            added += 1
    db.session.commit()
    logger.info("Added %d members to group %s", added, group_id)
    return added


def remove_member(group_id, student_id):
    """Remove a student from a group."""
    member = StudentGroupMember.query.filter_by(
        group_id=group_id, student_id=student_id
    ).first()
    if member:
        db.session.delete(member)
        db.session.commit()
        logger.info("Removed student %s from group %s", student_id, group_id)
```

- [ ] **Step 3: Run tests, full suite, commit**

Run: `pytest tests/test_services/test_group_service.py -v`
Then: `pytest tests/ -v --tb=short`

```bash
git add app/services/group_service.py tests/test_services/test_group_service.py
git commit -m "feat(exam): add group service with CRUD and member management"
```

---

## Task 5: Session Service

**Files:**
- Create: `app/services/session_service.py`
- Create: `tests/test_services/test_session_service.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_services/test_session_service.py`:

```python
"""Tests for session service."""

import pytest
from datetime import datetime, timezone, timedelta
from app.models.exam import Exam
from app.models.student import Student
from app.models.group import StudentGroup
from app.models.exam_session import ExamSession, ExamAssignment
from app.services.group_service import create_group, add_members
from app.services.session_service import (
    create_session, get_all_sessions, get_session_by_id,
    update_session, delete_session, assign_students,
    get_monitor_data, compute_session_status,
)
from app.errors import NotFoundError


def _make_exam(db):
    exam = Exam(title="Math", subject="Science", total_marks=100)
    db.session.add(exam)
    db.session.commit()
    return exam


def _future(hours=1):
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _past(hours=1):
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()


def test_create_session(db):
    exam = _make_exam(db)
    session = create_session(
        exam_id=exam.id,
        start_time=_future(1),
        end_time=_future(2),
        display_mode="one_by_one",
        save_mode="auto_each",
        show_result="score_only",
    )
    assert session.id is not None
    assert session.exam_id == exam.id


def test_create_session_invalid_exam(db):
    with pytest.raises(NotFoundError):
        create_session(
            exam_id=999,
            start_time=_future(1),
            end_time=_future(2),
            display_mode="one_by_one",
            save_mode="auto_each",
            show_result="none",
        )


def test_get_all_sessions(db):
    exam = _make_exam(db)
    create_session(exam_id=exam.id, start_time=_future(1), end_time=_future(2),
                   display_mode="one_by_one", save_mode="auto_each", show_result="none")
    sessions = get_all_sessions()
    assert len(sessions) == 1


def test_compute_session_status_scheduled(db):
    exam = _make_exam(db)
    session = create_session(exam_id=exam.id, start_time=_future(1), end_time=_future(2),
                             display_mode="one_by_one", save_mode="auto_each", show_result="none")
    assert compute_session_status(session) == "scheduled"


def test_compute_session_status_active(db):
    exam = _make_exam(db)
    session = create_session(exam_id=exam.id, start_time=_past(1), end_time=_future(1),
                             display_mode="one_by_one", save_mode="auto_each", show_result="none")
    assert compute_session_status(session) == "active"


def test_compute_session_status_ended(db):
    exam = _make_exam(db)
    session = create_session(exam_id=exam.id, start_time=_past(2), end_time=_past(1),
                             display_mode="one_by_one", save_mode="auto_each", show_result="none")
    assert compute_session_status(session) == "ended"


def test_update_session(db):
    exam = _make_exam(db)
    session = create_session(exam_id=exam.id, start_time=_future(1), end_time=_future(2),
                             display_mode="one_by_one", save_mode="auto_each", show_result="none")
    updated = update_session(session.id, display_mode="all_at_once")
    assert updated.display_mode == "all_at_once"


def test_delete_session(db):
    exam = _make_exam(db)
    session = create_session(exam_id=exam.id, start_time=_future(1), end_time=_future(2),
                             display_mode="one_by_one", save_mode="auto_each", show_result="none")
    delete_session(session.id)
    assert ExamSession.query.count() == 0


def test_assign_students_individual(db):
    exam = _make_exam(db)
    session = create_session(exam_id=exam.id, start_time=_future(1), end_time=_future(2),
                             display_mode="one_by_one", save_mode="auto_each", show_result="none")
    s1 = Student(name="A", matricule="001")
    s2 = Student(name="B", matricule="002")
    db.session.add_all([s1, s2])
    db.session.commit()

    count = assign_students(session.id, student_ids=[s1.id, s2.id], group_ids=[])
    assert count == 2


def test_assign_students_via_group(db):
    exam = _make_exam(db)
    session = create_session(exam_id=exam.id, start_time=_future(1), end_time=_future(2),
                             display_mode="one_by_one", save_mode="auto_each", show_result="none")
    s1 = Student(name="A", matricule="001")
    s2 = Student(name="B", matricule="002")
    db.session.add_all([s1, s2])
    db.session.commit()

    group = create_group("G1")
    add_members(group.id, [s1.id, s2.id])

    count = assign_students(session.id, student_ids=[], group_ids=[group.id])
    assert count == 2


def test_assign_students_skip_duplicates(db):
    exam = _make_exam(db)
    session = create_session(exam_id=exam.id, start_time=_future(1), end_time=_future(2),
                             display_mode="one_by_one", save_mode="auto_each", show_result="none")
    s1 = Student(name="A", matricule="001")
    db.session.add(s1)
    db.session.commit()

    assign_students(session.id, student_ids=[s1.id], group_ids=[])
    count = assign_students(session.id, student_ids=[s1.id], group_ids=[])
    assert count == 0
```

- [ ] **Step 2: Create the service**

Create `app/services/session_service.py`:

```python
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
    from app.services.exam_take_service import auto_submit_expired

    session = get_session_by_id(session_id)

    if compute_session_status(session) == "ended":
        auto_submit_expired(session_id)

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
```

- [ ] **Step 3: Run tests, full suite, commit**

Run: `pytest tests/test_services/test_session_service.py -v`
Then: `pytest tests/ -v --tb=short`

```bash
git add app/services/session_service.py tests/test_services/test_session_service.py
git commit -m "feat(exam): add session service with CRUD, assignment, and monitoring"
```

---

## Task 6: Exam Take Service

**Files:**
- Create: `app/services/exam_take_service.py`
- Create: `tests/test_services/test_exam_take_service.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_services/test_exam_take_service.py`:

```python
"""Tests for exam take service."""

import json
import pytest
from datetime import datetime, timezone, timedelta
from app.models.exam import Exam, Question, Choice
from app.models.student import Student
from app.models.user import User
from app.models.exam_session import ExamSession, ExamAssignment
from app.models.exam_attempt import ExamAttempt
from app.models import db as _db
from app.services.exam_take_service import (
    get_student_exams, start_attempt, save_answer, save_answers_batch,
    submit_attempt, get_exam_status, get_attempt_result, auto_submit_expired,
)
from app.errors import NotFoundError, SmartGraderError


def _future(hours=1):
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _past(hours=1):
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()


def _setup_exam(db, start_time=None, end_time=None, randomize=False, show_result="score_only"):
    """Create exam with 2 questions, 2 choices each, session, student, and assignment."""
    exam = Exam(title="Test Exam", subject="Math", total_marks=10)
    db.session.add(exam)
    db.session.commit()

    q1 = Question(exam_id=exam.id, question_text="Q1", question_choices_number=2, marks=5)
    q2 = Question(exam_id=exam.id, question_text="Q2", question_choices_number=2, marks=5)
    db.session.add_all([q1, q2])
    db.session.commit()

    c1a = Choice(question_id=q1.id, choice_label="A", choice_text="Correct", is_correct=1)
    c1b = Choice(question_id=q1.id, choice_label="B", choice_text="Wrong", is_correct=0)
    c2a = Choice(question_id=q2.id, choice_label="A", choice_text="Wrong", is_correct=0)
    c2b = Choice(question_id=q2.id, choice_label="B", choice_text="Correct", is_correct=1)
    db.session.add_all([c1a, c1b, c2a, c2b])
    db.session.commit()

    session = ExamSession(
        exam_id=exam.id,
        start_time=start_time or _past(1),
        end_time=end_time or _future(1),
        display_mode="one_by_one",
        save_mode="auto_each",
        show_result=show_result,
        randomize=randomize,
    )
    db.session.add(session)
    db.session.commit()

    student = Student(name="Ali", matricule="001")
    db.session.add(student)
    db.session.commit()

    db.session.add(ExamAssignment(session_id=session.id, student_id=student.id, assigned_via="individual"))
    db.session.commit()

    return {
        "exam": exam, "session": session, "student": student,
        "q1": q1, "q2": q2, "c1a": c1a, "c1b": c1b, "c2a": c2a, "c2b": c2b,
    }


def test_get_student_exams(db):
    data = _setup_exam(db)
    exams = get_student_exams(data["student"].id)
    assert len(exams["active"]) == 1
    assert len(exams["upcoming"]) == 0
    assert len(exams["completed"]) == 0


def test_start_attempt(db):
    data = _setup_exam(db)
    result = start_attempt(data["session"].id, data["student"].id)
    assert result["attempt_id"] is not None
    assert len(result["questions"]) == 2
    assert result["remaining_seconds"] > 0


def test_start_attempt_resume(db):
    data = _setup_exam(db)
    r1 = start_attempt(data["session"].id, data["student"].id)
    r2 = start_attempt(data["session"].id, data["student"].id)
    assert r1["attempt_id"] == r2["attempt_id"]


def test_start_attempt_not_assigned(db):
    data = _setup_exam(db)
    other = Student(name="Other", matricule="999")
    db.session.add(other)
    db.session.commit()
    with pytest.raises(SmartGraderError, match="not assigned"):
        start_attempt(data["session"].id, other.id)


def test_start_attempt_not_active(db):
    data = _setup_exam(db, start_time=_future(1), end_time=_future(2))
    with pytest.raises(SmartGraderError, match="not active"):
        start_attempt(data["session"].id, data["student"].id)


def test_save_answer(db):
    data = _setup_exam(db)
    start_attempt(data["session"].id, data["student"].id)
    answer = save_answer(data["session"].id, data["student"].id, data["q1"].id, data["c1a"].id)
    assert answer.selected_choice_id == data["c1a"].id


def test_save_answer_upsert(db):
    data = _setup_exam(db)
    start_attempt(data["session"].id, data["student"].id)
    save_answer(data["session"].id, data["student"].id, data["q1"].id, data["c1a"].id)
    answer = save_answer(data["session"].id, data["student"].id, data["q1"].id, data["c1b"].id)
    assert answer.selected_choice_id == data["c1b"].id


def test_save_answers_batch(db):
    data = _setup_exam(db)
    start_attempt(data["session"].id, data["student"].id)
    count = save_answers_batch(data["session"].id, data["student"].id, [
        {"question_id": data["q1"].id, "choice_id": data["c1a"].id},
        {"question_id": data["q2"].id, "choice_id": data["c2b"].id},
    ])
    assert count == 2


def test_submit_attempt_perfect_score(db):
    data = _setup_exam(db)
    start_attempt(data["session"].id, data["student"].id)
    save_answer(data["session"].id, data["student"].id, data["q1"].id, data["c1a"].id)
    save_answer(data["session"].id, data["student"].id, data["q2"].id, data["c2b"].id)

    result = submit_attempt(data["session"].id, data["student"].id)
    assert result["score"] == 10
    assert result["percentage"] == 100.0


def test_submit_attempt_partial_score(db):
    data = _setup_exam(db)
    start_attempt(data["session"].id, data["student"].id)
    save_answer(data["session"].id, data["student"].id, data["q1"].id, data["c1a"].id)
    # q2 unanswered

    result = submit_attempt(data["session"].id, data["student"].id)
    assert result["score"] == 5
    assert result["percentage"] == 50.0


def test_submit_attempt_locks(db):
    data = _setup_exam(db)
    start_attempt(data["session"].id, data["student"].id)
    submit_attempt(data["session"].id, data["student"].id)

    with pytest.raises(SmartGraderError, match="already submitted"):
        submit_attempt(data["session"].id, data["student"].id)


def test_get_exam_status(db):
    data = _setup_exam(db)
    start_attempt(data["session"].id, data["student"].id)
    status = get_exam_status(data["session"].id, data["student"].id)
    assert status["remaining_seconds"] > 0
    assert status["status"] == "in_progress"
    assert status["answered_count"] == 0


def test_auto_submit_expired(db):
    data = _setup_exam(db, start_time=_past(2), end_time=_past(1))
    # Manually create an in-progress attempt for this ended session
    attempt = ExamAttempt(
        session_id=data["session"].id, student_id=data["student"].id,
        status="in_progress", started_at=_past(2),
    )
    db.session.add(attempt)
    db.session.commit()

    auto_submit_expired(data["session"].id)

    attempt = ExamAttempt.query.get(attempt.id)
    assert attempt.status == "auto_submitted"
    assert attempt.score is not None


def test_get_attempt_result_score_only(db):
    data = _setup_exam(db, show_result="score_only")
    start_attempt(data["session"].id, data["student"].id)
    save_answer(data["session"].id, data["student"].id, data["q1"].id, data["c1a"].id)
    submit_attempt(data["session"].id, data["student"].id)

    result = get_attempt_result(data["session"].id, data["student"].id)
    assert "score" in result
    assert "answers" not in result


def test_get_attempt_result_none(db):
    data = _setup_exam(db, show_result="none")
    start_attempt(data["session"].id, data["student"].id)
    submit_attempt(data["session"].id, data["student"].id)

    result = get_attempt_result(data["session"].id, data["student"].id)
    assert "score" not in result
    assert result["message"] == "Results are not available yet"


def test_get_attempt_result_with_answers(db):
    data = _setup_exam(db, show_result="score_and_answers")
    start_attempt(data["session"].id, data["student"].id)
    save_answer(data["session"].id, data["student"].id, data["q1"].id, data["c1a"].id)
    submit_attempt(data["session"].id, data["student"].id)

    result = get_attempt_result(data["session"].id, data["student"].id)
    assert "score" in result
    assert "answers" in result
    assert len(result["answers"]) == 2


def test_randomization_different_orders(db):
    data = _setup_exam(db, randomize=True)
    r1 = start_attempt(data["session"].id, data["student"].id)
    order1 = json.loads(ExamAttempt.query.first().question_order)

    # Create second student + assignment
    s2 = Student(name="B", matricule="002")
    db.session.add(s2)
    db.session.commit()
    db.session.add(ExamAssignment(session_id=data["session"].id, student_id=s2.id, assigned_via="individual"))
    db.session.commit()

    r2 = start_attempt(data["session"].id, s2.id)
    order2 = json.loads(ExamAttempt.query.filter_by(student_id=s2.id).first().question_order)

    # Both should have valid question IDs (order may or may not differ with only 2 questions)
    assert set(order1["questions"]) == set(order2["questions"])
```

- [ ] **Step 2: Create the service**

Create `app/services/exam_take_service.py`:

```python
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
```

- [ ] **Step 3: Run tests, full suite, commit**

Run: `pytest tests/test_services/test_exam_take_service.py -v`
Then: `pytest tests/ -v --tb=short`

```bash
git add app/services/exam_take_service.py tests/test_services/test_exam_take_service.py
git commit -m "feat(exam): add exam take service with start, answer, submit, grade, auto-submit"
```

---

## Task 7: Group Routes

**Files:**
- Create: `app/routes/groups.py`
- Modify: `app/routes/__init__.py`
- Create: `tests/test_routes/test_groups.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_routes/test_groups.py`:

```python
"""Tests for group API routes."""

import json
from app.models.student import Student


def test_create_group(auth_client, db):
    response = auth_client.post(
        "/api/groups",
        data=json.dumps({"name": "CS Year 3"}),
        content_type="application/json",
    )
    assert response.status_code == 201
    assert json.loads(response.data)["name"] == "CS Year 3"


def test_list_groups(auth_client, db):
    auth_client.post("/api/groups", data=json.dumps({"name": "G1"}), content_type="application/json")
    response = auth_client.get("/api/groups")
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1


def test_get_group(auth_client, db):
    resp = auth_client.post("/api/groups", data=json.dumps({"name": "G1"}), content_type="application/json")
    gid = json.loads(resp.data)["id"]
    response = auth_client.get(f"/api/groups/{gid}")
    assert response.status_code == 200
    assert json.loads(response.data)["name"] == "G1"


def test_delete_group(auth_client, db):
    resp = auth_client.post("/api/groups", data=json.dumps({"name": "Del"}), content_type="application/json")
    gid = json.loads(resp.data)["id"]
    response = auth_client.delete(f"/api/groups/{gid}")
    assert response.status_code == 200


def test_add_members(auth_client, db):
    resp = auth_client.post("/api/groups", data=json.dumps({"name": "G1"}), content_type="application/json")
    gid = json.loads(resp.data)["id"]

    s = Student(name="Ali", matricule="001")
    db.session.add(s)
    db.session.commit()

    response = auth_client.post(
        f"/api/groups/{gid}/members",
        data=json.dumps({"student_ids": [s.id]}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert json.loads(response.data)["added"] == 1


def test_remove_member(auth_client, db):
    resp = auth_client.post("/api/groups", data=json.dumps({"name": "G1"}), content_type="application/json")
    gid = json.loads(resp.data)["id"]

    s = Student(name="Ali", matricule="001")
    db.session.add(s)
    db.session.commit()

    auth_client.post(f"/api/groups/{gid}/members", data=json.dumps({"student_ids": [s.id]}), content_type="application/json")
    response = auth_client.delete(f"/api/groups/{gid}/members/{s.id}")
    assert response.status_code == 200


def test_groups_unauthenticated(client):
    response = client.get("/api/groups")
    assert response.status_code == 401
```

- [ ] **Step 2: Create the route**

Create `app/routes/groups.py`:

```python
"""Student group API endpoints."""

import logging
from flask import Blueprint, request, jsonify
from app.auth import require_auth, require_role
from app.services.group_service import (
    create_group, get_all_groups, get_group_by_id,
    delete_group, add_members, remove_member,
)

logger = logging.getLogger("smartgrader.routes.groups")
groups_bp = Blueprint("groups", __name__)


@groups_bp.route("/groups", methods=["POST"])
@require_auth
@require_role("teacher")
def create():
    data = request.get_json()
    group = create_group(name=data["name"])
    return jsonify(group.to_dict()), 201


@groups_bp.route("/groups", methods=["GET"])
@require_auth
@require_role("teacher")
def list_all():
    groups = get_all_groups()
    return jsonify([g.to_dict() for g in groups])


@groups_bp.route("/groups/<int:group_id>", methods=["GET"])
@require_auth
@require_role("teacher")
def get_one(group_id):
    group = get_group_by_id(group_id)
    return jsonify(group.to_dict(include_members=True))


@groups_bp.route("/groups/<int:group_id>", methods=["DELETE"])
@require_auth
@require_role("teacher")
def delete(group_id):
    delete_group(group_id)
    return jsonify({"message": "Group deleted"})


@groups_bp.route("/groups/<int:group_id>/members", methods=["POST"])
@require_auth
@require_role("teacher")
def add(group_id):
    data = request.get_json()
    count = add_members(group_id, data["student_ids"])
    return jsonify({"added": count})


@groups_bp.route("/groups/<int:group_id>/members/<int:student_id>", methods=["DELETE"])
@require_auth
@require_role("teacher")
def remove(group_id, student_id):
    remove_member(group_id, student_id)
    return jsonify({"message": "Member removed"})
```

- [ ] **Step 3: Register blueprint**

Add to `app/routes/__init__.py` inside `register_blueprints`:

```python
    from app.routes.groups import groups_bp
    app.register_blueprint(groups_bp, url_prefix="/api")
```

- [ ] **Step 4: Run tests, full suite, commit**

Run: `pytest tests/test_routes/test_groups.py -v`
Then: `pytest tests/ -v --tb=short`

```bash
git add app/routes/groups.py app/routes/__init__.py tests/test_routes/test_groups.py
git commit -m "feat(exam): add group routes — CRUD and member management"
```

---

## Task 8: Session Routes

**Files:**
- Create: `app/routes/sessions.py`
- Modify: `app/routes/__init__.py`
- Create: `tests/test_routes/test_sessions.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_routes/test_sessions.py`:

```python
"""Tests for session API routes."""

import json
from datetime import datetime, timezone, timedelta
from app.models.exam import Exam
from app.models.student import Student


def _future(hours=1):
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _make_exam(db):
    exam = Exam(title="Math", subject="S", total_marks=100)
    db.session.add(exam)
    db.session.commit()
    return exam


def test_create_session(auth_client, db):
    exam = _make_exam(db)
    response = auth_client.post(
        "/api/sessions",
        data=json.dumps({
            "exam_id": exam.id,
            "start_time": _future(1),
            "end_time": _future(2),
            "display_mode": "one_by_one",
            "save_mode": "auto_each",
            "show_result": "score_only",
        }),
        content_type="application/json",
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["exam_id"] == exam.id
    assert data["status"] == "scheduled"


def test_list_sessions(auth_client, db):
    exam = _make_exam(db)
    auth_client.post("/api/sessions", data=json.dumps({
        "exam_id": exam.id, "start_time": _future(1), "end_time": _future(2),
        "display_mode": "one_by_one", "save_mode": "auto_each", "show_result": "none",
    }), content_type="application/json")
    response = auth_client.get("/api/sessions")
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1


def test_assign_students(auth_client, db):
    exam = _make_exam(db)
    resp = auth_client.post("/api/sessions", data=json.dumps({
        "exam_id": exam.id, "start_time": _future(1), "end_time": _future(2),
        "display_mode": "one_by_one", "save_mode": "auto_each", "show_result": "none",
    }), content_type="application/json")
    sid = json.loads(resp.data)["id"]

    s = Student(name="Ali", matricule="001")
    db.session.add(s)
    db.session.commit()

    response = auth_client.post(
        f"/api/sessions/{sid}/assign",
        data=json.dumps({"student_ids": [s.id], "group_ids": []}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert json.loads(response.data)["assigned"] == 1


def test_delete_session(auth_client, db):
    exam = _make_exam(db)
    resp = auth_client.post("/api/sessions", data=json.dumps({
        "exam_id": exam.id, "start_time": _future(1), "end_time": _future(2),
        "display_mode": "one_by_one", "save_mode": "auto_each", "show_result": "none",
    }), content_type="application/json")
    sid = json.loads(resp.data)["id"]

    response = auth_client.delete(f"/api/sessions/{sid}")
    assert response.status_code == 200


def test_sessions_unauthenticated(client):
    response = client.get("/api/sessions")
    assert response.status_code == 401
```

- [ ] **Step 2: Create the route**

Create `app/routes/sessions.py`:

```python
"""Exam session API endpoints."""

import logging
from flask import Blueprint, request, jsonify
from app.auth import require_auth, require_role
from app.services.session_service import (
    create_session, get_all_sessions, get_session_by_id,
    update_session, delete_session, assign_students,
    get_monitor_data, compute_session_status,
)

logger = logging.getLogger("smartgrader.routes.sessions")
sessions_bp = Blueprint("sessions", __name__)


@sessions_bp.route("/sessions", methods=["POST"])
@require_auth
@require_role("teacher")
def create():
    data = request.get_json()
    session = create_session(
        exam_id=data["exam_id"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        display_mode=data["display_mode"],
        save_mode=data["save_mode"],
        show_result=data["show_result"],
        randomize=data.get("randomize", False),
    )
    result = session.to_dict()
    result["status"] = compute_session_status(session)
    return jsonify(result), 201


@sessions_bp.route("/sessions", methods=["GET"])
@require_auth
@require_role("teacher")
def list_all():
    sessions = get_all_sessions()
    result = []
    for s in sessions:
        d = s.to_dict()
        d["status"] = compute_session_status(s)
        result.append(d)
    return jsonify(result)


@sessions_bp.route("/sessions/<int:session_id>", methods=["GET"])
@require_auth
@require_role("teacher")
def get_one(session_id):
    session = get_session_by_id(session_id)
    result = session.to_dict()
    result["status"] = compute_session_status(session)
    return jsonify(result)


@sessions_bp.route("/sessions/<int:session_id>", methods=["PUT"])
@require_auth
@require_role("teacher")
def update(session_id):
    data = request.get_json()
    session = update_session(session_id, **data)
    result = session.to_dict()
    result["status"] = compute_session_status(session)
    return jsonify(result)


@sessions_bp.route("/sessions/<int:session_id>", methods=["DELETE"])
@require_auth
@require_role("teacher")
def delete(session_id):
    delete_session(session_id)
    return jsonify({"message": "Session deleted"})


@sessions_bp.route("/sessions/<int:session_id>/assign", methods=["POST"])
@require_auth
@require_role("teacher")
def assign(session_id):
    data = request.get_json()
    count = assign_students(
        session_id,
        student_ids=data.get("student_ids", []),
        group_ids=data.get("group_ids", []),
    )
    return jsonify({"assigned": count})


@sessions_bp.route("/sessions/<int:session_id>/monitor", methods=["GET"])
@require_auth
@require_role("teacher")
def monitor(session_id):
    data = get_monitor_data(session_id)
    return jsonify(data)
```

- [ ] **Step 3: Register blueprint**

Add to `app/routes/__init__.py`:

```python
    from app.routes.sessions import sessions_bp
    app.register_blueprint(sessions_bp, url_prefix="/api")
```

- [ ] **Step 4: Run tests, full suite, commit**

Run: `pytest tests/test_routes/test_sessions.py -v`
Then: `pytest tests/ -v --tb=short`

```bash
git add app/routes/sessions.py app/routes/__init__.py tests/test_routes/test_sessions.py
git commit -m "feat(exam): add session routes — CRUD, assign, monitor"
```

---

## Task 9: Student Exam Routes + Student Test Fixture

**Files:**
- Modify: `tests/conftest.py`
- Create: `app/routes/student_exam.py`
- Modify: `app/routes/__init__.py`
- Create: `tests/test_routes/test_student_exam.py`

- [ ] **Step 1: Add student_client fixture to conftest.py**

Add to `tests/conftest.py`:

```python
from app.models.student import Student
from app.models.user import User


@pytest.fixture
def student_client(client, db):
    """Provide an authenticated test client (student role)."""
    student = Student(name="Test Student", matricule="TEST001")
    db.session.add(student)
    db.session.commit()
    user = User(role="student", student_id=student.id)
    db.session.add(user)
    db.session.commit()
    client.post(
        "/api/auth/scan",
        data=json.dumps({"matricule": "TEST001"}),
        content_type="application/json",
    )
    return client, student
```

- [ ] **Step 2: Write failing tests**

Create `tests/test_routes/test_student_exam.py`:

```python
"""Tests for student exam API routes."""

import json
from datetime import datetime, timezone, timedelta
from app.models.exam import Exam, Question, Choice
from app.models.exam_session import ExamSession, ExamAssignment
from app.models import db as _db


def _past(hours=1):
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()


def _future(hours=1):
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _setup(db, student):
    exam = Exam(title="Test", subject="S", total_marks=10)
    db.session.add(exam)
    db.session.commit()

    q = Question(exam_id=exam.id, question_text="Q1", question_choices_number=2, marks=10)
    db.session.add(q)
    db.session.commit()

    c1 = Choice(question_id=q.id, choice_label="A", choice_text="Right", is_correct=1)
    c2 = Choice(question_id=q.id, choice_label="B", choice_text="Wrong", is_correct=0)
    db.session.add_all([c1, c2])
    db.session.commit()

    session = ExamSession(
        exam_id=exam.id,
        start_time=_past(1), end_time=_future(1),
        display_mode="one_by_one", save_mode="auto_each",
        show_result="score_only",
    )
    db.session.add(session)
    db.session.commit()

    db.session.add(ExamAssignment(session_id=session.id, student_id=student.id, assigned_via="individual"))
    db.session.commit()

    return session, q, c1, c2


def test_list_student_exams(student_client, db):
    client, student = student_client
    _setup(db, student)
    response = client.get("/api/student/exams")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["active"]) == 1


def test_start_exam(student_client, db):
    client, student = student_client
    session, q, c1, c2 = _setup(db, student)
    response = client.post(f"/api/student/exams/{session.id}/start")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["attempt_id"] is not None
    assert len(data["questions"]) == 1


def test_save_answer(student_client, db):
    client, student = student_client
    session, q, c1, c2 = _setup(db, student)
    client.post(f"/api/student/exams/{session.id}/start")
    response = client.post(
        f"/api/student/exams/{session.id}/answer",
        data=json.dumps({"question_id": q.id, "choice_id": c1.id}),
        content_type="application/json",
    )
    assert response.status_code == 200


def test_submit_exam(student_client, db):
    client, student = student_client
    session, q, c1, c2 = _setup(db, student)
    client.post(f"/api/student/exams/{session.id}/start")
    client.post(
        f"/api/student/exams/{session.id}/answer",
        data=json.dumps({"question_id": q.id, "choice_id": c1.id}),
        content_type="application/json",
    )
    response = client.post(f"/api/student/exams/{session.id}/submit")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["score"] == 10


def test_get_result(student_client, db):
    client, student = student_client
    session, q, c1, c2 = _setup(db, student)
    client.post(f"/api/student/exams/{session.id}/start")
    client.post(f"/api/student/exams/{session.id}/submit")
    response = client.get(f"/api/student/exams/{session.id}/result")
    assert response.status_code == 200


def test_student_exams_unauthenticated(client):
    response = client.get("/api/student/exams")
    assert response.status_code == 401


def test_teacher_cannot_access_student_routes(auth_client, db):
    response = auth_client.get("/api/student/exams")
    assert response.status_code == 403
```

- [ ] **Step 3: Create the route**

Create `app/routes/student_exam.py`:

```python
"""Student exam-taking API endpoints."""

import logging
from flask import Blueprint, request, jsonify, g
from app.auth import require_auth, require_role
from app.services.exam_take_service import (
    get_student_exams, start_attempt, save_answer, save_answers_batch,
    submit_attempt, get_exam_status, get_attempt_result,
)

logger = logging.getLogger("smartgrader.routes.student_exam")
student_exam_bp = Blueprint("student_exam", __name__)


@student_exam_bp.route("/student/exams", methods=["GET"])
@require_auth
@require_role("student")
def list_exams():
    student_id = g.current_user.student_id
    exams = get_student_exams(student_id)
    return jsonify(exams)


@student_exam_bp.route("/student/exams/<int:session_id>/start", methods=["POST"])
@require_auth
@require_role("student")
def start(session_id):
    student_id = g.current_user.student_id
    result = start_attempt(session_id, student_id)
    return jsonify(result)


@student_exam_bp.route("/student/exams/<int:session_id>/status", methods=["GET"])
@require_auth
@require_role("student")
def status(session_id):
    student_id = g.current_user.student_id
    result = get_exam_status(session_id, student_id)
    return jsonify(result)


@student_exam_bp.route("/student/exams/<int:session_id>/answer", methods=["POST"])
@require_auth
@require_role("student")
def answer_one(session_id):
    student_id = g.current_user.student_id
    data = request.get_json()
    save_answer(session_id, student_id, data["question_id"], data["choice_id"])
    return jsonify({"message": "Answer saved"})


@student_exam_bp.route("/student/exams/<int:session_id>/answers", methods=["POST"])
@require_auth
@require_role("student")
def answer_batch(session_id):
    student_id = g.current_user.student_id
    data = request.get_json()
    count = save_answers_batch(session_id, student_id, data["answers"])
    return jsonify({"saved": count})


@student_exam_bp.route("/student/exams/<int:session_id>/submit", methods=["POST"])
@require_auth
@require_role("student")
def submit(session_id):
    student_id = g.current_user.student_id
    result = submit_attempt(session_id, student_id)
    return jsonify(result)


@student_exam_bp.route("/student/exams/<int:session_id>/result", methods=["GET"])
@require_auth
@require_role("student")
def result(session_id):
    student_id = g.current_user.student_id
    result = get_attempt_result(session_id, student_id)
    return jsonify(result)
```

- [ ] **Step 4: Register blueprint**

Add to `app/routes/__init__.py`:

```python
    from app.routes.student_exam import student_exam_bp
    app.register_blueprint(student_exam_bp, url_prefix="/api")
```

- [ ] **Step 5: Run tests, full suite, commit**

Run: `pytest tests/test_routes/test_student_exam.py -v`
Then: `pytest tests/ -v --tb=short`

```bash
git add app/routes/student_exam.py app/routes/__init__.py tests/conftest.py tests/test_routes/test_student_exam.py
git commit -m "feat(exam): add student exam routes — start, answer, submit, result"
```

---

## Task 10: Database Migration

- [ ] **Step 1: Generate migration**

Run: `flask db migrate -m "add online exam models"`

- [ ] **Step 2: Apply migration**

Run: `flask db upgrade`

- [ ] **Step 3: Commit**

```bash
git add migrations/
git commit -m "feat(exam): add database migration for online exam models"
```

---

## Task 11: Frontend — React Query Hooks

**Files:**
- Create: `frontend/src/hooks/use-groups.js`
- Create: `frontend/src/hooks/use-sessions.js`
- Create: `frontend/src/hooks/use-student-exam.js`

- [ ] **Step 1: Create use-groups.js**

```javascript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAPI } from "@/lib/api";

export function useGroups() {
  return useQuery({ queryKey: ["groups"], queryFn: () => fetchAPI("/groups") });
}

export function useGroup(id) {
  return useQuery({
    queryKey: ["groups", id],
    queryFn: () => fetchAPI(`/groups/${id}`),
    enabled: !!id,
  });
}

export function useCreateGroup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => fetchAPI("/groups", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["groups"] }),
  });
}

export function useDeleteGroup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => fetchAPI(`/groups/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["groups"] }),
  });
}

export function useAddMembers() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ groupId, studentIds }) =>
      fetchAPI(`/groups/${groupId}/members`, { method: "POST", body: JSON.stringify({ student_ids: studentIds }) }),
    onSuccess: (_, { groupId }) => qc.invalidateQueries({ queryKey: ["groups", groupId] }),
  });
}

export function useRemoveMember() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ groupId, studentId }) =>
      fetchAPI(`/groups/${groupId}/members/${studentId}`, { method: "DELETE" }),
    onSuccess: (_, { groupId }) => qc.invalidateQueries({ queryKey: ["groups", groupId] }),
  });
}
```

- [ ] **Step 2: Create use-sessions.js**

```javascript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAPI } from "@/lib/api";

export function useSessions() {
  return useQuery({ queryKey: ["sessions"], queryFn: () => fetchAPI("/sessions") });
}

export function useSession(id) {
  return useQuery({
    queryKey: ["sessions", id],
    queryFn: () => fetchAPI(`/sessions/${id}`),
    enabled: !!id,
  });
}

export function useCreateSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => fetchAPI("/sessions", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["sessions"] }),
  });
}

export function useUpdateSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }) => fetchAPI(`/sessions/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["sessions"] }),
  });
}

export function useDeleteSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => fetchAPI(`/sessions/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["sessions"] }),
  });
}

export function useAssignStudents() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ sessionId, studentIds, groupIds }) =>
      fetchAPI(`/sessions/${sessionId}/assign`, {
        method: "POST",
        body: JSON.stringify({ student_ids: studentIds, group_ids: groupIds }),
      }),
    onSuccess: (_, { sessionId }) => qc.invalidateQueries({ queryKey: ["sessions", sessionId] }),
  });
}

export function useMonitorSession(sessionId, enabled = true) {
  return useQuery({
    queryKey: ["sessions", sessionId, "monitor"],
    queryFn: () => fetchAPI(`/sessions/${sessionId}/monitor`),
    enabled: !!sessionId && enabled,
    refetchInterval: 10000,
  });
}
```

- [ ] **Step 3: Create use-student-exam.js**

```javascript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAPI } from "@/lib/api";

export function useStudentExams() {
  return useQuery({ queryKey: ["student-exams"], queryFn: () => fetchAPI("/student/exams") });
}

export function useStartAttempt() {
  return useMutation({
    mutationFn: (sessionId) => fetchAPI(`/student/exams/${sessionId}/start`, { method: "POST" }),
  });
}

export function useExamStatus(sessionId, enabled = true) {
  return useQuery({
    queryKey: ["student-exams", sessionId, "status"],
    queryFn: () => fetchAPI(`/student/exams/${sessionId}/status`),
    enabled: !!sessionId && enabled,
    refetchInterval: 30000,
  });
}

export function useSaveAnswer() {
  return useMutation({
    mutationFn: ({ sessionId, questionId, choiceId }) =>
      fetchAPI(`/student/exams/${sessionId}/answer`, {
        method: "POST",
        body: JSON.stringify({ question_id: questionId, choice_id: choiceId }),
      }),
  });
}

export function useSaveAnswersBatch() {
  return useMutation({
    mutationFn: ({ sessionId, answers }) =>
      fetchAPI(`/student/exams/${sessionId}/answers`, {
        method: "POST",
        body: JSON.stringify({ answers }),
      }),
  });
}

export function useSubmitExam() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (sessionId) => fetchAPI(`/student/exams/${sessionId}/submit`, { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["student-exams"] }),
  });
}

export function useExamResult(sessionId) {
  return useQuery({
    queryKey: ["student-exams", sessionId, "result"],
    queryFn: () => fetchAPI(`/student/exams/${sessionId}/result`),
    enabled: !!sessionId,
  });
}
```

- [ ] **Step 4: Commit**

```bash
cd frontend && git add src/hooks/use-groups.js src/hooks/use-sessions.js src/hooks/use-student-exam.js
git commit -m "feat(exam): add React Query hooks for groups, sessions, student exam"
```

---

## Task 12: Frontend — Teacher Pages (Groups, Sessions, CreateSession, SessionDetail)

**Files:**
- Create: `frontend/src/pages/StudentGroups.jsx`
- Create: `frontend/src/pages/ExamSessions.jsx`
- Create: `frontend/src/pages/CreateSession.jsx`
- Create: `frontend/src/pages/SessionDetail.jsx`

This task creates all 4 teacher management pages. Each page follows existing patterns (React Query hooks, Tailwind classes, form state). Due to plan length constraints, the implementer should:

- [ ] **Step 1: Create StudentGroups.jsx** — list groups, create group form, click group to see members, add/remove members. Use `useGroups`, `useGroup`, `useCreateGroup`, `useDeleteGroup`, `useAddMembers`, `useRemoveMember` hooks. Follow existing page patterns (TeacherManagement.jsx is a good reference).

- [ ] **Step 2: Create ExamSessions.jsx** — list sessions with status badges (scheduled=blue, active=green, ended=gray), "New Session" button links to `/sessions/new`. Use `useSessions`. Follow existing list page patterns.

- [ ] **Step 3: Create CreateSession.jsx** — form with: exam selector (dropdown from `useExams`), start/end datetime inputs, display_mode toggle, save_mode selector, randomize checkbox, show_result selector, student/group assignment (multi-select from `useStudents` and `useGroups`). Submit calls `useCreateSession` then `useAssignStudents`, navigates to `/sessions/:id`. 

- [ ] **Step 4: Create SessionDetail.jsx** — show session info, settings, and live monitor table. Use `useSession` and `useMonitorSession`. Monitor table columns: Student Name, Matricule, Status (badge), Answers, Score. Auto-refreshes every 10s when session is active. Summary stats at top (total/started/submitted).

- [ ] **Step 5: Verify frontend builds**

Run: `cd frontend && npm run build`

- [ ] **Step 6: Commit**

```bash
cd frontend && git add src/pages/StudentGroups.jsx src/pages/ExamSessions.jsx src/pages/CreateSession.jsx src/pages/SessionDetail.jsx
git commit -m "feat(exam): add teacher pages — groups, sessions, create session, monitor"
```

---

## Task 13: Frontend — Student Pages (StudentLayout, Dashboard, TakeExam, ExamResult)

**Files:**
- Create: `frontend/src/components/layout/StudentLayout.jsx`
- Create: `frontend/src/pages/StudentDashboard.jsx`
- Create: `frontend/src/pages/TakeExam.jsx`
- Create: `frontend/src/pages/ExamResult.jsx`

- [ ] **Step 1: Create StudentLayout.jsx** — minimal layout: top bar with student name + logout button, no sidebar. Wraps student routes with `<Outlet />`.

```jsx
import { Outlet } from "react-router-dom";
import { useAuth } from "@/hooks/use-auth";
import { useNavigate } from "react-router-dom";
import { LogOut } from "lucide-react";

export default function StudentLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-40 h-16 border-b border-border bg-background/80 backdrop-blur-sm flex items-center justify-between px-6">
        <span className="font-semibold">SmartGrader</span>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">{user?.name}</span>
          <button onClick={handleLogout} className="rounded-lg p-2 text-muted-foreground hover:bg-accent transition-colors" title="Sign out">
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </header>
      <main className="p-6">
        <Outlet />
      </main>
    </div>
  );
}
```

- [ ] **Step 2: Create StudentDashboard.jsx** — shows upcoming, active, completed exam cards. Use `useStudentExams`. Active exams show "Start" or "Resume" button. Completed show score if available.

- [ ] **Step 3: Create TakeExam.jsx** — the core exam-taking component. This is the most complex page:
  - Calls `useStartAttempt` on mount to get questions
  - Countdown timer (using `remaining_seconds` from start, decremented locally, synced with `useExamStatus` every 30s)
  - Question navigator strip (numbered squares: green=answered, blue=current, gray=unanswered)
  - Two display modes based on `display_mode`:
    - `all_at_once`: scrollable page with all questions
    - `one_by_one`: single question with prev/next
  - Answer saving based on `save_mode`:
    - `auto_each`: call `useSaveAnswer` on every selection
    - `auto_periodic`: buffer locally, flush via `useSaveAnswersBatch` every 30s
    - `manual`: buffer locally, "Save" button calls `useSaveAnswersBatch`
  - Submit button with confirmation dialog
  - Auto-submit when timer reaches 0 (call `useSubmitExam`)
  - Navigate to `/exam/:sessionId/result` after submit

- [ ] **Step 4: Create ExamResult.jsx** — shows result using `useExamResult`. Handles three show_result modes:
  - `none`: "Results will be available later"
  - `score_only`: score and percentage
  - `score_and_answers`: score + per-question breakdown (correct/incorrect with indicators)

- [ ] **Step 5: Verify frontend builds**

Run: `cd frontend && npm run build`

- [ ] **Step 6: Commit**

```bash
cd frontend && git add src/components/layout/StudentLayout.jsx src/pages/StudentDashboard.jsx src/pages/TakeExam.jsx src/pages/ExamResult.jsx
git commit -m "feat(exam): add student pages — dashboard, take exam, result"
```

---

## Task 14: Frontend — Update App.jsx and Sidebar

**Files:**
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/components/layout/Sidebar.jsx`

- [ ] **Step 1: Update App.jsx**

Add imports and routes for the new pages:

```jsx
import { Routes, Route } from "react-router-dom";
import AppLayout from "@/components/layout/AppLayout";
import StudentLayout from "@/components/layout/StudentLayout";
import ProtectedRoute from "@/components/ProtectedRoute";
import LoginPage from "@/pages/LoginPage";
import Dashboard from "@/pages/Dashboard";
import Exams from "@/pages/Exams";
import ExamDetail from "@/pages/ExamDetail";
import Scanner from "@/pages/Scanner";
import Students from "@/pages/Students";
import Results from "@/pages/Results";
import Settings from "@/pages/Settings";
import Documentation from "@/pages/Documentation";
import AcademicDocs from "@/pages/AcademicDocs";
import AIConfig from "@/pages/AIConfig";
import SampleData from "@/pages/SampleData";
import LegacyCode from "@/pages/LegacyCode";
import Help from "@/pages/Help";
import TeacherManagement from "@/pages/TeacherManagement";
import StudentImport from "@/pages/StudentImport";
import StudentGroups from "@/pages/StudentGroups";
import ExamSessions from "@/pages/ExamSessions";
import CreateSession from "@/pages/CreateSession";
import SessionDetail from "@/pages/SessionDetail";
import StudentDashboard from "@/pages/StudentDashboard";
import TakeExam from "@/pages/TakeExam";
import ExamResult from "@/pages/ExamResult";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      {/* Teacher routes */}
      <Route element={<ProtectedRoute role="teacher" />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/exams" element={<Exams />} />
          <Route path="/exams/:id" element={<ExamDetail />} />
          <Route path="/scanner" element={<Scanner />} />
          <Route path="/students" element={<Students />} />
          <Route path="/results" element={<Results />} />
          <Route path="/groups" element={<StudentGroups />} />
          <Route path="/sessions" element={<ExamSessions />} />
          <Route path="/sessions/new" element={<CreateSession />} />
          <Route path="/sessions/:id" element={<SessionDetail />} />
          <Route path="/documentation" element={<Documentation />} />
          <Route path="/academic-docs" element={<AcademicDocs />} />
          <Route path="/samples" element={<SampleData />} />
          <Route path="/legacy" element={<LegacyCode />} />
          <Route path="/ai-config" element={<AIConfig />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/help" element={<Help />} />
        </Route>
      </Route>

      {/* Admin routes */}
      <Route element={<ProtectedRoute role="teacher" requireAdmin />}>
        <Route element={<AppLayout />}>
          <Route path="/admin/teachers" element={<TeacherManagement />} />
          <Route path="/admin/import" element={<StudentImport />} />
        </Route>
      </Route>

      {/* Student routes */}
      <Route element={<ProtectedRoute role="student" />}>
        <Route element={<StudentLayout />}>
          <Route path="/exam" element={<StudentDashboard />} />
          <Route path="/exam/:sessionId" element={<TakeExam />} />
          <Route path="/exam/:sessionId/result" element={<ExamResult />} />
        </Route>
      </Route>
    </Routes>
  );
}
```

- [ ] **Step 2: Update Sidebar.jsx**

Add `Monitor` to the lucide-react import:

```javascript
import { ..., Monitor } from "lucide-react";
```

Add two items to the "Main" group in `navGroups`:

```javascript
{ icon: Users,   label: "Groups",       to: "/groups" },
{ icon: Monitor, label: "Online Exams", to: "/sessions" },
```

Note: `Users` is already imported. Add these after the "Results" item in the Main group.

- [ ] **Step 3: Verify build**

Run: `cd frontend && npm run build`

- [ ] **Step 4: Commit**

```bash
cd frontend && git add src/App.jsx src/components/layout/Sidebar.jsx
git commit -m "feat(exam): update routing and sidebar for online exam pages"
```

---

## Task 15: End-to-End Verification

- [ ] **Step 1: Run full backend test suite**

Run: `pytest tests/ -v --tb=short`
Expected: all tests pass

- [ ] **Step 2: Run frontend build**

Run: `cd frontend && npm run build`
Expected: build succeeds

- [ ] **Step 3: Manual smoke test**

Start the app:
```bash
python run.py
cd frontend && npm run dev
```

Test flows:
1. Login as admin teacher
2. Create a student group at `/groups`, add students
3. Create an exam session at `/sessions/new` — pick exam, set times, assign group
4. Monitor at `/sessions/:id` — see assigned students
5. Login as student (barcode scan)
6. See assigned exam at `/exam`
7. Start exam — verify questions appear, timer works
8. Answer questions, submit — verify score
9. Check teacher monitor shows submitted status

- [ ] **Step 4: Final commit if fixes needed**

```bash
git add -A
git commit -m "fix(exam): address issues found during smoke testing"
```

---

## Summary

| Task | Description | Tests |
|------|-------------|-------|
| 1 | StudentGroup + StudentGroupMember models | 4 |
| 2 | ExamSession + ExamAssignment models | 4 |
| 3 | ExamAttempt + OnlineAnswer models | 3 |
| 4 | Group service | 8 |
| 5 | Session service | 12 |
| 6 | Exam take service | 17 |
| 7 | Group routes | 7 |
| 8 | Session routes | 5 |
| 9 | Student exam routes + fixture | 7 |
| 10 | Database migration | - |
| 11 | Frontend hooks | - |
| 12 | Teacher pages | - |
| 13 | Student pages | - |
| 14 | App.jsx + Sidebar | - |
| 15 | E2E verification | manual |

**Total: 15 tasks, ~67 automated tests, 15 commits**
