# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SmartGrader is a web-based exam platform covering four complete sub-systems:
1. **Exam Management & OMR Scanning** -- Create MCQ exams, generate printable A4 answer sheets, scan filled sheets with OpenCV
2. **AI Grading** -- Qwen2.5-VL-3B vision model evaluates handwritten answers with RAG feedback loop
3. **Online Exam Engine** -- Browser-based exam delivery with groups, sessions, countdown timer, answer persistence, and teacher monitoring
4. **Anti-Cheat Proctoring** -- Browser-side face detection (BlazeFace), DOM event tracking, webcam snapshots, configurable cheat response

Authentication uses JWT with httpOnly cookies. Roles: teacher, student, admin. Built as a PFE (final-year graduation project).

## Running the Application

```bash
pip install -r requirements.txt
python -m scripts.create_admin   # bootstrap first admin account
python run.py                    # Flask API at http://localhost:5000
```

### LAN Mode (Classroom)

```bash
cd frontend && npm run build && cd ..
python run.py --lan              # serves built frontend + API at http://<ip>:5000
```

### Optional SSL

```bash
python run.py --ssl              # generates self-signed cert and runs HTTPS
```

### Docker

```bash
cp .env.example .env
docker-compose up -d             # Nginx on port 80, Flask via Gunicorn internally
```

Health check: `GET /api/health`.

### Database

SQLAlchemy ORM with SQLite. Database auto-creates in `instance/smart_grader.db`. Use Flask-Migrate for schema changes:
```bash
flask db migrate -m "description"
flask db upgrade
```

To seed sample data: `python -m scripts.seed_data`
To migrate from legacy DB: `python -m scripts.migrate_data path/to/old.db`

### Testing

```bash
pytest tests/ -v              # all tests
pytest tests/test_models/ -v  # just model tests
pytest tests/ -v --tb=short   # compact output
```

191 tests across models, services, scanner, routes, auth, sessions, and proctoring.

## Architecture

```
app/
  __init__.py          # Flask app factory (create_app)
  config.py            # All configuration (Config, DevelopmentConfig, TestingConfig)
  errors.py            # Custom exceptions (ScannerError, GradingError, NotFoundError, etc.)
  logging_config.py    # Python logging setup
  models/              # SQLAlchemy ORM models (~15 tables)
    exam.py            # Exam, Question, Choice
    student.py         # Student, StudentAnswer
    result.py          # Result
    user.py            # User (teacher/student/admin, hashed password, role)
    group.py           # StudentGroup, StudentGroupMember
    session.py         # ExamSession, ExamAssignment, ExamAttempt, OnlineAnswer
    proctor.py         # ProctorEvent, ProctorSnapshot, CaptureRequest
  services/            # Business logic (no HTTP, no UI)
    exam_service.py    # Exam CRUD, question creation, statistics
    grading_service.py # MCQ grading, result saving
    scanner_service.py # Full scan pipeline orchestration
    auth_service.py    # JWT issue/verify, login, bcrypt password check
    session_service.py # Session lifecycle, answer persistence, auto-submit
    proctor_service.py # Event logging, snapshot storage, capture requests
  scanner/             # Image processing modules
    preprocessor.py    # Deskew, crop, grayscale, threshold pipeline
    marker_finder.py   # Triangle alignment marker detection
    detector.py        # Bubble detection (contour-based, configurable)
    grid_mapper.py     # Map bubbles to question/choice grid
    answer_reader.py   # Read filled answers from grid
  routes/              # Flask blueprints (thin HTTP layer)
    auth.py            # /api/auth/* (login, student-login, logout, me)
    admin.py           # /api/admin/* (teacher management, CSV import)
    exams.py           # /api/exams/*
    questions.py       # /api/exams/<id>/questions
    students.py        # /api/students/*
    scanning.py        # /api/scan/upload
    grading.py         # /api/results/*
    groups.py          # /api/groups/*
    sessions.py        # /api/sessions/* (teacher session management + monitor)
    student_exam.py    # /api/student/exams/* (take exam, submit, proctor events)
  ai/                  # Vision model integration (Qwen2.5-VL-3B, OCR, evaluator, RAG)
```

**Layering:** Routes call services, services use models and scanner modules. Routes are thin (validate input, call service, return JSON). Services contain all business logic. Scanner modules are pure image processing with no DB dependencies.

**Auth pattern:** JWT stored in httpOnly cookie. `@require_auth` decorator on protected routes reads cookie, verifies token, injects `g.current_user`. Role checks via `@require_role('teacher')` / `@require_role('admin')`.

**Legacy code** is archived in `legacy/` for reference (original PyQt5 app).

## API Endpoints

```
# Auth
POST           /api/auth/login
POST           /api/auth/student-login
POST           /api/auth/logout
GET            /api/auth/me

# Admin
GET/POST/PUT   /api/admin/teachers
POST           /api/admin/students/import

# Exams
GET/POST       /api/exams
GET/PUT/DELETE /api/exams/<id>
GET/POST       /api/exams/<id>/questions

# Students
GET/POST       /api/students
GET/PUT        /api/students/<id>

# Scanning
POST           /api/scan/upload          (multipart: file + exam_id)

# Results
GET/POST       /api/results
GET            /api/results/exam/<id>

# Groups
GET/POST       /api/groups
GET/PUT/DELETE /api/groups/<id>
POST           /api/groups/<id>/members

# Sessions (teacher)
GET/POST       /api/sessions
GET/PUT/DELETE /api/sessions/<id>
GET            /api/sessions/<id>/monitor
POST           /api/sessions/<id>/proctor/snapshot

# Student exam-taking
GET            /api/student/exams
POST           /api/student/exams/<id>/start
POST           /api/student/exams/<id>/answer
POST           /api/student/exams/<id>/submit
POST           /api/student/exams/<id>/proctor/event
POST           /api/student/exams/<id>/proctor/snapshot

# AI
GET            /api/ai/status
POST           /api/ai/ocr
POST           /api/ai/evaluate
POST           /api/ai/correct
GET            /api/ai/corrections

GET            /api/health
```

## Configuration

All tunable values in `app/config.py`. Key sections:
- Scanner thresholds (FILL_THRESHOLD, CIRCLE_AREA_MIN/MAX, CIRCULARITY_MIN)
- Sheet generation (A4 dimensions, margins, typography)
- AI model settings (VISION_MODEL, CONFIDENCE_THRESHOLD)
- Auth settings (JWT_SECRET, JWT_EXPIRY, COOKIE_SECURE)
- Proctoring settings (SNAPSHOT_INTERVAL, CHEAT_RESPONSE)

Environment-specific configs: DevelopmentConfig, TestingConfig (in-memory SQLite), ProductionConfig.

Environment variables loaded from `.env` (python-dotenv). See `.env.example`.

## Conventions

- Python snake_case throughout
- Python `logging` module (no print statements)
- Custom exceptions in `app/errors.py` with HTTP status codes
- All models have `to_dict()` for JSON serialization
- Tests use pytest fixtures from `tests/conftest.py` (app, db, client)
- Auth: `@require_auth` decorator injects `g.current_user`; `@require_role('teacher')` enforces roles
- Passwords hashed with bcrypt; never stored or logged in plaintext
- JWT tokens issued as httpOnly, SameSite=Strict cookies; no localStorage auth
