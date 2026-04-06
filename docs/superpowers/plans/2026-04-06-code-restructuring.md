# SmartGrader Code Restructuring -- Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the flat SmartGrader codebase into a clean, layered Flask application with SQLAlchemy ORM, consolidated scanner, configuration system, logging, error handling, and tests.

**Architecture:** Flask app factory pattern with blueprints. Four layers: routes (HTTP), services (business logic), models (ORM), scanner (image processing). All hardcoded values move to config. Old PyQt5 files archived in `legacy/` for reference.

**Tech Stack:** Python 3.10+, Flask, SQLAlchemy, Flask-Migrate, OpenCV, NumPy, pdfkit, pytest

---

## File Map

### New files to create:
```
app/__init__.py                    # Flask app factory
app/config.py                      # All configuration constants
app/errors.py                      # Custom exception classes
app/logging_config.py              # Logging setup
app/models/__init__.py             # DB instance + model imports
app/models/exam.py                 # Exam, Question, Choice models
app/models/student.py              # Student, StudentAnswer models
app/models/result.py               # Result model
app/services/__init__.py           # Empty init
app/services/exam_service.py       # Exam CRUD operations
app/services/grading_service.py    # Grading logic
app/services/sheet_generator.py    # QCM sheet HTML/PDF generation
app/services/scanner_service.py    # Scanning orchestration
app/scanner/__init__.py            # Empty init
app/scanner/preprocessor.py        # Image preprocessing pipeline
app/scanner/detector.py            # Unified bubble detector
app/scanner/marker_finder.py       # Triangle/marker detection
app/scanner/grid_mapper.py         # Bubble → question grid mapping
app/scanner/answer_reader.py       # Read filled answers
app/routes/__init__.py             # Blueprint registration
app/routes/exams.py                # /api/exams/* endpoints
app/routes/questions.py            # /api/questions/* endpoints
app/routes/students.py             # /api/students/* endpoints
app/routes/scanning.py             # /api/scan/* endpoints
app/routes/grading.py              # /api/grade/* endpoints
app/templates/qcm_template.html    # Moved from root
tests/__init__.py                  # Empty init
tests/conftest.py                  # Shared fixtures
tests/test_models/__init__.py
tests/test_models/test_exam.py     # Exam model tests
tests/test_models/test_student.py  # Student model tests
tests/test_services/__init__.py
tests/test_services/test_exam_service.py
tests/test_services/test_grading_service.py
tests/test_scanner/__init__.py
tests/test_scanner/test_preprocessor.py
tests/test_scanner/test_detector.py
tests/test_routes/__init__.py
tests/test_routes/test_exams.py
scripts/init_db.py                 # Database initialization
scripts/seed_data.py               # Sample data for development
scripts/migrate_data.py            # Migrate old SQLite data to new schema
run.py                             # Entry point: python run.py
requirements.txt                   # Pinned dependencies
.gitignore                         # Git ignores
CHANGELOG.md                       # Version history
TODO.md                            # Tracked TODOs
```

### Files to archive (move to `legacy/`):
```
main.py → legacy/main.py
exam_form.py → legacy/exam_form.py
question_form.py → legacy/question_form.py
database.py → legacy/database.py
database_init.py → legacy/database_init.py
scanner.py → legacy/scanner.py
exam_scanner.py → legacy/exam_scanner.py
circle_detection.py → legacy/circle_detection.py
circle_detector.py → legacy/circle_detector.py
robust_detection.py → legacy/robust_detection.py
section_detector.py → legacy/section_detector.py
section_circle_detector.py → legacy/section_circle_detector.py
single_column_scanner.py → legacy/single_column_scanner.py
preprocessing.py → legacy/preprocessing.py
auto_screenshot.py → legacy/auto_screenshot.py
view_tables.py → legacy/view_tables.py
generate_qcm_sheet.py → legacy/generate_qcm_sheet.py
```

---

## Task 1: Project Scaffolding & Tooling

**Files:**
- Create: `requirements.txt`, `.gitignore`, `CHANGELOG.md`, `TODO.md`, `run.py`
- Create: all `__init__.py` files for package structure
- Move: old files to `legacy/`

- [ ] **Step 1: Initialize git repository**

```bash
cd C:\Users\pc\Desktop\SmartGrader_APP_WithPDF
git init
```

- [ ] **Step 2: Create `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
*.egg

# Virtual environment
venv/
.venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Database
*.db
instance/

# Generated files
*.pdf
*.jpg
*.jpeg
*.png
debug_output/
scanned_result.*

# OS
.DS_Store
Thumbs.db

# Environment
.env
.flaskenv

# Migrations
migrations/versions/*.pyc
```

- [ ] **Step 3: Create `requirements.txt`**

```
Flask==3.1.1
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.1.0
Flask-CORS==5.0.1
SQLAlchemy==2.0.40
alembic==1.15.2
opencv-python==4.11.0.86
numpy==2.2.4
Pillow==11.2.1
pdfkit==1.0.0
PyMuPDF==1.25.5
qrcode==8.0
pyzbar==0.1.9
pytest==8.3.5
pytest-cov==6.1.1
```

- [ ] **Step 4: Create `CHANGELOG.md`**

```markdown
# Changelog

All notable changes to SmartGrader will be documented in this file.

## [0.2.0] - 2026-04-06

### Changed
- Restructured project from flat layout to layered Flask architecture
- Migrated database layer from raw sqlite3 to SQLAlchemy ORM
- Consolidated 6 scanner files into 5 focused modules
- Replaced print statements with Python logging
- Moved all hardcoded values to centralized configuration

### Added
- Flask app factory with blueprint-based routing
- Flask-Migrate for database schema migrations
- Custom exception classes for scanner and grading errors
- pytest test suite with fixtures
- requirements.txt with pinned dependencies
- .gitignore for clean repository
- CHANGELOG.md and TODO.md for project tracking

### Archived
- Legacy PyQt5 UI code moved to `legacy/` directory

## [0.1.0] - 2026-01-01

### Added
- Initial PyQt5 desktop application
- SQLite database with exam, question, choice, student, result tables
- QCM answer sheet generation (HTML + PDF via pdfkit)
- Bubble detection and automatic MCQ grading via OpenCV
- Multiple detection algorithms (Hough, contour, template matching)
```

- [ ] **Step 5: Create `TODO.md`**

```markdown
# TODO

## Sub-Project 1: Code Restructuring (Current)
- [x] Project scaffolding and tooling
- [ ] Configuration system
- [ ] Custom exceptions and logging
- [ ] SQLAlchemy models
- [ ] Database migration from legacy
- [ ] Exam service layer
- [ ] Grading service layer
- [ ] Scanner consolidation
- [ ] Sheet generator service
- [ ] Flask routes (API)
- [ ] Test suite
- [ ] Entry point and smoke test

## Sub-Project 2: Web UI
- [ ] Flask backend with blueprints
- [ ] React frontend scaffold
- [ ] Dashboard page
- [ ] Exam management pages
- [ ] Scanner upload page
- [ ] Results and statistics pages

## Sub-Project 3: AI Vision Model
- [ ] Model loader (Qwen2.5-VL-3B with 4-bit quantization)
- [ ] OCR pipeline for handwriting extraction
- [ ] Answer evaluator with prompt templates
- [ ] RAG feedback loop with ai_corrections table
- [ ] Confidence threshold and teacher review flow

## Sub-Project 4: Academic Documentation
- [ ] Chapter 1: General Introduction
- [ ] Chapter 2: State of the Art
- [ ] Chapter 3: Analysis & Design (UML diagrams)
- [ ] Chapter 4: Implementation
- [ ] Chapter 5: Testing & Results
- [ ] Chapter 6: Conclusion & Perspectives
```

- [ ] **Step 6: Create directory structure**

```bash
mkdir -p app/models app/services app/scanner app/routes app/ai app/templates
mkdir -p tests/test_models tests/test_services tests/test_scanner tests/test_routes
mkdir -p scripts legacy instance docs/chapters docs/figures
```

- [ ] **Step 7: Create empty `__init__.py` files**

Create each with a single docstring:

`app/__init__.py`:
```python
"""SmartGrader Flask application."""
```

`app/models/__init__.py`:
```python
"""SQLAlchemy models for SmartGrader."""
```

`app/services/__init__.py`:
```python
"""Business logic services."""
```

`app/scanner/__init__.py`:
```python
"""Image processing and bubble detection modules."""
```

`app/routes/__init__.py`:
```python
"""Flask API route blueprints."""
```

`app/ai/__init__.py`:
```python
"""AI vision model integration (Sub-Project 3)."""
```

`tests/__init__.py`, `tests/test_models/__init__.py`, `tests/test_services/__init__.py`, `tests/test_scanner/__init__.py`, `tests/test_routes/__init__.py`:
```python
```

- [ ] **Step 8: Move legacy files**

```bash
mv main.py legacy/
mv exam_form.py legacy/
mv question_form.py legacy/
mv question_form.py legacy/
mv database.py legacy/
mv database_init.py legacy/
mv scanner.py legacy/
mv exam_scanner.py legacy/
mv circle_detection.py legacy/
mv circle_detector.py legacy/
mv robust_detection.py legacy/
mv section_detector.py legacy/
mv section_circle_detector.py legacy/
mv single_column_scanner.py legacy/
mv preprocessing.py legacy/
mv auto_screenshot.py legacy/
mv view_tables.py legacy/
mv generate_qcm_sheet.py legacy/
```

- [ ] **Step 9: Move template**

```bash
cp qcm_template.html app/templates/qcm_template.html
mv qcm_template.html legacy/
```

- [ ] **Step 10: Commit**

```bash
git add .gitignore requirements.txt CHANGELOG.md TODO.md
git add app/ tests/ scripts/ legacy/ docs/
git commit -m "chore: restructure project layout, archive legacy code"
```

---

## Task 2: Configuration System

**Files:**
- Create: `app/config.py`

- [ ] **Step 1: Write the config module**

```python
"""Centralized configuration for SmartGrader."""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "smart_grader.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Sheet generation (A4 dimensions in mm)
    PAGE_HEIGHT_MM = 297
    PAGE_WIDTH_MM = 210
    MARGIN_MM = {"top": 8, "bottom": 8, "left": 12, "right": 12}
    HEADER_HEIGHT_MM = 28
    MINIMAL_HEADER_HEIGHT_MM = 10
    STUDENT_SECTION_HEIGHT_MM = 36
    INSTRUCTION_HEIGHT_MM = 8
    PAGE_NUMBER_HEIGHT_MM = 6
    GRID_GAP_MM = 2
    LINE_HEIGHT_MM = 4.3
    OPTION_SPACING_MM = 1.2
    QUESTION_BOTTOM_MM = 3.5
    MIN_QUESTION_HEIGHT_MM = 10
    CHARS_PER_LINE = 62
    HEIGHT_SAFETY_BUFFER_MM = 4

    # Scanner thresholds
    FILL_THRESHOLD = 50
    CIRCLE_AREA_MIN = 60
    CIRCLE_AREA_MAX = 600
    CIRCULARITY_MIN = 0.65
    ASPECT_RATIO_MIN = 0.6
    ASPECT_RATIO_MAX = 1.5
    RADIUS_MIN = 6
    RADIUS_MAX = 25
    DUPLICATE_DISTANCE = 10
    OUTLIER_MAX_DEVIATION = 50

    # Column detection (as fraction of image width)
    LEFT_COL_MIN = 0.08
    LEFT_COL_MAX = 0.25
    RIGHT_COL_MIN = 0.45
    RIGHT_COL_MAX = 0.75

    # PDF generation
    PDF_DPI = 300
    PDFKIT_OPTIONS = {
        "page-size": "A4",
        "margin-top": "0mm",
        "margin-right": "0mm",
        "margin-bottom": "0mm",
        "margin-left": "0mm",
        "encoding": "UTF-8",
        "enable-local-file-access": "",
    }

    # Smart grading features
    SMART_GRADING_ENABLED = True
    GENERATE_ANSWER_KEY = True
    INCLUDE_OMR_MARKERS = True

    # AI model (Sub-Project 3 -- placeholders)
    VISION_MODEL = "Qwen/Qwen2.5-VL-3B-Instruct"
    MODEL_DEVICE = "cuda"
    MAX_TOKENS = 512
    CONFIDENCE_THRESHOLD = 0.7

    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "tiff", "bmp"}

    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = os.path.join(BASE_DIR, "logs", "smartgrader.log")


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    LOG_LEVEL = "WARNING"


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = "WARNING"


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
```

- [ ] **Step 2: Commit**

```bash
git add app/config.py
git commit -m "feat: add centralized configuration system"
```

---

## Task 3: Custom Exceptions and Logging

**Files:**
- Create: `app/errors.py`, `app/logging_config.py`

- [ ] **Step 1: Write custom exceptions**

`app/errors.py`:
```python
"""Custom exception classes for SmartGrader."""


class SmartGraderError(Exception):
    """Base exception for all SmartGrader errors."""

    def __init__(self, message="An error occurred", status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ScannerError(SmartGraderError):
    """Raised when image scanning fails."""

    def __init__(self, message="Scanner error"):
        super().__init__(message, status_code=422)


class DetectionError(ScannerError):
    """Raised when bubble/marker detection fails."""

    def __init__(self, message="Detection failed"):
        super().__init__(message)


class GradingError(SmartGraderError):
    """Raised when grading logic fails."""

    def __init__(self, message="Grading error"):
        super().__init__(message, status_code=422)


class SheetGenerationError(SmartGraderError):
    """Raised when answer sheet generation fails."""

    def __init__(self, message="Sheet generation failed"):
        super().__init__(message, status_code=500)


class NotFoundError(SmartGraderError):
    """Raised when a resource is not found."""

    def __init__(self, resource="Resource", resource_id=None):
        msg = f"{resource} not found"
        if resource_id is not None:
            msg = f"{resource} with id {resource_id} not found"
        super().__init__(msg, status_code=404)
```

- [ ] **Step 2: Write logging configuration**

`app/logging_config.py`:
```python
"""Logging configuration for SmartGrader."""

import logging
import os


def setup_logging(log_level="INFO", log_file=None):
    """Configure application-wide logging.

    Args:
        log_level: Logging level string (DEBUG, INFO, WARNING, ERROR).
        log_file: Path to log file. If None, logs to console only.
    """
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger("smartgrader")
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger
```

- [ ] **Step 3: Commit**

```bash
git add app/errors.py app/logging_config.py
git commit -m "feat: add custom exceptions and logging configuration"
```

---

## Task 4: SQLAlchemy Models

**Files:**
- Create: `app/models/__init__.py` (update), `app/models/exam.py`, `app/models/student.py`, `app/models/result.py`
- Test: `tests/test_models/test_exam.py`, `tests/test_models/test_student.py`

- [ ] **Step 1: Write the model init with db instance**

`app/models/__init__.py`:
```python
"""SQLAlchemy models for SmartGrader."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.exam import Exam, Question, Choice  # noqa: E402, F401
from app.models.student import Student, StudentAnswer  # noqa: E402, F401
from app.models.result import Result  # noqa: E402, F401
```

- [ ] **Step 2: Write the Exam models**

`app/models/exam.py`:
```python
"""Exam, Question, and Choice models."""

from app.models import db


class Exam(db.Model):
    __tablename__ = "exams"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100))
    date = db.Column(db.String(20))
    total_marks = db.Column(db.Float)

    questions = db.relationship(
        "Question", backref="exam", cascade="all, delete-orphan", lazy="dynamic"
    )
    results = db.relationship(
        "Result", backref="exam", cascade="all, delete-orphan", lazy="dynamic"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "subject": self.subject,
            "date": self.date,
            "total_marks": self.total_marks,
        }


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_choices_number = db.Column(db.Integer, nullable=False)
    marks = db.Column(db.Float, nullable=False)

    choices = db.relationship(
        "Choice", backref="question", cascade="all, delete-orphan", lazy="dynamic"
    )
    answers = db.relationship(
        "StudentAnswer", backref="question", cascade="all, delete-orphan", lazy="dynamic"
    )

    def to_dict(self, include_choices=False):
        data = {
            "id": self.id,
            "exam_id": self.exam_id,
            "question_text": self.question_text,
            "choices_number": self.question_choices_number,
            "marks": self.marks,
        }
        if include_choices:
            data["choices"] = [c.to_dict() for c in self.choices.order_by(Choice.choice_label)]
        return data


class Choice(db.Model):
    __tablename__ = "choices"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    choice_label = db.Column(db.String(5), nullable=False)
    choice_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.choice_label,
            "text": self.choice_text,
            "is_correct": bool(self.is_correct),
        }
```

- [ ] **Step 3: Write the Student models**

`app/models/student.py`:
```python
"""Student and StudentAnswer models."""

from app.models import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    matricule = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(200))

    answers = db.relationship(
        "StudentAnswer", backref="student", cascade="all, delete-orphan", lazy="dynamic"
    )
    results = db.relationship(
        "Result", backref="student", cascade="all, delete-orphan", lazy="dynamic"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "matricule": self.matricule,
            "email": self.email,
        }


class StudentAnswer(db.Model):
    __tablename__ = "student_answers"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    selected_choice_id = db.Column(db.Integer, db.ForeignKey("choices.id"))

    selected_choice = db.relationship("Choice", foreign_keys=[selected_choice_id])

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "question_id": self.question_id,
            "selected_choice_id": self.selected_choice_id,
        }
```

- [ ] **Step 4: Write the Result model**

`app/models/result.py`:
```python
"""Result model for exam scores."""

from app.models import db


class Result(db.Model):
    __tablename__ = "results"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False)
    score = db.Column(db.Float, nullable=False)
    percentage = db.Column(db.Float)
    graded_at = db.Column(db.String(30))

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "exam_id": self.exam_id,
            "score": self.score,
            "percentage": self.percentage,
            "graded_at": self.graded_at,
            "student_name": self.student.name if self.student else None,
            "exam_title": self.exam.title if self.exam else None,
        }
```

- [ ] **Step 5: Write model tests**

`tests/conftest.py`:
```python
"""Shared test fixtures."""

import pytest
from app import create_app
from app.models import db as _db


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def db(app):
    """Provide database session."""
    with app.app_context():
        yield _db


@pytest.fixture
def client(app):
    """Provide Flask test client."""
    return app.test_client()
```

`tests/test_models/test_exam.py`:
```python
"""Tests for Exam, Question, Choice models."""

from app.models.exam import Exam, Question, Choice


def test_create_exam(db):
    exam = Exam(title="Math Final", subject="Mathematics", total_marks=100)
    db.session.add(exam)
    db.session.commit()

    assert exam.id is not None
    assert exam.title == "Math Final"


def test_exam_to_dict(db):
    exam = Exam(title="Physics", subject="Science", date="2026-04-06", total_marks=50)
    db.session.add(exam)
    db.session.commit()

    data = exam.to_dict()
    assert data["title"] == "Physics"
    assert data["total_marks"] == 50


def test_exam_question_relationship(db):
    exam = Exam(title="Test", subject="Test")
    db.session.add(exam)
    db.session.commit()

    q = Question(exam_id=exam.id, question_text="What is 2+2?", question_choices_number=4, marks=5)
    db.session.add(q)
    db.session.commit()

    assert exam.questions.count() == 1
    assert q.exam.title == "Test"


def test_question_choice_relationship(db):
    exam = Exam(title="Test", subject="Test")
    db.session.add(exam)
    db.session.commit()

    q = Question(exam_id=exam.id, question_text="Q1", question_choices_number=2, marks=1)
    db.session.add(q)
    db.session.commit()

    c1 = Choice(question_id=q.id, choice_label="A", choice_text="Yes", is_correct=1)
    c2 = Choice(question_id=q.id, choice_label="B", choice_text="No", is_correct=0)
    db.session.add_all([c1, c2])
    db.session.commit()

    assert q.choices.count() == 2
    assert c1.to_dict()["is_correct"] is True


def test_cascade_delete(db):
    exam = Exam(title="Delete Me", subject="Test")
    db.session.add(exam)
    db.session.commit()

    q = Question(exam_id=exam.id, question_text="Q1", question_choices_number=2, marks=1)
    db.session.add(q)
    db.session.commit()

    Choice(question_id=q.id, choice_label="A", choice_text="A", is_correct=0)
    db.session.commit()

    db.session.delete(exam)
    db.session.commit()

    assert Question.query.count() == 0
    assert Choice.query.count() == 0
```

`tests/test_models/test_student.py`:
```python
"""Tests for Student and StudentAnswer models."""

from app.models.student import Student, StudentAnswer
from app.models.exam import Exam, Question, Choice


def test_create_student(db):
    s = Student(name="Ahmed", matricule="2026001", email="ahmed@univ.dz")
    db.session.add(s)
    db.session.commit()

    assert s.id is not None
    assert s.matricule == "2026001"


def test_student_unique_matricule(db):
    import sqlalchemy
    s1 = Student(name="A", matricule="001")
    s2 = Student(name="B", matricule="001")
    db.session.add(s1)
    db.session.commit()

    db.session.add(s2)
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db.session.commit()


def test_student_answer(db):
    exam = Exam(title="E", subject="S")
    db.session.add(exam)
    db.session.commit()

    q = Question(exam_id=exam.id, question_text="Q", question_choices_number=2, marks=1)
    db.session.add(q)
    db.session.commit()

    c = Choice(question_id=q.id, choice_label="A", choice_text="A", is_correct=1)
    db.session.add(c)
    db.session.commit()

    s = Student(name="X", matricule="100")
    db.session.add(s)
    db.session.commit()

    sa = StudentAnswer(student_id=s.id, question_id=q.id, selected_choice_id=c.id)
    db.session.add(sa)
    db.session.commit()

    assert sa.selected_choice.is_correct == 1


# Need pytest import for raises
import pytest
```

- [ ] **Step 6: Commit**

```bash
git add app/models/ tests/conftest.py tests/test_models/
git commit -m "feat: add SQLAlchemy models with relationships and tests"
```

---

## Task 5: Flask App Factory

**Files:**
- Create: `app/__init__.py` (update), `run.py`

- [ ] **Step 1: Write the app factory**

`app/__init__.py`:
```python
"""SmartGrader Flask application."""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from app.config import config_by_name
from app.models import db
from app.logging_config import setup_logging
from app.errors import SmartGraderError

migrate = Migrate()
logger = logging.getLogger("smartgrader")


def create_app(config_name=None):
    """Application factory.

    Args:
        config_name: One of 'development', 'testing', 'production'.
                     Defaults to FLASK_ENV or 'development'.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name[config_name])

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Setup logging
    setup_logging(
        log_level=app.config.get("LOG_LEVEL", "INFO"),
        log_file=app.config.get("LOG_FILE"),
    )

    # Register error handlers
    @app.errorhandler(SmartGraderError)
    def handle_smartgrader_error(error):
        return jsonify({"error": error.message}), error.status_code

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def handle_500(error):
        logger.exception("Internal server error")
        return jsonify({"error": "Internal server error"}), 500

    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    # Health check
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "version": "0.2.0"})

    logger.info("SmartGrader app created [%s]", config_name)
    return app
```

- [ ] **Step 2: Update routes init to register blueprints**

`app/routes/__init__.py`:
```python
"""Flask API route blueprints."""


def register_blueprints(app):
    """Register all route blueprints with the Flask app."""
    from app.routes.exams import exams_bp
    from app.routes.questions import questions_bp
    from app.routes.students import students_bp
    from app.routes.scanning import scanning_bp
    from app.routes.grading import grading_bp

    app.register_blueprint(exams_bp, url_prefix="/api")
    app.register_blueprint(questions_bp, url_prefix="/api")
    app.register_blueprint(students_bp, url_prefix="/api")
    app.register_blueprint(scanning_bp, url_prefix="/api")
    app.register_blueprint(grading_bp, url_prefix="/api")
```

- [ ] **Step 3: Create stub blueprints (so imports work)**

`app/routes/exams.py`:
```python
"""Exam API endpoints."""

from flask import Blueprint

exams_bp = Blueprint("exams", __name__)
```

`app/routes/questions.py`:
```python
"""Question API endpoints."""

from flask import Blueprint

questions_bp = Blueprint("questions", __name__)
```

`app/routes/students.py`:
```python
"""Student API endpoints."""

from flask import Blueprint

students_bp = Blueprint("students", __name__)
```

`app/routes/scanning.py`:
```python
"""Scanning API endpoints."""

from flask import Blueprint

scanning_bp = Blueprint("scanning", __name__)
```

`app/routes/grading.py`:
```python
"""Grading API endpoints."""

from flask import Blueprint

grading_bp = Blueprint("grading", __name__)
```

- [ ] **Step 4: Write `run.py`**

```python
"""Entry point for SmartGrader application."""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

- [ ] **Step 5: Run test to verify app creates**

```bash
cd C:\Users\pc\Desktop\SmartGrader_APP_WithPDF
pytest tests/test_models/test_exam.py -v
```

Expected: All tests pass (5 tests).

- [ ] **Step 6: Commit**

```bash
git add app/__init__.py app/routes/ run.py
git commit -m "feat: add Flask app factory with blueprint registration"
```

---

## Task 6: Exam Service Layer

**Files:**
- Create: `app/services/exam_service.py`
- Test: `tests/test_services/test_exam_service.py`

- [ ] **Step 1: Write the failing test**

`tests/test_services/test_exam_service.py`:
```python
"""Tests for exam service CRUD operations."""

from app.services.exam_service import (
    create_exam,
    get_all_exams,
    get_exam_by_id,
    update_exam,
    delete_exam,
    create_question_with_choices,
    get_questions_for_exam,
    get_exam_statistics,
)


def test_create_exam(db):
    exam = create_exam(title="Math", subject="Science", total_marks=100)
    assert exam.id is not None
    assert exam.title == "Math"


def test_get_all_exams(db):
    create_exam(title="A", subject="S")
    create_exam(title="B", subject="S")
    exams = get_all_exams()
    assert len(exams) == 2


def test_get_exam_by_id(db):
    exam = create_exam(title="Find Me", subject="Test")
    found = get_exam_by_id(exam.id)
    assert found.title == "Find Me"


def test_get_exam_not_found(db):
    from app.errors import NotFoundError
    import pytest
    with pytest.raises(NotFoundError):
        get_exam_by_id(999)


def test_update_exam(db):
    exam = create_exam(title="Old", subject="S")
    updated = update_exam(exam.id, title="New")
    assert updated.title == "New"


def test_delete_exam(db):
    exam = create_exam(title="Delete", subject="S")
    delete_exam(exam.id)
    from app.models.exam import Exam
    assert Exam.query.count() == 0


def test_create_question_with_choices(db):
    exam = create_exam(title="E", subject="S")
    question = create_question_with_choices(
        exam_id=exam.id,
        question_text="What is 1+1?",
        marks=5,
        choices=[
            {"label": "A", "text": "1", "is_correct": False},
            {"label": "B", "text": "2", "is_correct": True},
            {"label": "C", "text": "3", "is_correct": False},
        ],
    )
    assert question.id is not None
    assert question.choices.count() == 3
    assert question.question_choices_number == 3


def test_get_questions_for_exam(db):
    exam = create_exam(title="E", subject="S")
    create_question_with_choices(
        exam_id=exam.id,
        question_text="Q1",
        marks=1,
        choices=[{"label": "A", "text": "A", "is_correct": True}],
    )
    questions = get_questions_for_exam(exam.id)
    assert len(questions) == 1
    assert questions[0]["choices"][0]["is_correct"] is True


def test_get_exam_statistics(db):
    exam = create_exam(title="E", subject="S")
    create_question_with_choices(
        exam_id=exam.id,
        question_text="Q1",
        marks=10,
        choices=[{"label": "A", "text": "A", "is_correct": True}],
    )
    create_question_with_choices(
        exam_id=exam.id,
        question_text="Q2",
        marks=20,
        choices=[{"label": "A", "text": "A", "is_correct": True}],
    )
    stats = get_exam_statistics(exam.id)
    assert stats["question_count"] == 2
    assert stats["total_marks"] == 30
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_services/test_exam_service.py -v
```

Expected: FAIL -- module not found.

- [ ] **Step 3: Write the implementation**

`app/services/exam_service.py`:
```python
"""Exam CRUD service layer."""

import logging
from app.models import db
from app.models.exam import Exam, Question, Choice
from app.errors import NotFoundError

logger = logging.getLogger("smartgrader.services.exam")


def create_exam(title, subject=None, date=None, total_marks=None):
    """Create a new exam."""
    exam = Exam(title=title, subject=subject, date=date, total_marks=total_marks)
    db.session.add(exam)
    db.session.commit()
    logger.info("Created exam %d: %s", exam.id, title)
    return exam


def get_all_exams():
    """Return all exams ordered by id descending."""
    return Exam.query.order_by(Exam.id.desc()).all()


def get_exam_by_id(exam_id):
    """Return exam by id or raise NotFoundError."""
    exam = Exam.query.get(exam_id)
    if exam is None:
        raise NotFoundError("Exam", exam_id)
    return exam


def update_exam(exam_id, **kwargs):
    """Update exam fields. Only updates provided non-None values."""
    exam = get_exam_by_id(exam_id)
    for key, value in kwargs.items():
        if value is not None and hasattr(exam, key):
            setattr(exam, key, value)
    db.session.commit()
    logger.info("Updated exam %d", exam_id)
    return exam


def delete_exam(exam_id):
    """Delete exam and all related data (cascade)."""
    exam = get_exam_by_id(exam_id)
    db.session.delete(exam)
    db.session.commit()
    logger.info("Deleted exam %d", exam_id)


def create_question_with_choices(exam_id, question_text, marks, choices):
    """Create a question with its choices in one transaction.

    Args:
        exam_id: ID of the parent exam.
        question_text: The question text.
        marks: Points for this question.
        choices: List of dicts with keys: label, text, is_correct.
    """
    get_exam_by_id(exam_id)  # Validate exam exists

    question = Question(
        exam_id=exam_id,
        question_text=question_text,
        question_choices_number=len(choices),
        marks=marks,
    )
    db.session.add(question)
    db.session.flush()  # Get question.id before adding choices

    for choice_data in choices:
        choice = Choice(
            question_id=question.id,
            choice_label=choice_data["label"],
            choice_text=choice_data["text"],
            is_correct=int(choice_data.get("is_correct", False)),
        )
        db.session.add(choice)

    db.session.commit()
    logger.info("Created question %d for exam %d with %d choices", question.id, exam_id, len(choices))
    return question


def get_questions_for_exam(exam_id):
    """Return all questions with choices for an exam."""
    get_exam_by_id(exam_id)  # Validate exam exists
    questions = Question.query.filter_by(exam_id=exam_id).order_by(Question.id).all()
    return [q.to_dict(include_choices=True) for q in questions]


def get_exam_statistics(exam_id):
    """Return statistics about an exam."""
    exam = get_exam_by_id(exam_id)
    questions = exam.questions.all()

    question_count = len(questions)
    total_marks = sum(q.marks for q in questions) if questions else 0
    avg_marks = total_marks / question_count if question_count > 0 else 0

    results = exam.results.all()
    student_count = len(results)
    avg_score = sum(r.percentage for r in results) / student_count if student_count > 0 else 0

    return {
        "question_count": question_count,
        "total_marks": total_marks,
        "average_marks": round(avg_marks, 2),
        "student_count": student_count,
        "average_score": round(avg_score, 2),
    }
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_services/test_exam_service.py -v
```

Expected: All 9 tests pass.

- [ ] **Step 5: Commit**

```bash
git add app/services/exam_service.py tests/test_services/test_exam_service.py
git commit -m "feat: add exam service with CRUD operations and tests"
```

---

## Task 7: Grading Service Layer

**Files:**
- Create: `app/services/grading_service.py`
- Test: `tests/test_services/test_grading_service.py`

- [ ] **Step 1: Write the failing test**

`tests/test_services/test_grading_service.py`:
```python
"""Tests for grading service."""

from app.services.exam_service import create_exam, create_question_with_choices
from app.services.grading_service import grade_mcq_answers, save_result, get_results_for_exam
from app.models.student import Student
from app.models import db


def _create_exam_with_questions(db_session):
    """Helper: create exam with 2 questions."""
    exam = create_exam(title="Grading Test", subject="Math", total_marks=10)
    create_question_with_choices(
        exam_id=exam.id, question_text="2+2?", marks=5,
        choices=[
            {"label": "A", "text": "3", "is_correct": False},
            {"label": "B", "text": "4", "is_correct": True},
        ],
    )
    create_question_with_choices(
        exam_id=exam.id, question_text="3+3?", marks=5,
        choices=[
            {"label": "A", "text": "6", "is_correct": True},
            {"label": "B", "text": "7", "is_correct": False},
        ],
    )
    return exam


def test_grade_all_correct(db):
    exam = _create_exam_with_questions(db)
    questions = exam.questions.order_by("id").all()

    # Detected answers: question_id -> choice_label
    detected = {
        questions[0].id: "B",  # correct
        questions[1].id: "A",  # correct
    }
    result = grade_mcq_answers(exam.id, detected)
    assert result["obtained_marks"] == 10
    assert result["percentage"] == 100.0


def test_grade_one_wrong(db):
    exam = _create_exam_with_questions(db)
    questions = exam.questions.order_by("id").all()

    detected = {
        questions[0].id: "A",  # wrong
        questions[1].id: "A",  # correct
    }
    result = grade_mcq_answers(exam.id, detected)
    assert result["obtained_marks"] == 5
    assert result["percentage"] == 50.0


def test_grade_unanswered(db):
    exam = _create_exam_with_questions(db)
    questions = exam.questions.order_by("id").all()

    detected = {
        questions[0].id: "B",  # correct
        # question 2 not answered
    }
    result = grade_mcq_answers(exam.id, detected)
    assert result["obtained_marks"] == 5


def test_save_and_get_results(db):
    exam = _create_exam_with_questions(db)
    student = Student(name="Test", matricule="001")
    db.session.add(student)
    db.session.commit()

    save_result(student.id, exam.id, score=8, percentage=80.0)
    results = get_results_for_exam(exam.id)
    assert len(results) == 1
    assert results[0]["score"] == 8
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/test_services/test_grading_service.py -v
```

Expected: FAIL -- module not found.

- [ ] **Step 3: Write the implementation**

`app/services/grading_service.py`:
```python
"""Grading service for MCQ answer evaluation."""

import logging
from datetime import datetime
from app.models import db
from app.models.exam import Question, Choice
from app.models.result import Result
from app.services.exam_service import get_exam_by_id
from app.errors import GradingError

logger = logging.getLogger("smartgrader.services.grading")


def grade_mcq_answers(exam_id, detected_answers):
    """Grade detected MCQ answers against correct answers.

    Args:
        exam_id: The exam to grade.
        detected_answers: Dict mapping question_id -> detected choice label (e.g. "A", "B").

    Returns:
        Dict with grading results: obtained_marks, total_marks, percentage, details.
    """
    exam = get_exam_by_id(exam_id)
    questions = exam.questions.order_by(Question.id).all()

    if not questions:
        raise GradingError(f"Exam {exam_id} has no questions")

    total_marks = 0
    obtained_marks = 0
    details = []

    for question in questions:
        total_marks += question.marks

        correct_choice = question.choices.filter_by(is_correct=1).first()
        correct_label = correct_choice.choice_label.upper() if correct_choice else None

        detected_label = detected_answers.get(question.id)
        if detected_label:
            detected_label = detected_label.upper()

        is_correct = detected_label == correct_label if detected_label and correct_label else False
        if is_correct:
            obtained_marks += question.marks

        details.append({
            "question_id": question.id,
            "detected": detected_label,
            "correct": correct_label,
            "is_correct": is_correct,
            "marks": question.marks,
        })

    percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0

    logger.info(
        "Graded exam %d: %s/%s (%.1f%%)",
        exam_id, obtained_marks, total_marks, percentage,
    )

    return {
        "exam_id": exam_id,
        "total_marks": total_marks,
        "obtained_marks": obtained_marks,
        "percentage": round(percentage, 1),
        "answered": sum(1 for d in details if d["detected"]),
        "total_questions": len(questions),
        "details": details,
    }


def save_result(student_id, exam_id, score, percentage):
    """Save or update a grading result."""
    existing = Result.query.filter_by(student_id=student_id, exam_id=exam_id).first()

    if existing:
        existing.score = score
        existing.percentage = percentage
        existing.graded_at = datetime.utcnow().isoformat()
    else:
        result = Result(
            student_id=student_id,
            exam_id=exam_id,
            score=score,
            percentage=percentage,
            graded_at=datetime.utcnow().isoformat(),
        )
        db.session.add(result)

    db.session.commit()
    logger.info("Saved result for student %d, exam %d: %.1f%%", student_id, exam_id, percentage)


def get_results_for_exam(exam_id):
    """Get all results for an exam."""
    results = (
        Result.query
        .filter_by(exam_id=exam_id)
        .order_by(Result.percentage.desc())
        .all()
    )
    return [r.to_dict() for r in results]
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_services/test_grading_service.py -v
```

Expected: All 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add app/services/grading_service.py tests/test_services/test_grading_service.py
git commit -m "feat: add grading service with MCQ evaluation and tests"
```

---

## Task 8: Scanner Consolidation -- Preprocessor

**Files:**
- Create: `app/scanner/preprocessor.py`
- Test: `tests/test_scanner/test_preprocessor.py`

- [ ] **Step 1: Write the failing test**

`tests/test_scanner/test_preprocessor.py`:
```python
"""Tests for image preprocessor."""

import numpy as np
import pytest
from app.scanner.preprocessor import ImagePreprocessor


def _make_test_image(width=800, height=1000):
    """Create a synthetic test image (white with black rectangles)."""
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    # Draw some black shapes to simulate content
    img[100:150, 100:700] = 0   # horizontal line
    img[200:250, 100:700] = 0   # another line
    return img


def test_preprocessor_init():
    preprocessor = ImagePreprocessor()
    assert preprocessor.original is None


def test_load_from_array():
    img = _make_test_image()
    preprocessor = ImagePreprocessor()
    preprocessor.load_from_array(img)
    assert preprocessor.original is not None
    assert preprocessor.original.shape == (1000, 800, 3)


def test_to_grayscale():
    img = _make_test_image()
    preprocessor = ImagePreprocessor()
    preprocessor.load_from_array(img)
    gray = preprocessor.to_grayscale()
    assert len(gray.shape) == 2  # 2D array


def test_reduce_noise():
    img = _make_test_image()
    preprocessor = ImagePreprocessor()
    preprocessor.load_from_array(img)
    preprocessor.to_grayscale()
    blurred = preprocessor.reduce_noise(kernel_size=5)
    assert blurred.shape == preprocessor.gray.shape


def test_threshold_otsu():
    img = _make_test_image()
    preprocessor = ImagePreprocessor()
    preprocessor.load_from_array(img)
    preprocessor.to_grayscale()
    thresh = preprocessor.threshold(method="otsu")
    assert thresh is not None
    unique_values = np.unique(thresh)
    assert len(unique_values) <= 2  # binary


def test_full_preprocess():
    img = _make_test_image()
    preprocessor = ImagePreprocessor()
    preprocessor.load_from_array(img)
    result = preprocessor.full_preprocess(deskew=False, auto_crop=False)
    assert result is not None
    assert len(result.shape) == 2  # binary output
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/test_scanner/test_preprocessor.py -v
```

Expected: FAIL -- module not found.

- [ ] **Step 3: Write the implementation**

`app/scanner/preprocessor.py`:
```python
"""Image preprocessing pipeline for scanned exam sheets.

Migrated from legacy/preprocessing.py. All print() replaced with logging.
Hardcoded values moved to config or method parameters.
"""

import logging
import cv2
import numpy as np
import os

logger = logging.getLogger("smartgrader.scanner.preprocessor")


class ImagePreprocessor:
    """Preprocesses exam sheet images for bubble detection."""

    def __init__(self):
        self.original = None
        self.gray = None
        self.processed = None
        self.debug_images = {}

    def load_image(self, image_path):
        """Load image from file path."""
        self.original = cv2.imread(image_path)
        if self.original is None:
            raise ValueError(f"Could not load image: {image_path}")
        logger.info("Loaded image: %s (%dx%d)", image_path, self.original.shape[1], self.original.shape[0])
        return self.original

    def load_from_array(self, image_array):
        """Load image from numpy array."""
        self.original = image_array.copy()
        logger.info("Loaded image from array (%dx%d)", self.original.shape[1], self.original.shape[0])
        return self.original

    def to_grayscale(self):
        """Convert image to grayscale."""
        if self.original is None:
            raise ValueError("No image loaded")
        self.gray = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        self.debug_images["grayscale"] = self.gray
        logger.debug("Converted to grayscale")
        return self.gray

    def reduce_noise(self, kernel_size=5):
        """Apply Gaussian blur to reduce noise."""
        if self.gray is None:
            self.to_grayscale()
        self.processed = cv2.GaussianBlur(self.gray, (kernel_size, kernel_size), 0)
        self.debug_images["noise_reduced"] = self.processed
        logger.debug("Noise reduced (kernel=%d)", kernel_size)
        return self.processed

    def enhance_contrast(self):
        """Enhance contrast using CLAHE."""
        if self.gray is None:
            self.to_grayscale()
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        self.processed = clahe.apply(self.gray)
        self.debug_images["contrast_enhanced"] = self.processed
        logger.debug("Contrast enhanced")
        return self.processed

    def threshold(self, method="otsu", block_size=11, c=2):
        """Apply thresholding.

        Args:
            method: One of 'otsu', 'adaptive', 'binary'.
            block_size: Block size for adaptive thresholding.
            c: Constant for adaptive thresholding.
        """
        if self.gray is None:
            self.to_grayscale()

        if method == "otsu":
            _, thresh = cv2.threshold(self.gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        elif method == "adaptive":
            thresh = cv2.adaptiveThreshold(
                self.gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, block_size, c
            )
        elif method == "binary":
            _, thresh = cv2.threshold(self.gray, 127, 255, cv2.THRESH_BINARY_INV)
        else:
            raise ValueError(f"Unknown threshold method: {method}")

        self.processed = thresh
        self.debug_images["threshold"] = self.processed
        logger.debug("Threshold applied (%s)", method)
        return self.processed

    def deskew(self):
        """Detect and correct sheet rotation using Hough line detection."""
        if self.original is None:
            raise ValueError("No image loaded")

        gray = self.gray if self.gray is not None else self.to_grayscale()
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

        if lines is None:
            logger.warning("No lines detected for deskewing")
            return self.original

        angles = []
        for line in lines[:50]:
            _, theta = line[0]
            if np.pi / 4 < theta < 3 * np.pi / 4:
                angles.append(np.degrees(theta) - 90)

        if not angles:
            logger.warning("Could not determine rotation angle")
            return self.original

        median_angle = np.median(angles)
        if abs(median_angle) < 0.5:
            logger.debug("Image is straight (angle: %.2f)", median_angle)
            return self.original

        h, w = self.original.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        deskewed = cv2.warpAffine(
            self.original, rotation_matrix, (w, h),
            flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE,
        )

        self.original = deskewed
        if self.gray is not None:
            self.gray = cv2.cvtColor(deskewed, cv2.COLOR_BGR2GRAY)

        logger.info("Deskewed: rotated %.2f degrees", median_angle)
        self.debug_images["deskewed"] = deskewed
        return deskewed

    def auto_crop(self):
        """Automatically detect and crop the exam area."""
        if self.original is None:
            raise ValueError("No image loaded")

        gray = self.gray if self.gray is not None else self.to_grayscale()
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            logger.warning("No contours found for auto-crop")
            return self.original

        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        img_area = self.original.shape[0] * self.original.shape[1]

        if w * h < img_area * 0.5:
            logger.warning("Detected area too small, keeping original")
            return self.original

        margin = 10
        x = max(0, x - margin)
        y = max(0, y - margin)
        w = min(self.original.shape[1] - x, w + 2 * margin)
        h = min(self.original.shape[0] - y, h + 2 * margin)

        self.original = self.original[y : y + h, x : x + w]
        if self.gray is not None:
            self.gray = self.gray[y : y + h, x : x + w]
        if self.processed is not None:
            self.processed = self.processed[y : y + h, x : x + w]

        logger.info("Auto-cropped: %dx%d at (%d, %d)", w, h, x, y)
        self.debug_images["auto_cropped"] = self.original
        return self.original

    def full_preprocess(self, deskew=True, auto_crop=True):
        """Apply full preprocessing pipeline.

        Pipeline: deskew -> auto_crop -> grayscale -> noise reduction -> contrast -> threshold.
        """
        logger.info("Starting preprocessing pipeline")

        if deskew:
            self.deskew()
        if auto_crop:
            self.auto_crop()

        self.to_grayscale()
        self.reduce_noise(kernel_size=5)
        self.enhance_contrast()
        self.threshold(method="otsu")

        logger.info("Preprocessing complete")
        return self.processed

    def save_debug_images(self, output_dir):
        """Save all intermediate images for inspection."""
        os.makedirs(output_dir, exist_ok=True)
        images = {
            "01_original": self.original,
            "02_grayscale": self.gray,
            "03_processed": self.processed,
        }
        images.update({f"04_{k}": v for k, v in self.debug_images.items()})

        for name, img in images.items():
            if img is not None:
                filepath = os.path.join(output_dir, f"{name}.png")
                cv2.imwrite(filepath, img)
                logger.debug("Saved debug image: %s", filepath)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_scanner/test_preprocessor.py -v
```

Expected: All 6 tests pass.

- [ ] **Step 5: Commit**

```bash
git add app/scanner/preprocessor.py tests/test_scanner/test_preprocessor.py
git commit -m "feat: add image preprocessor with configurable pipeline and tests"
```

---

## Task 9: Scanner Consolidation -- Marker Finder & Detector

**Files:**
- Create: `app/scanner/marker_finder.py`, `app/scanner/detector.py`
- Test: `tests/test_scanner/test_detector.py`

- [ ] **Step 1: Write the marker finder**

`app/scanner/marker_finder.py`:
```python
"""Triangle marker detection for exam sheet alignment.

Migrated from legacy/scanner.py detect_triangles_and_lines().
"""

import logging
import cv2
import numpy as np

logger = logging.getLogger("smartgrader.scanner.marker_finder")


def find_triangles(image, min_area=400, approx_tolerance=0.05):
    """Detect triangle markers in the image.

    Args:
        image: BGR image.
        min_area: Minimum contour area to consider.
        approx_tolerance: Polygon approximation tolerance factor.

    Returns:
        List of dicts with keys: center (x, y), area, contour.
    """
    height, width = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect background color from corners
    corners = [gray[0, 0], gray[0, width - 1], gray[height - 1, 0], gray[height - 1, width - 1]]
    if np.mean(corners) < 127:
        gray = cv2.bitwise_not(gray)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    triangles = []

    for cnt in contours:
        perimeter = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, approx_tolerance * perimeter, True)
        if len(approx) != 3:
            continue
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        triangles.append({"center": (cx, cy), "area": area, "contour": approx})

    triangles.sort(key=lambda t: t["area"], reverse=True)
    logger.info("Found %d triangles (min_area=%d)", len(triangles), min_area)
    return triangles


def find_section_boundaries(image, triangles):
    """Find top and bottom Y boundaries from 4 triangle markers.

    The 4 largest triangles are paired by proximity, and the midpoint
    Y of each pair defines a horizontal boundary line.

    Args:
        image: BGR image (for dimensions).
        triangles: List from find_triangles().

    Returns:
        Tuple (top_y, bottom_y) or None if fewer than 4 triangles found.
    """
    best_4 = triangles[:4]
    if len(best_4) < 4:
        logger.warning("Need 4 triangles, found %d", len(best_4))
        return None

    centers = [t["center"] for t in best_4]

    # Pair triangles by shortest distance
    linked = set()
    pairs = []
    for i in range(len(centers)):
        if i in linked:
            continue
        best_dist = float("inf")
        best_j = None
        for j in range(len(centers)):
            if j <= i or j in linked:
                continue
            dist = np.sqrt((centers[i][0] - centers[j][0]) ** 2 + (centers[i][1] - centers[j][1]) ** 2)
            if dist < best_dist:
                best_dist = dist
                best_j = j
        if best_j is not None:
            pairs.append((i, best_j))
            linked.add(i)
            linked.add(best_j)

    line_ys = []
    for i, j in pairs:
        y = (centers[i][1] + centers[j][1]) // 2
        line_ys.append(y)

    line_ys.sort()
    top_y, bottom_y = line_ys[0], line_ys[-1]
    logger.info("Section boundaries: y=%d to y=%d", top_y, bottom_y)
    return top_y, bottom_y
```

- [ ] **Step 2: Write the bubble detector**

`app/scanner/detector.py`:
```python
"""Unified bubble detector with configurable parameters.

Consolidates logic from legacy scanner files into a single detector.
Uses contour analysis (most reliable method from testing).
"""

import logging
import cv2
import numpy as np

logger = logging.getLogger("smartgrader.scanner.detector")


class BubbleDetector:
    """Detects bubbles (filled circles) in exam sheet images."""

    def __init__(
        self,
        area_min=60,
        area_max=600,
        circularity_min=0.65,
        aspect_min=0.6,
        aspect_max=1.5,
        radius_min=6,
        radius_max=25,
        duplicate_distance=10,
    ):
        self.area_min = area_min
        self.area_max = area_max
        self.circularity_min = circularity_min
        self.aspect_min = aspect_min
        self.aspect_max = aspect_max
        self.radius_min = radius_min
        self.radius_max = radius_max
        self.duplicate_distance = duplicate_distance

    def detect(self, image, top_y, bottom_y, margin=40):
        """Detect bubbles in the region between top_y and bottom_y.

        Args:
            image: BGR image.
            top_y: Top boundary of answer section.
            bottom_y: Bottom boundary of answer section.
            margin: Pixel margin inside boundaries.

        Returns:
            List of bubble dicts with keys: x, y, r, area, col ('L' or 'R').
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 4
        )
        kernel = np.ones((2, 2), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        img_width = image.shape[1]
        bubbles = self._filter_contours(contours, top_y, bottom_y, img_width, margin)
        bubbles = self._remove_duplicates(bubbles)
        bubbles = self._remove_outliers(bubbles)

        logger.info("Detected %d bubbles in region y=%d..%d", len(bubbles), top_y, bottom_y)
        return bubbles

    def _filter_contours(self, contours, top_y, bottom_y, img_width, margin):
        """Filter contours to only valid bubbles."""
        left_min = int(img_width * 0.08)
        left_max = int(img_width * 0.25)
        right_min = int(img_width * 0.45)
        right_max = int(img_width * 0.75)

        bubbles = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.area_min or area > self.area_max:
                continue

            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue

            circularity = 4 * np.pi * area / (perimeter * perimeter)
            if circularity < self.circularity_min:
                continue

            x, y, cw, ch = cv2.boundingRect(cnt)
            aspect = cw / ch if ch > 0 else 0
            if aspect < self.aspect_min or aspect > self.aspect_max:
                continue

            M = cv2.moments(cnt)
            if M["m00"] == 0:
                continue

            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            r = int(np.sqrt(area / np.pi))

            if r < self.radius_min or r > self.radius_max:
                continue
            if not (top_y + margin < cy < bottom_y - margin):
                continue

            col = None
            if left_min <= cx <= left_max:
                col = "L"
            elif right_min <= cx <= right_max:
                col = "R"

            if col:
                bubbles.append({"x": cx, "y": cy, "r": r, "area": area, "col": col})

        return bubbles

    def _remove_duplicates(self, bubbles):
        """Remove duplicate detections within duplicate_distance pixels."""
        final = []
        for b in bubbles:
            is_dup = False
            for f in final:
                dist = np.sqrt((b["x"] - f["x"]) ** 2 + (b["y"] - f["y"]) ** 2)
                if dist < self.duplicate_distance:
                    is_dup = True
                    break
            if not is_dup:
                final.append(b)
        return final

    def _remove_outliers(self, bubbles, max_deviation=50):
        """Remove bubbles that deviate too far from column average X."""
        if len(bubbles) < 4:
            return bubbles

        left = [b for b in bubbles if b["col"] == "L"]
        right = [b for b in bubbles if b["col"] == "R"]

        avg_left_x = sum(b["x"] for b in left) / len(left) if left else 0
        avg_right_x = sum(b["x"] for b in right) / len(right) if right else 0

        verified = []
        for b in bubbles:
            avg_x = avg_left_x if b["col"] == "L" else avg_right_x
            if abs(b["x"] - avg_x) <= max_deviation:
                verified.append(b)

        removed = len(bubbles) - len(verified)
        if removed > 0:
            logger.debug("Removed %d outlier bubbles", removed)
        return verified


def check_if_filled(image, bubble, fill_threshold=50):
    """Check if a bubble is filled by counting dark pixels.

    Args:
        image: BGR image.
        bubble: Dict with x, y, r keys.
        fill_threshold: Percentage of dark pixels to consider filled.

    Returns:
        Tuple (is_filled: bool, fill_percentage: float).
    """
    x, y, r = bubble["x"], bubble["y"], bubble["r"]
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.circle(mask, (x, y), r, 255, -1)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    dark_pixels = cv2.countNonZero(cv2.bitwise_not(gray) & mask)
    total_pixels = cv2.countNonZero(mask)

    if total_pixels == 0:
        return False, 0.0

    fill_pct = (dark_pixels / total_pixels) * 100
    return fill_pct >= fill_threshold, fill_pct
```

- [ ] **Step 3: Write detector tests**

`tests/test_scanner/test_detector.py`:
```python
"""Tests for bubble detector."""

import numpy as np
import cv2
from app.scanner.detector import BubbleDetector, check_if_filled


def _make_bubble_image(width=800, height=1000, bubble_positions=None):
    """Create a white image with black circles at specified positions."""
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    if bubble_positions:
        for (cx, cy, r) in bubble_positions:
            cv2.circle(img, (cx, cy), r, (0, 0, 0), -1)  # filled black circle
    return img


def test_detector_init():
    detector = BubbleDetector()
    assert detector.area_min == 60
    assert detector.circularity_min == 0.65


def test_detector_custom_params():
    detector = BubbleDetector(area_min=100, area_max=500)
    assert detector.area_min == 100
    assert detector.area_max == 500


def test_detect_no_bubbles():
    img = _make_bubble_image()
    detector = BubbleDetector()
    bubbles = detector.detect(img, top_y=100, bottom_y=900)
    assert len(bubbles) == 0


def test_check_filled_bubble():
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    cv2.circle(img, (50, 50), 15, (0, 0, 0), -1)  # filled
    bubble = {"x": 50, "y": 50, "r": 15}
    is_filled, pct = check_if_filled(img, bubble, fill_threshold=50)
    assert is_filled is True
    assert pct > 80


def test_check_empty_bubble():
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    cv2.circle(img, (50, 50), 15, (0, 0, 0), 2)  # outline only
    bubble = {"x": 50, "y": 50, "r": 15}
    is_filled, pct = check_if_filled(img, bubble, fill_threshold=50)
    assert is_filled is False
    assert pct < 50
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_scanner/test_detector.py -v
```

Expected: All 5 tests pass.

- [ ] **Step 5: Commit**

```bash
git add app/scanner/marker_finder.py app/scanner/detector.py tests/test_scanner/test_detector.py
git commit -m "feat: add marker finder and bubble detector with tests"
```

---

## Task 10: Scanner Consolidation -- Grid Mapper & Answer Reader

**Files:**
- Create: `app/scanner/grid_mapper.py`, `app/scanner/answer_reader.py`

- [ ] **Step 1: Write the grid mapper**

`app/scanner/grid_mapper.py`:
```python
"""Maps detected bubbles to question/choice grid.

Migrated from legacy/scanner.py map_bubbles_to_questions().
"""

import logging

logger = logging.getLogger("smartgrader.scanner.grid_mapper")

CHOICE_LABELS = ["A", "B", "C", "D", "E", "F"]


def map_bubbles_to_questions(bubbles, questions):
    """Map detected bubbles to questions using choice counts from database.

    Bubbles are sorted by Y position within each column (L/R).
    Questions are consumed in order, taking choices_count bubbles per question.

    Args:
        bubbles: List of bubble dicts with keys: x, y, r, area, col.
        questions: List of question dicts with keys: id, choices_count, marks.

    Returns:
        Dict mapping "Q{id}{label}" -> bubble dict (with added question, choice, label keys).
    """
    left_col = sorted([b for b in bubbles if b["col"] == "L"], key=lambda b: b["y"])
    right_col = sorted([b for b in bubbles if b["col"] == "R"], key=lambda b: b["y"])

    questions_sorted = sorted(questions, key=lambda q: q["id"])

    # Determine how many questions fit in left column
    left_count = len(left_col)
    left_questions = []
    bubble_used = 0
    for q in questions_sorted:
        if bubble_used + q["choices_count"] <= left_count:
            left_questions.append(q)
            bubble_used += q["choices_count"]
        else:
            break

    right_questions = [q for q in questions_sorted if q not in left_questions]

    result = {}
    mapped_ids = []

    _assign_column(left_col, left_questions, result, mapped_ids)
    _assign_column(right_col, right_questions, result, mapped_ids)

    logger.info("Mapped %d bubbles to %d questions", len(result), len(mapped_ids))
    return result, mapped_ids


def _assign_column(col_bubbles, questions, result, mapped_ids):
    """Assign bubbles in a column to questions sequentially."""
    idx = 0
    for q in questions:
        count = q["choices_count"]
        q_id = q["id"]

        q_bubbles = []
        while idx < len(col_bubbles) and len(q_bubbles) < count:
            q_bubbles.append(col_bubbles[idx])
            idx += 1

        if len(q_bubbles) < count:
            logger.warning("Q%d: expected %d bubbles, got %d", q_id, count, len(q_bubbles))
            break

        mapped_ids.append(q_id)
        for j, bubble in enumerate(q_bubbles):
            if j < len(CHOICE_LABELS):
                label = CHOICE_LABELS[j]
                bubble["question"] = q_id
                bubble["choice"] = label
                bubble["label"] = f"Q{q_id}{label}"
                result[f"Q{q_id}{label}"] = bubble
```

- [ ] **Step 2: Write the answer reader**

`app/scanner/answer_reader.py`:
```python
"""Reads student answers from mapped bubbles.

Determines which bubble per question has the highest fill percentage.
"""

import logging
from app.scanner.detector import check_if_filled

logger = logging.getLogger("smartgrader.scanner.answer_reader")

CHOICE_LABELS = ["A", "B", "C", "D", "E", "F"]


def read_answers(image, mapped_bubbles, questions, fill_threshold=50):
    """Read detected answers from mapped bubbles.

    For each question, finds the bubble with highest fill percentage.
    If the best fill is below threshold, the question is unanswered.

    Args:
        image: BGR image.
        mapped_bubbles: Dict from grid_mapper.map_bubbles_to_questions().
        questions: List of question dicts with keys: id, choices_count.
        fill_threshold: Minimum fill percentage to consider a bubble selected.

    Returns:
        Dict mapping question_id -> detected choice label (or None if unanswered).
    """
    answers = {}

    for q in questions:
        q_id = q["id"]
        best_fill = 0.0
        best_choice = None

        for label in CHOICE_LABELS[: q["choices_count"]]:
            key = f"Q{q_id}{label}"
            if key not in mapped_bubbles:
                continue

            bubble = mapped_bubbles[key]
            _, fill_pct = check_if_filled(image, bubble, fill_threshold)

            if fill_pct > best_fill:
                best_fill = fill_pct
                best_choice = label

        if best_fill >= fill_threshold:
            answers[q_id] = best_choice
            logger.debug("Q%d: detected %s (%.1f%%)", q_id, best_choice, best_fill)
        else:
            answers[q_id] = None
            logger.debug("Q%d: unanswered (best fill %.1f%%)", q_id, best_fill)

    answered = sum(1 for v in answers.values() if v is not None)
    logger.info("Read answers: %d/%d answered", answered, len(questions))
    return answers
```

- [ ] **Step 3: Commit**

```bash
git add app/scanner/grid_mapper.py app/scanner/answer_reader.py
git commit -m "feat: add grid mapper and answer reader modules"
```

---

## Task 11: Scanner Service (Orchestrator)

**Files:**
- Create: `app/services/scanner_service.py`

- [ ] **Step 1: Write the scanner service**

`app/services/scanner_service.py`:
```python
"""Scanning orchestration service.

Coordinates the full pipeline: load image -> preprocess -> detect markers ->
detect bubbles -> map to questions -> read answers -> grade.
"""

import logging
import os
import cv2
import numpy as np

from app.scanner.preprocessor import ImagePreprocessor
from app.scanner.marker_finder import find_triangles, find_section_boundaries
from app.scanner.detector import BubbleDetector
from app.scanner.grid_mapper import map_bubbles_to_questions
from app.scanner.answer_reader import read_answers
from app.services.exam_service import get_exam_by_id, get_questions_for_exam
from app.services.grading_service import grade_mcq_answers
from app.errors import ScannerError, DetectionError

logger = logging.getLogger("smartgrader.services.scanner")


def load_image(file_path):
    """Load image from file (supports PDF and image formats).

    Args:
        file_path: Path to image or PDF file.

    Returns:
        BGR numpy array.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        try:
            import fitz
            doc = fitz.open(file_path)
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            doc.close()
            logger.info("Loaded PDF: %s (%dx%d)", file_path, img.shape[1], img.shape[0])
            return img
        except ImportError:
            raise ScannerError("PyMuPDF (fitz) is required for PDF scanning")
    else:
        img = cv2.imread(file_path)
        if img is None:
            raise ScannerError(f"Could not load image: {file_path}")
        logger.info("Loaded image: %s (%dx%d)", file_path, img.shape[1], img.shape[0])
        return img


def scan_and_grade(file_path, exam_id, fill_threshold=50, save_debug=None):
    """Full scanning and grading pipeline.

    Args:
        file_path: Path to scanned answer sheet.
        exam_id: Exam ID to grade against.
        fill_threshold: Minimum fill percentage for bubble detection.
        save_debug: Directory to save debug images (None to skip).

    Returns:
        Dict with grading results from grading_service.grade_mcq_answers().
    """
    # Load image
    image = load_image(file_path)

    # Get exam questions
    exam = get_exam_by_id(exam_id)
    questions_data = get_questions_for_exam(exam_id)
    questions = [
        {
            "id": q["id"],
            "choices_count": q["choices_number"],
            "marks": q["marks"],
        }
        for q in questions_data
    ]

    if not questions:
        raise ScannerError(f"Exam {exam_id} has no questions")

    # Detect triangle markers
    triangles = find_triangles(image)
    boundaries = find_section_boundaries(image, triangles)

    if boundaries is None:
        raise DetectionError("Could not detect 4 triangle markers on the sheet")

    top_y, bottom_y = boundaries

    # Detect bubbles
    detector = BubbleDetector(
        area_min=60,
        area_max=600,
        circularity_min=0.65,
    )
    bubbles = detector.detect(image, top_y, bottom_y)

    if not bubbles:
        raise DetectionError("No bubbles detected in the answer section")

    # Map bubbles to questions
    mapped_bubbles, mapped_ids = map_bubbles_to_questions(bubbles, questions)

    if not mapped_bubbles:
        raise DetectionError("Could not map bubbles to questions")

    # Read answers
    detected_answers = read_answers(image, mapped_bubbles, questions, fill_threshold)

    # Grade
    result = grade_mcq_answers(exam_id, detected_answers)

    # Save debug visualization
    if save_debug:
        _save_debug_image(image, mapped_bubbles, top_y, bottom_y, save_debug)

    logger.info(
        "Scan complete for exam %d: %s/%s (%.1f%%)",
        exam_id, result["obtained_marks"], result["total_marks"], result["percentage"],
    )
    return result


def _save_debug_image(image, mapped_bubbles, top_y, bottom_y, output_dir):
    """Save annotated debug image."""
    os.makedirs(output_dir, exist_ok=True)
    result_img = image.copy()

    cv2.line(result_img, (0, top_y), (image.shape[1], top_y), (255, 0, 0), 4)
    cv2.line(result_img, (0, bottom_y), (image.shape[1], bottom_y), (255, 0, 0), 4)

    colors = [(0, 255, 0), (0, 255, 255), (255, 0, 255), (0, 128, 255), (128, 0, 255)]
    for label, bubble in mapped_bubbles.items():
        q_num = bubble.get("question", 0)
        color = colors[q_num % len(colors)]
        cv2.circle(result_img, (bubble["x"], bubble["y"]), bubble["r"], color, 3)
        cv2.putText(
            result_img, label,
            (bubble["x"] + 15, bubble["y"] + 4),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2,
        )

    filepath = os.path.join(output_dir, "scan_result.jpg")
    cv2.imwrite(filepath, result_img)
    logger.info("Saved debug image: %s", filepath)
```

- [ ] **Step 2: Commit**

```bash
git add app/services/scanner_service.py
git commit -m "feat: add scanner service orchestrating full scan pipeline"
```

---

## Task 12: Flask API Routes

**Files:**
- Update: `app/routes/exams.py`, `app/routes/questions.py`, `app/routes/students.py`, `app/routes/scanning.py`, `app/routes/grading.py`
- Test: `tests/test_routes/test_exams.py`

- [ ] **Step 1: Write exam routes**

`app/routes/exams.py`:
```python
"""Exam API endpoints."""

import logging
from flask import Blueprint, request, jsonify
from app.services.exam_service import (
    create_exam, get_all_exams, get_exam_by_id,
    update_exam, delete_exam, get_exam_statistics,
)

logger = logging.getLogger("smartgrader.routes.exams")
exams_bp = Blueprint("exams", __name__)


@exams_bp.route("/exams", methods=["GET"])
def list_exams():
    exams = get_all_exams()
    return jsonify([e.to_dict() for e in exams])


@exams_bp.route("/exams", methods=["POST"])
def create():
    data = request.get_json()
    exam = create_exam(
        title=data["title"],
        subject=data.get("subject"),
        date=data.get("date"),
        total_marks=data.get("total_marks"),
    )
    return jsonify(exam.to_dict()), 201


@exams_bp.route("/exams/<int:exam_id>", methods=["GET"])
def get_exam(exam_id):
    exam = get_exam_by_id(exam_id)
    data = exam.to_dict()
    data["statistics"] = get_exam_statistics(exam_id)
    return jsonify(data)


@exams_bp.route("/exams/<int:exam_id>", methods=["PUT"])
def update(exam_id):
    data = request.get_json()
    exam = update_exam(exam_id, **data)
    return jsonify(exam.to_dict())


@exams_bp.route("/exams/<int:exam_id>", methods=["DELETE"])
def delete(exam_id):
    delete_exam(exam_id)
    return jsonify({"message": "Exam deleted"}), 200
```

- [ ] **Step 2: Write question routes**

`app/routes/questions.py`:
```python
"""Question API endpoints."""

import logging
from flask import Blueprint, request, jsonify
from app.services.exam_service import create_question_with_choices, get_questions_for_exam

logger = logging.getLogger("smartgrader.routes.questions")
questions_bp = Blueprint("questions", __name__)


@questions_bp.route("/exams/<int:exam_id>/questions", methods=["GET"])
def list_questions(exam_id):
    questions = get_questions_for_exam(exam_id)
    return jsonify(questions)


@questions_bp.route("/exams/<int:exam_id>/questions", methods=["POST"])
def create_question(exam_id):
    data = request.get_json()
    question = create_question_with_choices(
        exam_id=exam_id,
        question_text=data["question_text"],
        marks=data["marks"],
        choices=data["choices"],
    )
    return jsonify(question.to_dict(include_choices=True)), 201
```

- [ ] **Step 3: Write student routes**

`app/routes/students.py`:
```python
"""Student API endpoints."""

import logging
from flask import Blueprint, request, jsonify
from app.models import db
from app.models.student import Student
from app.errors import NotFoundError

logger = logging.getLogger("smartgrader.routes.students")
students_bp = Blueprint("students", __name__)


@students_bp.route("/students", methods=["GET"])
def list_students():
    students = Student.query.order_by(Student.name).all()
    return jsonify([s.to_dict() for s in students])


@students_bp.route("/students", methods=["POST"])
def create_student():
    data = request.get_json()
    student = Student(
        name=data["name"],
        matricule=data["matricule"],
        email=data.get("email"),
    )
    db.session.add(student)
    db.session.commit()
    return jsonify(student.to_dict()), 201


@students_bp.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    student = Student.query.get(student_id)
    if student is None:
        raise NotFoundError("Student", student_id)
    return jsonify(student.to_dict())
```

- [ ] **Step 4: Write scanning routes**

`app/routes/scanning.py`:
```python
"""Scanning API endpoints."""

import os
import logging
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.services.scanner_service import scan_and_grade
from app.errors import SmartGraderError

logger = logging.getLogger("smartgrader.routes.scanning")
scanning_bp = Blueprint("scanning", __name__)


def _allowed_file(filename):
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"pdf", "png", "jpg", "jpeg"})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


@scanning_bp.route("/scan/upload", methods=["POST"])
def upload_and_scan():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    exam_id = request.form.get("exam_id", type=int)
    if exam_id is None:
        return jsonify({"error": "exam_id is required"}), 400

    upload_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    try:
        fill_threshold = current_app.config.get("FILL_THRESHOLD", 50)
        result = scan_and_grade(filepath, exam_id, fill_threshold=fill_threshold)
        return jsonify(result)
    except SmartGraderError as e:
        return jsonify({"error": e.message}), e.status_code
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
```

- [ ] **Step 5: Write grading routes**

`app/routes/grading.py`:
```python
"""Grading API endpoints."""

import logging
from flask import Blueprint, request, jsonify
from app.services.grading_service import save_result, get_results_for_exam

logger = logging.getLogger("smartgrader.routes.grading")
grading_bp = Blueprint("grading", __name__)


@grading_bp.route("/results/exam/<int:exam_id>", methods=["GET"])
def get_exam_results(exam_id):
    results = get_results_for_exam(exam_id)
    return jsonify(results)


@grading_bp.route("/results", methods=["POST"])
def save_grade():
    data = request.get_json()
    save_result(
        student_id=data["student_id"],
        exam_id=data["exam_id"],
        score=data["score"],
        percentage=data["percentage"],
    )
    return jsonify({"message": "Result saved"}), 201
```

- [ ] **Step 6: Write route tests**

`tests/test_routes/test_exams.py`:
```python
"""Tests for exam API routes."""

import json


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "ok"


def test_create_exam(client):
    response = client.post(
        "/api/exams",
        data=json.dumps({"title": "Math", "subject": "Science", "total_marks": 100}),
        content_type="application/json",
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["title"] == "Math"
    assert data["id"] is not None


def test_list_exams(client):
    client.post(
        "/api/exams",
        data=json.dumps({"title": "A", "subject": "S"}),
        content_type="application/json",
    )
    response = client.get("/api/exams")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1


def test_get_exam(client):
    resp = client.post(
        "/api/exams",
        data=json.dumps({"title": "Find", "subject": "S"}),
        content_type="application/json",
    )
    exam_id = json.loads(resp.data)["id"]

    response = client.get(f"/api/exams/{exam_id}")
    assert response.status_code == 200
    assert json.loads(response.data)["title"] == "Find"


def test_get_exam_not_found(client):
    response = client.get("/api/exams/999")
    assert response.status_code == 404


def test_update_exam(client):
    resp = client.post(
        "/api/exams",
        data=json.dumps({"title": "Old", "subject": "S"}),
        content_type="application/json",
    )
    exam_id = json.loads(resp.data)["id"]

    response = client.put(
        f"/api/exams/{exam_id}",
        data=json.dumps({"title": "New"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert json.loads(response.data)["title"] == "New"


def test_delete_exam(client):
    resp = client.post(
        "/api/exams",
        data=json.dumps({"title": "Delete", "subject": "S"}),
        content_type="application/json",
    )
    exam_id = json.loads(resp.data)["id"]

    response = client.delete(f"/api/exams/{exam_id}")
    assert response.status_code == 200

    response = client.get(f"/api/exams/{exam_id}")
    assert response.status_code == 404


def test_create_question_with_choices(client):
    resp = client.post(
        "/api/exams",
        data=json.dumps({"title": "E", "subject": "S"}),
        content_type="application/json",
    )
    exam_id = json.loads(resp.data)["id"]

    response = client.post(
        f"/api/exams/{exam_id}/questions",
        data=json.dumps({
            "question_text": "What is 1+1?",
            "marks": 5,
            "choices": [
                {"label": "A", "text": "1", "is_correct": False},
                {"label": "B", "text": "2", "is_correct": True},
            ],
        }),
        content_type="application/json",
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert len(data["choices"]) == 2
```

- [ ] **Step 7: Run all tests**

```bash
pytest tests/ -v
```

Expected: All tests pass (~30 tests).

- [ ] **Step 8: Commit**

```bash
git add app/routes/ tests/test_routes/
git commit -m "feat: add Flask API routes with full CRUD and scan endpoints"
```

---

## Task 13: Data Migration Script

**Files:**
- Create: `scripts/migrate_data.py`, `scripts/seed_data.py`

- [ ] **Step 1: Write the migration script**

`scripts/migrate_data.py`:
```python
"""Migrate data from legacy SQLite database to new SQLAlchemy models.

Usage: python -m scripts.migrate_data [path_to_old_db]
"""

import os
import sys
import sqlite3

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db
from app.models.exam import Exam, Question, Choice
from app.models.student import Student, StudentAnswer
from app.models.result import Result


def migrate(old_db_path):
    """Migrate data from old database to new."""
    if not os.path.exists(old_db_path):
        print(f"Old database not found: {old_db_path}")
        return

    app = create_app("development")
    old_conn = sqlite3.connect(old_db_path)
    old_cur = old_conn.cursor()

    with app.app_context():
        db.create_all()

        # Migrate exams
        old_cur.execute("SELECT id, title, subject, date, total_marks FROM exams")
        for row in old_cur.fetchall():
            exam = Exam(id=row[0], title=row[1], subject=row[2], date=row[3], total_marks=row[4])
            db.session.add(exam)
        db.session.commit()
        print(f"Migrated {Exam.query.count()} exams")

        # Migrate questions
        old_cur.execute("SELECT id, exam_id, question_text, question_choices_number, marks FROM questions")
        for row in old_cur.fetchall():
            q = Question(id=row[0], exam_id=row[1], question_text=row[2], question_choices_number=row[3], marks=row[4])
            db.session.add(q)
        db.session.commit()
        print(f"Migrated {Question.query.count()} questions")

        # Migrate choices
        old_cur.execute("SELECT id, question_id, choice_label, choice_text, is_correct FROM choices")
        for row in old_cur.fetchall():
            c = Choice(id=row[0], question_id=row[1], choice_label=row[2], choice_text=row[3], is_correct=row[4])
            db.session.add(c)
        db.session.commit()
        print(f"Migrated {Choice.query.count()} choices")

        # Migrate students
        old_cur.execute("SELECT id, name, matricule, email FROM students")
        for row in old_cur.fetchall():
            s = Student(id=row[0], name=row[1], matricule=row[2], email=row[3])
            db.session.add(s)
        db.session.commit()
        print(f"Migrated {Student.query.count()} students")

        # Migrate results
        old_cur.execute("SELECT id, student_id, exam_id, score, percentage, graded_at FROM results")
        for row in old_cur.fetchall():
            r = Result(id=row[0], student_id=row[1], exam_id=row[2], score=row[3], percentage=row[4], graded_at=row[5])
            db.session.add(r)
        db.session.commit()
        print(f"Migrated {Result.query.count()} results")

    old_conn.close()
    print("Migration complete!")


if __name__ == "__main__":
    old_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smart_grader.db"
    )
    migrate(old_path)
```

- [ ] **Step 2: Write seed data script**

`scripts/seed_data.py`:
```python
"""Seed database with sample data for development.

Usage: python -m scripts.seed_data
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db
from app.services.exam_service import create_exam, create_question_with_choices
from app.models.student import Student


def seed():
    """Insert sample data."""
    app = create_app("development")

    with app.app_context():
        db.create_all()

        # Sample exam
        exam = create_exam(
            title="Mathematics - Algebra",
            subject="Mathematics",
            date="2026-04-06",
            total_marks=20,
        )

        create_question_with_choices(
            exam_id=exam.id,
            question_text="What is 2 + 2?",
            marks=5,
            choices=[
                {"label": "A", "text": "3", "is_correct": False},
                {"label": "B", "text": "4", "is_correct": True},
                {"label": "C", "text": "5", "is_correct": False},
                {"label": "D", "text": "6", "is_correct": False},
            ],
        )

        create_question_with_choices(
            exam_id=exam.id,
            question_text="What is 5 x 3?",
            marks=5,
            choices=[
                {"label": "A", "text": "8", "is_correct": False},
                {"label": "B", "text": "15", "is_correct": True},
                {"label": "C", "text": "20", "is_correct": False},
            ],
        )

        create_question_with_choices(
            exam_id=exam.id,
            question_text="Solve: x + 3 = 7",
            marks=5,
            choices=[
                {"label": "A", "text": "x = 3", "is_correct": False},
                {"label": "B", "text": "x = 4", "is_correct": True},
                {"label": "C", "text": "x = 10", "is_correct": False},
                {"label": "D", "text": "x = 7", "is_correct": False},
            ],
        )

        create_question_with_choices(
            exam_id=exam.id,
            question_text="What is the square root of 16?",
            marks=5,
            choices=[
                {"label": "A", "text": "2", "is_correct": False},
                {"label": "B", "text": "4", "is_correct": True},
                {"label": "C", "text": "8", "is_correct": False},
            ],
        )

        # Sample students
        s1 = Student(name="Ahmed Benali", matricule="2026001", email="ahmed@univ.dz")
        s2 = Student(name="Fatima Zahra", matricule="2026002", email="fatima@univ.dz")
        s3 = Student(name="Mohamed Amine", matricule="2026003", email="amine@univ.dz")
        db.session.add_all([s1, s2, s3])
        db.session.commit()

        print(f"Seeded: 1 exam, 4 questions, 3 students")


if __name__ == "__main__":
    seed()
```

- [ ] **Step 3: Commit**

```bash
git add scripts/
git commit -m "feat: add data migration and seed scripts"
```

---

## Task 14: Entry Point & Smoke Test

**Files:**
- Verify: `run.py`, all modules import correctly

- [ ] **Step 1: Run the full test suite**

```bash
cd C:\Users\pc\Desktop\SmartGrader_APP_WithPDF
pip install -r requirements.txt
pytest tests/ -v --tb=short
```

Expected: All tests pass.

- [ ] **Step 2: Run the app and test health endpoint**

```bash
python run.py &
# In another terminal:
curl http://localhost:5000/api/health
```

Expected: `{"status":"ok","version":"0.2.0"}`

- [ ] **Step 3: Run seed and verify API**

```bash
python -m scripts.seed_data
curl http://localhost:5000/api/exams
```

Expected: JSON array with the seeded exam.

- [ ] **Step 4: Update TODO.md to mark completed items**

Update all Sub-Project 1 items to `[x]`.

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete sub-project 1 -- code restructuring and quality"
```

---

## Summary

| Task | Module | Tests |
|------|--------|-------|
| 1 | Scaffolding (.gitignore, requirements, CHANGELOG, TODO, directory layout) | -- |
| 2 | Configuration system (app/config.py) | -- |
| 3 | Exceptions & logging (app/errors.py, app/logging_config.py) | -- |
| 4 | SQLAlchemy models (exam, student, result) | 7 tests |
| 5 | Flask app factory + blueprint stubs | -- |
| 6 | Exam service CRUD | 9 tests |
| 7 | Grading service | 4 tests |
| 8 | Scanner: preprocessor | 6 tests |
| 9 | Scanner: marker finder + detector | 5 tests |
| 10 | Scanner: grid mapper + answer reader | -- |
| 11 | Scanner service orchestrator | -- |
| 12 | Flask API routes | 8 tests |
| 13 | Data migration + seed scripts | -- |
| 14 | Integration smoke test | manual |

**Total: 14 tasks, ~39 automated tests**
