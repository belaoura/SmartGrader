# Phase 2: Online Exam Engine — Design Spec

## Overview

Add an online exam-taking system so students can take MCQ exams digitally through the browser. Teachers schedule exam sessions with configurable settings (display mode, save strategy, randomization, result visibility), assign students individually or via groups, and monitor live progress. Students see assigned exams, take them with a countdown timer, and get results based on teacher settings.

## Goals

- Student groups for class-based assignment
- Exam sessions with scheduled time windows (start_time → end_time)
- Teacher-configurable settings: display mode, save mode, randomization, result visibility
- Student exam-taking UI with countdown timer, question navigator, answer persistence
- Auto-submit on timer expiry (client-side primary, server-side fallback)
- Teacher monitoring dashboard (live student progress)
- Resume on reconnect (answers persisted server-side)
- Zero new dependencies — uses existing Flask + SQLAlchemy + React + React Query

## Non-Goals (deferred to later phases)

- Anti-cheat / proctoring (Phase 3)
- WebSocket / real-time push (Phase 4)
- Written/essay question support
- Multiple exam attempts per student
- Exam analytics / statistics dashboard

---

## 1. Data Model

### New Model: StudentGroup

| Column | Type | Notes |
|--------|------|-------|
| id | Integer, PK | Auto-increment |
| name | String(200), NOT NULL | e.g., "CS Year 3 Group A" |
| created_at | String(30) | ISO timestamp |

File: `app/models/group.py`

### New Model: StudentGroupMember (join table)

| Column | Type | Notes |
|--------|------|-------|
| id | Integer, PK | |
| group_id | Integer, FK → student_groups | |
| student_id | Integer, FK → students | Unique per group |

File: `app/models/group.py`

### New Model: ExamSession

| Column | Type | Notes |
|--------|------|-------|
| id | Integer, PK | |
| exam_id | Integer, FK → exams | Which exam (questions come from here) |
| start_time | String(30), NOT NULL | ISO datetime — when exam opens |
| end_time | String(30), NOT NULL | ISO datetime — when exam closes + auto-submit |
| display_mode | String(20), NOT NULL | "all_at_once" or "one_by_one" |
| save_mode | String(20), NOT NULL | "auto_each", "auto_periodic", or "manual" |
| randomize | Boolean, default False | Shuffle questions + choices per student |
| show_result | String(20), NOT NULL | "none", "score_only", or "score_and_answers" |
| created_at | String(30) | ISO timestamp |

Status is computed at query time from current time vs start_time/end_time — not stored in the database. This avoids stale status values.

File: `app/models/exam_session.py`

### New Model: ExamAssignment

| Column | Type | Notes |
|--------|------|-------|
| id | Integer, PK | |
| session_id | Integer, FK → exam_sessions | |
| student_id | Integer, FK → students | Unique per session |
| assigned_via | String(20) | "individual" or "group" |

File: `app/models/exam_session.py`

### New Model: ExamAttempt

| Column | Type | Notes |
|--------|------|-------|
| id | Integer, PK | |
| session_id | Integer, FK → exam_sessions | |
| student_id | Integer, FK → students | Unique per session |
| status | String(20), NOT NULL | "in_progress", "submitted", "auto_submitted" |
| started_at | String(30) | When student opened the exam |
| submitted_at | String(30), nullable | When submitted (or auto-submitted) |
| question_order | Text, nullable | JSON array of question IDs (randomized order) |
| score | Float, nullable | Computed on submission |
| percentage | Float, nullable | Computed on submission |

File: `app/models/exam_attempt.py`

### New Model: OnlineAnswer

| Column | Type | Notes |
|--------|------|-------|
| id | Integer, PK | |
| attempt_id | Integer, FK → exam_attempts | |
| question_id | Integer, FK → questions | |
| selected_choice_id | Integer, FK → choices, nullable | NULL if unanswered |
| answered_at | String(30) | Last updated timestamp |

Unique constraint on (attempt_id, question_id) — one answer per question per attempt.

File: `app/models/online_answer.py`

### Relationships

- Exam 1:N ExamSession (one exam can have multiple scheduled sessions)
- ExamSession 1:N ExamAssignment (each session has many assigned students)
- ExamSession 1:N ExamAttempt (each session has many attempts)
- ExamAttempt 1:N OnlineAnswer (each attempt has many answers)
- StudentGroup M:N Student (via StudentGroupMember)

### Existing Models — No Changes

Exam, Question, Choice, Student, User, Result, StudentAnswer, AICorrection — all remain untouched. Online answers are stored in OnlineAnswer (separate from StudentAnswer used by the OMR scanner flow).

---

## 2. API Endpoints

### Student Group Management (Teacher)

All require `@require_auth @require_role("teacher")`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/groups | Create a student group |
| GET | /api/groups | List all groups (with member count) |
| GET | /api/groups/\<id\> | Get group with full member list |
| DELETE | /api/groups/\<id\> | Delete group |
| POST | /api/groups/\<id\>/members | Add students to group (list of student IDs) |
| DELETE | /api/groups/\<id\>/members/\<student_id\> | Remove student from group |

Blueprint: `app/routes/groups.py` → `groups_bp` registered at `/api`

### Exam Session Management (Teacher)

All require `@require_auth @require_role("teacher")`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/sessions | Create exam session (exam_id, times, settings) |
| GET | /api/sessions | List all sessions (with computed status, student count) |
| GET | /api/sessions/\<id\> | Get session details + assignment list |
| PUT | /api/sessions/\<id\> | Update session (only if not yet started) |
| DELETE | /api/sessions/\<id\> | Delete session (only if not yet started) |
| POST | /api/sessions/\<id\>/assign | Assign students/groups {student_ids, group_ids} |
| GET | /api/sessions/\<id\>/monitor | Teacher monitoring: all attempts with status, progress |

Blueprint: `app/routes/sessions.py` → `sessions_bp` registered at `/api`

### Student Exam Endpoints

All require `@require_auth @require_role("student")`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/student/exams | List assigned exams (upcoming, active, completed) |
| POST | /api/student/exams/\<session_id\>/start | Start or resume attempt → returns questions |
| GET | /api/student/exams/\<session_id\>/status | Poll: remaining time, attempt status, answered count |
| POST | /api/student/exams/\<session_id\>/answer | Save one answer: {question_id, choice_id} |
| POST | /api/student/exams/\<session_id\>/answers | Save batch: [{question_id, choice_id}, ...] |
| POST | /api/student/exams/\<session_id\>/submit | Submit exam → grade, compute score, lock attempt |
| GET | /api/student/exams/\<session_id\>/result | Get result (respects show_result setting) |

Blueprint: `app/routes/student_exam.py` → `student_exam_bp` registered at `/api`

---

## 3. Session Status Computation

Status is computed dynamically from timestamps, not stored:

```
if now < start_time → "scheduled"
if start_time <= now <= end_time → "active"
if now > end_time → "ended"
```

This is implemented in `session_service.compute_session_status(session)` and included in all session responses.

---

## 4. Exam-Taking Flow

### Start Attempt

1. Student calls `POST /api/student/exams/:session_id/start`
2. Server validates: student is assigned, session is active, student is authenticated
3. If attempt already exists (resume): return existing attempt + saved answers
4. If new attempt: create ExamAttempt with status="in_progress", started_at=now
5. If randomize is enabled: generate shuffled question_order (random permutation of question IDs), store as JSON in ExamAttempt. Also shuffle choice order per question.
6. Return: questions (in order), choices (per question), attempt_id, remaining_seconds

### Save Answers

**auto_each mode:** Frontend calls `POST .../answer` immediately when student selects a choice. Single answer upsert.

**auto_periodic mode:** Frontend buffers answers locally, sends `POST .../answers` batch every 30 seconds. Also saves on page visibility change (tab switch).

**manual mode:** Frontend buffers locally, student clicks "Save" button to send `POST .../answers` batch. Warning shown if unsaved answers exist when navigating.

All save endpoints validate: attempt exists, attempt is in_progress, session has not ended.

### Submit

1. Student clicks "Submit" or timer expires (client-side auto-submit)
2. `POST /api/student/exams/:session_id/submit`
3. Server grades all OnlineAnswers: for each question, check if selected_choice has is_correct=1
4. Compute total score and percentage
5. Set attempt status="submitted", submitted_at=now, store score/percentage
6. Return result based on show_result setting

### Auto-Submit (Server-Side Fallback)

If a student disconnects and their client-side timer can't fire:

1. `auto_submit_expired(session_id)` is called lazily from:
   - `get_exam_status()` (student status poll)
   - `get_monitor_data()` (teacher monitor poll)
2. Finds all ExamAttempt records where session_id matches, status="in_progress", and session end_time has passed
3. For each: grades answers, sets status="auto_submitted", records submitted_at=end_time
4. No background scheduler needed

---

## 5. Randomization

When `randomize=True` on the ExamSession:

- On `start_attempt`: generate a random permutation of question IDs, store as JSON in `ExamAttempt.question_order`
- For each question, shuffle the choice order (stored as a JSON map in question_order: `{"questions": [3,1,4,2], "choices": {"1": [2,4,1,3], "2": [3,1,2,4]}}`)
- When returning questions to the student, use the stored order
- Each student gets a different order (random seed per attempt)
- Grading is unaffected — answers reference choice IDs, not positions

---

## 6. Backend Services

### group_service.py

| Function | Description |
|----------|-------------|
| `create_group(name)` | Create a StudentGroup |
| `get_all_groups()` | List groups with member count |
| `get_group_by_id(group_id)` | Get group + full member list |
| `delete_group(group_id)` | Delete group and memberships |
| `add_members(group_id, student_ids)` | Add students, skip existing members |
| `remove_member(group_id, student_id)` | Remove one student from group |

File: `app/services/group_service.py`

### session_service.py

| Function | Description |
|----------|-------------|
| `create_session(exam_id, start_time, end_time, **settings)` | Validate and create ExamSession |
| `get_all_sessions()` | List all sessions with computed status |
| `get_session_by_id(session_id)` | Get session with assignments |
| `update_session(session_id, **kwargs)` | Update (only if not yet started) |
| `delete_session(session_id)` | Delete (only if not yet started) |
| `assign_students(session_id, student_ids, group_ids)` | Expand groups, create ExamAssignment rows, skip duplicates |
| `get_monitor_data(session_id)` | List all assigned students with attempt status, answer count, score |
| `compute_session_status(session)` | Return "scheduled"/"active"/"ended" based on current time |

File: `app/services/session_service.py`

### exam_take_service.py

| Function | Description |
|----------|-------------|
| `get_student_exams(student_id)` | Return {upcoming, active, completed} exam lists |
| `start_attempt(session_id, student_id)` | Create or resume attempt, return questions |
| `save_answer(session_id, student_id, question_id, choice_id)` | Upsert single answer |
| `save_answers_batch(session_id, student_id, answers)` | Upsert batch of answers |
| `submit_attempt(session_id, student_id)` | Grade, compute score, lock attempt |
| `get_exam_status(session_id, student_id)` | Return remaining time, status, progress; trigger auto-submit if expired |
| `get_attempt_result(session_id, student_id)` | Return result respecting show_result setting |
| `auto_submit_expired(session_id)` | Find and grade all expired in-progress attempts |

File: `app/services/exam_take_service.py`

---

## 7. Frontend Changes

### New Teacher Pages

| Route | Component | Description |
|-------|-----------|-------------|
| /groups | StudentGroups | Group CRUD, member management |
| /sessions | ExamSessions | Session list with status badges |
| /sessions/new | CreateSession | Form: select exam, times, settings, assign students/groups |
| /sessions/:id | SessionDetail | Session info + live monitor table |

### New Student Pages

| Route | Component | Description |
|-------|-----------|-------------|
| /exam | StudentDashboard | Upcoming, active, completed exam cards |
| /exam/:sessionId | TakeExam | Exam-taking UI with timer, navigator, choices |
| /exam/:sessionId/result | ExamResult | Score display (respects show_result) |

### StudentLayout

Students get a separate minimal layout — no sidebar, just a top bar with student name and logout. The `StudentLayout` component wraps all `/exam/*` routes.

### TakeExam Component

Two display modes (controlled by `display_mode` setting):

**all_at_once:** Scrollable page with all questions visible. Question navigator strip at top. Click any question number to scroll to it.

**one_by_one:** Single question with prev/next buttons. Question navigator strip at top shows answered/current/unanswered. Answer selection highlights the chosen choice.

Both modes share:
- Countdown timer (top bar, always visible, syncs with server every 30s)
- Question navigator (numbered squares: green=answered, blue=current, gray=unanswered)
- Submit button with confirmation dialog
- Connection status indicator
- Auto-submit when timer reaches 0

### New React Query Hooks

| Hook File | Hooks |
|-----------|-------|
| use-groups.js | useGroups, useGroup, useCreateGroup, useDeleteGroup, useAddMembers, useRemoveMember |
| use-sessions.js | useSessions, useSession, useCreateSession, useUpdateSession, useDeleteSession, useAssignStudents, useMonitorSession |
| use-student-exam.js | useStudentExams, useStartAttempt, useExamStatus, useSaveAnswer, useSaveAnswersBatch, useSubmitExam, useExamResult |

---

## 8. Sidebar Navigation Updates

Add to teacher sidebar under "Main" group:
- Groups (icon: Users)
- Online Exams (icon: Monitor) → links to /sessions

---

## 9. Configuration

No new config values needed. All settings are per-session (stored in ExamSession model).

---

## 10. Testing Strategy

### Model Tests
- `tests/test_models/test_group.py` — StudentGroup, StudentGroupMember CRUD, relationships
- `tests/test_models/test_exam_session.py` — ExamSession, ExamAssignment, ExamAttempt, OnlineAnswer CRUD, relationships, to_dict()

### Service Tests
- `tests/test_services/test_group_service.py` — group CRUD, add/remove members, duplicate handling
- `tests/test_services/test_session_service.py` — session CRUD, assignment expansion, status computation, monitor data
- `tests/test_services/test_exam_take_service.py` — start attempt, save answers, submit + grading, auto-submit, randomization, resume

### Route Tests
- `tests/test_routes/test_groups.py` — all group endpoints with auth
- `tests/test_routes/test_sessions.py` — all session endpoints with auth
- `tests/test_routes/test_student_exam.py` — full exam flow as student, access control

### Key Test Scenarios
- Student starts exam → saves answers → submits → gets correct score
- Randomization produces different question orders for different students
- Auto-submit grades in-progress attempts after end_time
- Student can resume after disconnect (answers preserved)
- Student cannot access unassigned exam (403)
- Student cannot start exam before start_time or after end_time
- Teacher cannot modify active or ended session
- Batch answer save handles duplicates correctly (upsert)
- show_result="none" hides score from student
- show_result="score_and_answers" reveals correct answers

---

## 11. File Structure (new/modified files)

```
NEW FILES:
  app/models/group.py                — StudentGroup, StudentGroupMember
  app/models/exam_session.py         — ExamSession, ExamAssignment
  app/models/exam_attempt.py         — ExamAttempt
  app/models/online_answer.py        — OnlineAnswer
  app/services/group_service.py      — group CRUD
  app/services/session_service.py    — session management + monitoring
  app/services/exam_take_service.py  — exam-taking flow + grading
  app/routes/groups.py               — /api/groups/* blueprint
  app/routes/sessions.py             — /api/sessions/* blueprint
  app/routes/student_exam.py         — /api/student/exams/* blueprint
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
  app/routes/__init__.py             — register new blueprints
  frontend/src/App.jsx               — add student routes + teacher routes
  frontend/src/components/layout/Sidebar.jsx — add Groups + Online Exams nav items
```
