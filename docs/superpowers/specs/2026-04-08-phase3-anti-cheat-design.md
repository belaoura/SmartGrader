# Phase 3: Anti-Cheat System — Design Spec

## Overview

Add a proctoring and anti-cheat layer to the online exam system. Browser-side AI (TensorFlow.js BlazeFace) detects faces and gaze in real-time. DOM event listeners track tab switches, focus loss, copy/paste, and keyboard shortcuts. Periodic + event-triggered webcam snapshots are uploaded to the server for storage and optional AI verification. Teachers configure proctoring settings per session and monitor events via an enhanced dashboard.

## Goals

- Browser-side face detection (face count, gaze estimation) via TensorFlow.js BlazeFace
- Extended browser event tracking (tab switch, focus loss, full-screen exit, copy/paste, right-click, keyboard shortcuts)
- Full-screen lockdown mode (optional per session)
- Periodic webcam snapshots (every 60s) + event-triggered captures
- Server-side AI verification of snapshots (optional, uses existing Qwen model)
- On-demand live frame capture (teacher requests, student's browser responds)
- Configurable cheat response: log only, warn student, warn + escalate (auto-flag)
- Configurable warning threshold before auto-flagging
- Teacher proctoring dashboard with event timeline, snapshot gallery, flag management
- Zero new Python dependencies

## Non-Goals (deferred)

- Live video streaming / WebRTC
- Screen recording / VNC
- Browser extension or desktop app lockdown
- Keystroke logging
- Network traffic analysis
- Audio monitoring

---

## 1. Data Model

### Modified Model: ExamSession — add proctoring columns

| New Column | Type | Notes |
|------------|------|-------|
| proctoring_enabled | Boolean, default False | Master switch for anti-cheat |
| lockdown_enabled | Boolean, default False | Require full-screen mode |
| cheat_response | String(20), default "log_only" | "log_only", "warn", or "warn_escalate" |
| warning_threshold | Integer, default 3 | Warnings before auto-flag (when warn_escalate) |

File: `app/models/exam_session.py` (modify existing)

### Modified Model: ExamAttempt — add proctoring fields

| New Column | Type | Notes |
|------------|------|-------|
| flagged | Boolean, default False | Auto or manually flagged |
| warning_count | Integer, default 0 | Running count of medium/high severity events |

File: `app/models/exam_attempt.py` (modify existing)

### New Model: ProctorEvent

| Column | Type | Notes |
|--------|------|-------|
| id | Integer, PK | |
| attempt_id | Integer, FK → exam_attempts, NOT NULL | Which student attempt |
| event_type | String(30), NOT NULL | See event types below |
| severity | String(10), NOT NULL | "low", "medium", "high" |
| details | Text, nullable | JSON with extra context |
| snapshot_id | Integer, FK → proctor_snapshots, nullable | Associated screenshot |
| created_at | String(30) | ISO timestamp |

Event types:
- Browser: "tab_switch", "focus_lost", "fullscreen_exit", "copy_paste", "right_click", "keyboard_shortcut"
- Webcam AI: "no_face", "multiple_faces", "gaze_away", "phone_detected"

Severity mapping:
- High: tab_switch, fullscreen_exit, no_face, multiple_faces, phone_detected
- Medium: focus_lost, gaze_away, copy_paste, keyboard_shortcut
- Low: right_click

### New Model: ProctorSnapshot

| Column | Type | Notes |
|--------|------|-------|
| id | Integer, PK | |
| attempt_id | Integer, FK → exam_attempts, NOT NULL | |
| file_path | String(500), NOT NULL | Path to saved JPEG |
| snapshot_type | String(20), NOT NULL | "periodic", "event_triggered", "on_demand" |
| ai_analysis | Text, nullable | JSON with server-side AI results |
| created_at | String(30) | ISO timestamp |

### New Model: CaptureRequest

| Column | Type | Notes |
|--------|------|-------|
| id | Integer, PK | |
| attempt_id | Integer, FK → exam_attempts, NOT NULL | |
| status | String(20), default "pending" | "pending" or "fulfilled" |
| created_at | String(30) | ISO timestamp |

File: `app/models/proctor.py` (all three new models)

### Relationships

- ExamAttempt 1:N ProctorEvent
- ExamAttempt 1:N ProctorSnapshot
- ExamAttempt 1:N CaptureRequest
- ProctorEvent N:1 ProctorSnapshot (optional link)

### Existing Models — No Changes

StudentGroup, StudentGroupMember, ExamAssignment, OnlineAnswer, Exam, Question, Choice, Student, User, Result — all untouched.

---

## 2. API Endpoints

### Student Proctoring Endpoints

All require `@require_auth @require_role("student")`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/student/exams/\<session_id\>/proctor/event | Log a proctor event {event_type, severity, details} |
| POST | /api/student/exams/\<session_id\>/proctor/snapshot | Upload webcam screenshot (multipart: file + snapshot_type) |
| GET | /api/student/exams/\<session_id\>/proctor/status | Get warning_count, flagged, pending capture requests |

### Teacher Proctoring Endpoints

All require `@require_auth @require_role("teacher")`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/sessions/\<id\>/proctor/events | List all events (filterable: ?student_id=&event_type=) |
| GET | /api/sessions/\<id\>/proctor/snapshots | List all snapshots (filterable: ?student_id=) |
| GET | /api/sessions/\<id\>/proctor/snapshots/\<snapshot_id\>/image | Serve snapshot JPEG file |
| POST | /api/sessions/\<id\>/proctor/capture/\<student_id\> | Request on-demand snapshot |
| GET | /api/sessions/\<id\>/proctor/summary | Aggregated stats per student |
| POST | /api/sessions/\<id\>/proctor/flag/\<attempt_id\> | Toggle flag on attempt |

Blueprint: `app/routes/proctoring.py` → `proctoring_bp` registered at `/api`

---

## 3. On-Demand Capture Flow

1. Teacher clicks "Capture Now" on a student in the dashboard
2. Server creates `CaptureRequest(attempt_id, status="pending")`
3. Student's `ProctorWarningBanner` polls `/proctor/status` every 15s
4. Response includes `pending_capture: true`
5. Browser captures webcam frame → uploads via `/proctor/snapshot` with type "on_demand"
6. Server marks CaptureRequest as "fulfilled"
7. Teacher dashboard refreshes → shows new snapshot

---

## 4. Warning Escalation Logic

1. Every ProctorEvent with severity "medium" or "high" → `attempt.warning_count += 1`
2. Based on session's `cheat_response` setting:
   - `log_only`: events logged, student sees nothing
   - `warn`: student sees warning banner with count ("Warning X/Y")
   - `warn_escalate`: student sees warning + when `warning_count >= warning_threshold` → `attempt.flagged = True`
3. Teacher can also manually flag/unflag via `/proctor/flag/<attempt_id>`

---

## 5. Browser-Side Anti-Cheat Engine

### ProctorEngine.jsx

Invisible component mounted inside TakeExam when `proctoring_enabled=true`.

**Webcam access:** Requests camera on mount via `navigator.mediaDevices.getUserMedia`. Shows error if denied — exam cannot proceed without camera when proctoring is on.

**Face detection loop (every 2s):**
- Loads BlazeFace model on mount (once)
- Runs detection on webcam video element
- 0 faces detected → emit "no_face" (high severity)
- 2+ faces → emit "multiple_faces" (high severity)
- Face landmarks → basic gaze: if estimated eye direction is off-center for >5 consecutive checks (10s) → "gaze_away" (medium)

**Browser event listeners:**
- `document.visibilitychange` (hidden) → "tab_switch" (high)
- `window.blur` → "focus_lost" (medium)
- `document.fullscreenchange` (exit when lockdown active) → "fullscreen_exit" (high)
- `copy`, `cut`, `paste` events → "copy_paste" (medium)
- `contextmenu` → "right_click" (low)
- `keydown` for Ctrl+C, Ctrl+V, Ctrl+A, PrintScreen → "keyboard_shortcut" (medium)

**Event throttling:** Same event_type limited to max 1 per 10 seconds to prevent spam.

**Snapshot capture:** On each suspicious event, capture webcam frame via canvas.toBlob() as JPEG.

**Periodic snapshots:** Every 60s, capture and upload a baseline screenshot (type "periodic").

**Upload queue:** Events sent via `POST /proctor/event`, snapshots via `POST /proctor/snapshot`. Failed uploads retry up to 3 times with exponential backoff.

### FullscreenLockdown.jsx

Mounted when `lockdown_enabled=true`.

- Calls `document.documentElement.requestFullscreen()` on mount
- Listens for `fullscreenchange` — if exited, shows blocking overlay: "Return to full-screen to continue your exam" with a "Re-enter Full Screen" button
- Logs "fullscreen_exit" event via ProctorEngine

### ProctorWarningBanner.jsx

Mounted when `cheat_response` is "warn" or "warn_escalate".

- Polls `GET /proctor/status` every 15s
- If `warning_count > 0`: shows dismissible banner "Suspicious activity detected — Warning X of Y"
- If `pending_capture`: triggers webcam capture → upload as "on_demand" snapshot
- If `flagged`: shows persistent red banner "Your exam has been flagged for review"

---

## 6. Server-Side AI Verification (Optional)

`proctor_service.analyze_snapshot(snapshot_id)`:

1. Loads snapshot image from disk
2. Checks if AI model is loaded via existing `get_ai_status()`
3. If available, sends image to Qwen vision model with prompt: "Analyze this exam proctoring image. Report: 1) How many faces are visible? 2) Is there a phone or electronic device visible? Return JSON: {face_count: N, phone_detected: bool}"
4. Stores result in `ProctorSnapshot.ai_analysis` as JSON
5. If `phone_detected=true`, creates a ProctorEvent with type "phone_detected" (high severity)

This is optional — if the AI model isn't loaded, snapshots are stored without analysis. Teacher can review manually.

---

## 7. Backend Service

### proctor_service.py

| Function | Description |
|----------|-------------|
| `log_event(attempt_id, event_type, severity, details, snapshot_id)` | Create ProctorEvent, increment warning_count if severity >= medium, auto-flag if threshold reached |
| `save_snapshot(attempt_id, file, snapshot_type)` | Save JPEG to uploads/proctor/, create record, optionally trigger AI |
| `get_proctor_status(attempt_id)` | Return warning_count, flagged, pending capture request |
| `get_session_events(session_id, student_id, event_type)` | List events with filters |
| `get_session_snapshots(session_id, student_id)` | List snapshots with filter |
| `get_proctor_summary(session_id)` | Aggregate: per student event count, warning count, flagged |
| `request_capture(attempt_id)` | Create pending CaptureRequest |
| `fulfill_capture(attempt_id)` | Mark request as fulfilled |
| `toggle_flag(attempt_id)` | Manually flag/unflag |
| `analyze_snapshot(snapshot_id)` | Optional server-side AI analysis |

File: `app/services/proctor_service.py`

---

## 8. Frontend Changes

### New Components

| Component | Description |
|-----------|-------------|
| ProctorEngine.jsx | Invisible: face detection + event tracking + snapshot capture |
| FullscreenLockdown.jsx | Full-screen enforcement overlay |
| ProctorWarningBanner.jsx | Warning display + capture request handler |

### New Hooks (use-proctor.js)

| Hook | Description |
|------|-------------|
| useProctorStatus(sessionId) | Poll student proctor status every 15s |
| useLogEvent() | Mutation: log proctor event |
| useUploadSnapshot() | Mutation: upload snapshot |
| useProctorEvents(sessionId) | Teacher: fetch events, refetch 10s |
| useProctorSnapshots(sessionId) | Teacher: fetch snapshots |
| useProctorSummary(sessionId) | Teacher: aggregated stats |
| useRequestCapture() | Teacher: request on-demand snapshot |
| useToggleFlag() | Teacher: flag/unflag attempt |

### Modified Pages

**TakeExam.jsx:** Mount `<ProctorEngine>`, `<FullscreenLockdown>`, `<ProctorWarningBanner>` conditionally based on session settings.

**CreateSession.jsx:** Add proctoring settings section: enable toggle, lockdown toggle, cheat response radio, warning threshold input.

**SessionDetail.jsx:** Add "Proctoring" tab with event timeline, snapshot gallery, per-student proctoring status, capture/flag actions. Auto-refreshes.

---

## 9. New Dependencies

### JavaScript (package.json)

- `@tensorflow/tfjs` — ML runtime for browser
- `@tensorflow-models/blazeface` — face detection model (~200KB)

### Python

- None

---

## 10. Configuration

No new config values. All proctoring settings are per-session (stored in ExamSession columns).

Snapshot storage directory: `uploads/proctor/{session_id}/{attempt_id}/` — created automatically on first upload.

---

## 11. Testing Strategy

### Model Tests
- `tests/test_models/test_proctor.py` — ProctorEvent, ProctorSnapshot, CaptureRequest CRUD, relationships

### Service Tests
- `tests/test_services/test_proctor_service.py` — log event with warning escalation, save snapshot, capture request lifecycle, flag toggle, summary aggregation, AI analysis skip when model unavailable

### Route Tests
- `tests/test_routes/test_proctoring.py` — student event logging, snapshot upload, teacher event listing, on-demand capture, flag toggle, auth enforcement

### Key Test Scenarios
- Event with high severity increments warning_count
- Auto-flag triggers at exact threshold
- Log-only mode: warning_count tracks but flagged stays false
- Snapshot saved to correct directory with correct path in DB
- On-demand capture: pending → fulfilled lifecycle
- Teacher can manually flag/unflag
- Proctoring endpoints return 403 for wrong role
- Event throttling (same type within 10s window) — tested in frontend
- Proctoring disabled: student proctor endpoints still accept events (graceful)
- AI analysis gracefully skips when model not loaded

---

## 12. File Structure

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
  frontend/src/hooks/use-sessions.js   — add proctoring hooks (or use separate use-proctor.js)
```
