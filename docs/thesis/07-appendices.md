# Appendices

## Appendix A: Full API Reference

SmartGrader exposes a RESTful API with approximately 40 endpoints organised into functional groups. All endpoints are prefixed with `/api/` and return JSON responses. Error responses follow a consistent format: `{"error": "<message>"}` with an appropriate HTTP status code. Protected endpoints require the header `Authorization: Bearer <token>`.

### A.1 Health Check

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 1 | GET | `/api/health` | None | Returns application status and version |

**Example Response (200):**
```json
{"status": "ok", "version": "1.0.0"}
```

---

### A.2 Authentication Endpoints

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 2 | POST | `/api/auth/register` | None | Register a teacher account |
| 3 | POST | `/api/auth/login` | None | Log in; returns JWT access token |
| 4 | POST | `/api/auth/barcode-login` | None | Student barcode/QR login; returns JWT |
| 5 | GET | `/api/auth/me` | Required | Get current user profile |

**Example Request (Login):**
```
POST /api/auth/login
Content-Type: application/json

{"username": "prof_dupont", "password": "secure123"}
```

**Example Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "role": "teacher",
  "user_id": 1
}
```

**Example Request (Barcode Login):**
```
POST /api/auth/barcode-login
Content-Type: application/json

{"matricule": "202312345"}
```

**Example Response (200):**
```json
{"access_token": "eyJhbGciOiJIUzI1NiIsInR5..."}
```

---

### A.3 Exam Endpoints

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 6 | GET | `/api/exams` | Teacher | List all examinations |
| 7 | POST | `/api/exams` | Teacher | Create a new examination |
| 8 | GET | `/api/exams/<exam_id>` | Teacher | Get a single examination by ID |
| 9 | PUT | `/api/exams/<exam_id>` | Teacher | Update an examination |
| 10 | DELETE | `/api/exams/<exam_id>` | Teacher | Delete an examination (cascades) |

**Example Request (Create):**
```
POST /api/exams
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Biology Midterm",
  "subject": "Biology",
  "date": "2026-03-15",
  "total_marks": 20
}
```

**Example Response (201):**
```json
{"id": 1, "title": "Biology Midterm", "subject": "Biology", "date": "2026-03-15", "total_marks": 20.0}
```

---

### A.4 Question Endpoints

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 11 | GET | `/api/exams/<exam_id>/questions` | Teacher | List questions for an exam |
| 12 | POST | `/api/exams/<exam_id>/questions` | Teacher | Create a question with choices |

**Example Request (Create Question):**
```
POST /api/exams/1/questions
Authorization: Bearer <token>
Content-Type: application/json

{
  "question_text": "Which organelle produces ATP?",
  "question_choices_number": 4,
  "marks": 2,
  "choices": [
    {"choice_label": "A", "choice_text": "Nucleus", "is_correct": false},
    {"choice_label": "B", "choice_text": "Mitochondria", "is_correct": true},
    {"choice_label": "C", "choice_text": "Ribosome", "is_correct": false},
    {"choice_label": "D", "choice_text": "Golgi apparatus", "is_correct": false}
  ]
}
```

---

### A.5 Student Endpoints

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 13 | GET | `/api/students` | Teacher | List all students |
| 14 | POST | `/api/students` | Teacher | Register a student |
| 15 | GET | `/api/students/<student_id>` | Teacher | Get a student by ID |
| 16 | POST | `/api/students/import` | Teacher | Bulk import students from CSV |

**Example Request (CSV Import):**
```
POST /api/students/import
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: [students.csv]
```

CSV format:
```
name,matricule,email
Amina Boucherit,202312345,amina.b@university.dz
Yacine Merrouche,202312346,y.merrouche@university.dz
```

**Example Response (200):**
```json
{"created": 2, "skipped": 0, "errors": []}
```

---

### A.6 Student Group Endpoints

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 17 | GET | `/api/groups` | Teacher | List all student groups |
| 18 | POST | `/api/groups` | Teacher | Create a group |
| 19 | GET | `/api/groups/<group_id>` | Teacher | Get a group with its members |
| 20 | PUT | `/api/groups/<group_id>` | Teacher | Update group name/description |
| 21 | DELETE | `/api/groups/<group_id>` | Teacher | Delete a group |
| 22 | POST | `/api/groups/<group_id>/members` | Teacher | Add students to a group |
| 23 | DELETE | `/api/groups/<group_id>/members/<student_id>` | Teacher | Remove a student from a group |

**Example Request (Create Group):**
```
POST /api/groups
Authorization: Bearer <token>
Content-Type: application/json

{"name": "L3 Informatique Groupe A", "description": "Morning group, 2025-2026"}
```

**Example Request (Add Members):**
```
POST /api/groups/1/members
Authorization: Bearer <token>
Content-Type: application/json

{"student_ids": [1, 2, 3, 4, 5]}
```

---

### A.7 Exam Session Endpoints

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 24 | GET | `/api/sessions` | Teacher | List all exam sessions |
| 25 | POST | `/api/sessions` | Teacher | Create a session |
| 26 | GET | `/api/sessions/<session_id>` | Teacher | Get session details |
| 27 | PUT | `/api/sessions/<session_id>/activate` | Teacher | Activate a scheduled session |
| 28 | PUT | `/api/sessions/<session_id>/close` | Teacher | Close an active session |
| 29 | GET | `/api/sessions/<session_id>/attempts` | Teacher | List all attempts for a session |

**Example Request (Create Session):**
```
POST /api/sessions
Authorization: Bearer <token>
Content-Type: application/json

{
  "exam_id": 1,
  "group_id": 1,
  "start_time": "2026-04-10T09:00:00",
  "duration_minutes": 90
}
```

**Example Response (201):**
```json
{
  "id": 1,
  "exam_id": 1,
  "group_id": 1,
  "start_time": "2026-04-10T09:00:00",
  "duration_minutes": 90,
  "status": "scheduled"
}
```

---

### A.8 Student Exam Endpoints

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 30 | GET | `/api/exam/active` | Student | Get the student's active session |
| 31 | POST | `/api/exam/attempt` | Student | Begin an examination attempt |
| 32 | GET | `/api/exam/attempt/<attempt_id>` | Student | Get attempt state and questions |
| 33 | POST | `/api/exam/attempt/<attempt_id>/answer` | Student | Save or update an answer |
| 34 | POST | `/api/exam/attempt/<attempt_id>/submit` | Student | Submit the attempt |

**Example Request (Save Answer):**
```
POST /api/exam/attempt/1/answer
Authorization: Bearer <student_token>
Content-Type: application/json

{"question_id": 3, "choice_id": 12}
```

**Example Response (200):**
```json
{"question_id": 3, "choice_id": 12, "answered_at": "2026-04-10T09:23:45"}
```

**Example Response (Submit, 200):**
```json
{
  "attempt_id": 1,
  "status": "submitted",
  "score": 16.0,
  "percentage": 80.0,
  "submitted_at": "2026-04-10T10:28:00"
}
```

---

### A.9 Proctoring Endpoints

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 35 | POST | `/api/proctor/event` | Student | Report a proctoring event |
| 36 | POST | `/api/proctor/snapshot` | Student | Upload a webcam snapshot |
| 37 | GET | `/api/proctor/attempt/<attempt_id>/events` | Teacher | Get events for an attempt |
| 38 | GET | `/api/proctor/attempt/<attempt_id>/snapshots` | Teacher | Get snapshots for an attempt |

**Example Request (Report Event):**
```
POST /api/proctor/event
Authorization: Bearer <student_token>
Content-Type: application/json

{
  "attempt_id": 1,
  "event_type": "tab_switch",
  "severity": "warning",
  "details": {"from_url": "/exam", "timestamp_client": 1712746523000}
}
```

**Example Request (Upload Snapshot):**
```
POST /api/proctor/snapshot
Authorization: Bearer <student_token>
Content-Type: multipart/form-data

attempt_id: 1
face_detected: true
image: [snapshot.jpg]
```

**Example Response (Events, 200):**
```json
{
  "attempt_id": 1,
  "events": [
    {"id": 1, "event_type": "tab_switch", "severity": "warning", "occurred_at": "2026-04-10T09:25:10"},
    {"id": 2, "event_type": "face_missing", "severity": "warning", "occurred_at": "2026-04-10T09:31:05"}
  ],
  "warning_count": 2
}
```

---

### A.10 Scanning and Grading Endpoints

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 39 | POST | `/api/scan/upload` | Teacher | Upload and scan an answer sheet image |
| 40 | GET | `/api/results/exam/<exam_id>` | Teacher | Get all results for an exam |
| 41 | POST | `/api/results` | Teacher | Save a grading result |

---

### A.11 AI Endpoints

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 42 | GET | `/api/ai/status` | Teacher | Get AI model status |
| 43 | POST | `/api/ai/ocr` | Teacher | Extract handwritten text from image |
| 44 | POST | `/api/ai/evaluate` | Teacher | Evaluate a student answer |
| 45 | POST | `/api/ai/correct` | Teacher | Submit a teacher correction (RAG) |
| 46 | GET | `/api/ai/corrections/<question_id>` | Teacher | List corrections for a question |

---

## Appendix B: Database Schema

The SmartGrader database uses SQLite and comprises 15 tables with foreign key constraints and cascade deletion rules.

### B.1 Original Core Tables

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    matricule TEXT UNIQUE NOT NULL,
    email TEXT
);

CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    subject TEXT,
    date TEXT,
    total_marks REAL
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_choices_number INTEGER NOT NULL,
    marks REAL NOT NULL,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS choices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    choice_label TEXT NOT NULL,
    choice_text TEXT NOT NULL,
    is_correct INTEGER DEFAULT 0,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS student_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_choice_id INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY (selected_choice_id) REFERENCES choices(id)
);

CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    exam_id INTEGER NOT NULL,
    score REAL NOT NULL,
    percentage REAL,
    graded_at TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ai_corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    student_text TEXT NOT NULL,
    ai_score REAL NOT NULL,
    ai_feedback TEXT,
    teacher_score REAL NOT NULL,
    teacher_feedback TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);
```

### B.2 Authentication Table (Phase 1)

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('teacher', 'student')),
    student_id INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL
);
```

### B.3 Online Examination Tables (Phase 2)

```sql
CREATE TABLE IF NOT EXISTS student_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS group_members (
    group_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    PRIMARY KEY (group_id, student_id),
    FOREIGN KEY (group_id) REFERENCES student_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS exam_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'scheduled',
    created_at TEXT NOT NULL,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES student_groups(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS exam_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    started_at TEXT NOT NULL,
    submitted_at TEXT,
    status TEXT NOT NULL DEFAULT 'in_progress',
    score REAL,
    percentage REAL,
    FOREIGN KEY (session_id) REFERENCES exam_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS online_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_choice_id INTEGER,
    answered_at TEXT NOT NULL,
    FOREIGN KEY (attempt_id) REFERENCES exam_attempts(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY (selected_choice_id) REFERENCES choices(id)
);
```

### B.4 Proctoring Tables (Phase 3)

```sql
CREATE TABLE IF NOT EXISTS proctor_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'info',
    details TEXT,
    occurred_at TEXT NOT NULL,
    FOREIGN KEY (attempt_id) REFERENCES exam_attempts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS proctor_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    face_detected INTEGER NOT NULL DEFAULT 1,
    captured_at TEXT NOT NULL,
    FOREIGN KEY (attempt_id) REFERENCES exam_attempts(id) ON DELETE CASCADE
);
```

### B.5 Indexes

```sql
-- Original indexes
CREATE INDEX IF NOT EXISTS idx_questions_exam ON questions(exam_id);
CREATE INDEX IF NOT EXISTS idx_choices_question ON choices(question_id);
CREATE INDEX IF NOT EXISTS idx_answers_student ON student_answers(student_id);
CREATE INDEX IF NOT EXISTS idx_answers_question ON student_answers(question_id);
CREATE INDEX IF NOT EXISTS idx_results_exam ON results(exam_id);

-- New indexes (Phases 1–3)
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_student ON users(student_id);
CREATE INDEX IF NOT EXISTS idx_sessions_exam ON exam_sessions(exam_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON exam_sessions(status);
CREATE INDEX IF NOT EXISTS idx_attempts_session ON exam_attempts(session_id);
CREATE INDEX IF NOT EXISTS idx_attempts_student ON exam_attempts(student_id);
CREATE INDEX IF NOT EXISTS idx_online_answers_attempt ON online_answers(attempt_id);
CREATE INDEX IF NOT EXISTS idx_proctor_events_attempt ON proctor_events(attempt_id);
CREATE INDEX IF NOT EXISTS idx_proctor_snapshots_attempt ON proctor_snapshots(attempt_id);
```

### B.6 Entity-Relationship Summary

The database follows a hierarchical structure centred on the `exams` table for content, and the `exam_sessions` table for online delivery. The `students` table is referenced by `users` (authentication), `group_members` (group assignment), `exam_attempts` (online exam participation), and `student_answers` (MCQ scan results). The `proctor_events` and `proctor_snapshots` tables are linked to `exam_attempts`, associating all integrity monitoring data with specific examination sittings. All foreign keys use `ON DELETE CASCADE` to maintain referential integrity.

---

## Appendix C: Installation Guide

This appendix provides step-by-step instructions for installing and running SmartGrader across all supported deployment modes.

### C.1 Prerequisites

- **Operating System:** Windows 10/11 or Linux (Ubuntu 22.04+)
- **Python:** 3.10 or higher
- **Node.js:** 18 or higher (for frontend build)
- **GPU:** NVIDIA GPU with at least 6 GB VRAM and CUDA 12.x drivers (required for AI grading only)
- **wkhtmltopdf:** Required for PDF answer sheet generation
- **Docker + Docker Compose:** Required for Docker deployment mode only

### C.2 Python Environment Setup

```bash
git clone https://github.com/your-org/SmartGrader.git
cd SmartGrader

python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### C.3 CUDA and PyTorch Setup (for AI grading)

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements-ai.txt

python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### C.4 Database Initialisation

```bash
flask db upgrade
# or from raw SQL:
sqlite3 instance/smart_grader.db < schema.sql
```

### C.5 First Teacher Account

```bash
# Register the first teacher account via the API
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "changeme", "role": "teacher"}'
```

### C.6 Frontend Setup

```bash
cd frontend
npm install
npm run dev        # Development server at http://localhost:5173
npm run build      # Production build to frontend/dist/
```

### C.7 Running (Development)

```bash
# Terminal 1: Flask backend
flask run --host=0.0.0.0 --port=5000

# Terminal 2: React frontend
cd frontend && npm run dev
```

### C.8 Running (LAN / Production with Gunicorn)

```bash
cd frontend && npm run build
gunicorn "app:create_app('production')" \
  --workers 4 \
  --bind 0.0.0.0:5000 \
  --timeout 120
```

### C.9 Running (Docker)

```bash
# Copy and edit the environment file
cp .env.example .env
# Set JWT_SECRET_KEY, CORS_ORIGINS, etc.

docker compose up --build -d
```

### C.10 Running Tests

```bash
pytest                        # All 191 tests
pytest -v                     # Verbose output
pytest tests/test_auth/       # Auth tests only
pytest --cov=app --cov-report=html  # Coverage report
```

---

## Appendix D: User Manual

This appendix provides a step-by-step guide for using all pages and features of the SmartGrader application.

### D.1 Login

All users (teachers and students) are presented with the Login page on first visit. Enter your username and password and click "Login". Upon successful authentication, you are redirected to the Dashboard (teachers) or the active examination (students).

**Students using barcode login:** Present your student identity card for scanning. The barcode reader enters your matricule automatically and logs you in without requiring a password.

### D.2 Dashboard (Teacher)

The Dashboard page is the teacher's landing page. It displays:
- Summary statistics: total examinations, total students, average grading percentage, recent activity.
- Score distribution chart (bar chart, Recharts).
- Recent examinations list with titles, dates, and question counts.

### D.3 Exams

The Exams page displays a sortable, searchable table of all examinations.

**To create an examination:** Click "New Exam", fill in the title (required), subject, date, and total marks, then click "Create".

**To edit or delete:** Use the action icons on each exam row. Deletion permanently removes all associated questions, choices, answers, and results.

### D.4 Exam Detail

Navigate to this page by clicking an examination title. Here you can:
- Add and edit questions with MCQ choices or short-answer format.
- Designate the correct answer for each MCQ question.
- Click "Generate Sheet" to produce a printable A4 PDF answer sheet.

### D.5 Students

The Students page manages the student registry.

**To register a student:** Click "Add Student", enter name, matricule (must be unique), and optional email.

**To import students from CSV:** Click "Import CSV" and upload a file with columns `name`, `matricule`, `email`.

### D.6 Groups

The Groups page manages student groups for online examination assignment.

**To create a group:** Click "New Group", enter a name and optional description.

**To add students to a group:** Open the group detail, click "Add Students", and select students from the registry.

### D.7 Sessions

The Sessions page manages online examination sessions.

**To create a session:** Click "New Session", select an examination, a student group, a start time, and a duration in minutes.

**To activate a session:** Click "Activate" on a scheduled session. Enrolled students can now access the examination.

**To monitor an active session:** Click "Monitor" to open the Proctoring Dashboard.

**To close a session:** Click "Close" when the examination period ends. Pending attempts are auto-submitted.

### D.8 Proctoring Dashboard (Teacher)

The Proctoring Dashboard provides real-time monitoring of all students in an active session.

- The student list shows each student's status (in progress / submitted / terminated) and warning count.
- Click a student row to expand the event timeline and snapshot grid.
- Events are colour-coded: grey (info), yellow (single warning), red (multiple warnings).
- Snapshots are displayed in chronological order with a face-detected indicator on each thumbnail.

### D.9 Scanner — MCQ Tab

**To scan an MCQ answer sheet:**
1. Select the examination from the dropdown.
2. Upload or drag and drop the scanned image.
3. Review detected answers (green = correct, red = incorrect, grey = unanswered).
4. Associate with a student and click "Save Result".

### D.10 Scanner — AI Tab

**To grade a handwritten answer sheet:**
1. Verify the AI model is loaded (green status indicator).
2. Select the examination and question.
3. Upload the scanned page.
4. Click "Run OCR"; review and optionally edit the extracted text.
5. Click "Evaluate"; review the AI score, feedback, and confidence.
6. If incorrect, enter the correct score and feedback and click "Submit Correction".

### D.11 Student Examination Page

After logging in as a student, you are automatically directed to your active examination if one is assigned to your group.

1. The page shows the examination title and a countdown timer.
2. Select your answer for each question using the radio buttons.
3. Each answer is saved automatically to the server.
4. Use the question grid or previous/next buttons to navigate.
5. Click "Submit Exam" to finalise your attempt, or wait for the timer to expire.

**Note:** The page requires webcam access for proctoring. Grant webcam permission when prompted. Keep your face visible in the camera at all times during the examination. Switching tabs, exiting fullscreen, or obscuring the camera will generate integrity warnings.

### D.12 Results

The Results page displays grading results with filtering by examination and sorting by any column.

### D.13 Settings

The Settings page allows:
- Theme selection (light / dark mode), persisted across sessions.
- AI model status monitoring (model name, loaded state, VRAM usage).
- Scanner threshold adjustment (fill threshold, area bounds, circularity minimum).
