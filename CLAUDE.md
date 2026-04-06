# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SmartGrader is a web-based platform for creating, managing, and grading multiple-choice exams. It generates printable answer sheets (HTML + PDF), scans filled sheets using computer vision (OpenCV), and will integrate AI-powered grading for short written answers. This is a PFE (final-year graduation project).

## Running the Application

```bash
pip install -r requirements.txt
python run.py
```

The Flask API runs at `http://localhost:5000`. Health check: `GET /api/health`.

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

40 tests across models, services, scanner, and routes.

## Architecture

```
app/
  __init__.py          # Flask app factory (create_app)
  config.py            # All configuration (Config, DevelopmentConfig, TestingConfig)
  errors.py            # Custom exceptions (ScannerError, GradingError, NotFoundError, etc.)
  logging_config.py    # Python logging setup
  models/              # SQLAlchemy ORM models
    exam.py            # Exam, Question, Choice
    student.py         # Student, StudentAnswer
    result.py          # Result
  services/            # Business logic (no HTTP, no UI)
    exam_service.py    # Exam CRUD, question creation, statistics
    grading_service.py # MCQ grading, result saving
    scanner_service.py # Full scan pipeline orchestration
  scanner/             # Image processing modules
    preprocessor.py    # Deskew, crop, grayscale, threshold pipeline
    marker_finder.py   # Triangle alignment marker detection
    detector.py        # Bubble detection (contour-based, configurable)
    grid_mapper.py     # Map bubbles to question/choice grid
    answer_reader.py   # Read filled answers from grid
  routes/              # Flask blueprints (thin HTTP layer)
    exams.py           # /api/exams/*
    questions.py       # /api/exams/<id>/questions
    students.py        # /api/students/*
    scanning.py        # /api/scan/upload
    grading.py         # /api/results/*
  ai/                  # Vision model integration (Sub-Project 3, not yet implemented)
```

**Layering:** Routes call services, services use models and scanner modules. Routes are thin (validate input, call service, return JSON). Services contain all business logic. Scanner modules are pure image processing with no DB dependencies.

**Legacy code** is archived in `legacy/` for reference (original PyQt5 app).

## API Endpoints

```
GET/POST       /api/exams
GET/PUT/DELETE /api/exams/<id>
GET/POST       /api/exams/<id>/questions
GET/POST       /api/students
GET            /api/students/<id>
POST           /api/scan/upload          (multipart: file + exam_id)
GET            /api/results/exam/<id>
POST           /api/results
GET            /api/health
```

## Configuration

All tunable values in `app/config.py`. Key sections:
- Scanner thresholds (FILL_THRESHOLD, CIRCLE_AREA_MIN/MAX, CIRCULARITY_MIN)
- Sheet generation (A4 dimensions, margins, typography)
- AI model settings (VISION_MODEL, CONFIDENCE_THRESHOLD)

Environment-specific configs: DevelopmentConfig, TestingConfig (in-memory SQLite), ProductionConfig.

## Conventions

- Python snake_case throughout
- Python `logging` module (no print statements)
- Custom exceptions in `app/errors.py` with HTTP status codes
- All models have `to_dict()` for JSON serialization
- Tests use pytest fixtures from `tests/conftest.py` (app, db, client)
