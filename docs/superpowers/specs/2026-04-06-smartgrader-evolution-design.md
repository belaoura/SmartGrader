# SmartGrader Evolution -- Design Specification

**Date:** 2026-04-06
**Status:** Approved
**Approach:** Incremental Migration (restructure → web UI → AI → documentation)

---

## 1. Overview

SmartGrader is a desktop application (PyQt5) for creating multiple-choice exams, generating printable answer sheets, and grading scanned sheets via bubble detection. This spec describes its evolution into a web-based platform with AI-powered grading for both MCQ and short written answers, structured as a final-year graduation project (PFE).

### Goals
- Restructure the codebase from a flat monolith into a clean, layered architecture
- Replace the PyQt5 desktop UI with a modern web application (Flask + React)
- Integrate a small vision language model (Qwen2.5-VL-3B) for handwriting OCR and short-answer grading
- Produce formal academic documentation suitable for a PFE defense

### Constraints
- GPU: 6-8 GB VRAM (RTX 3060 / RTX 4060 class)
- Languages: French, Arabic, English (trilingual handwriting)
- Vision model must run locally (no cloud API dependency)
- Must remain a single-developer project (PFE scope)

---

## 2. Sub-Projects

Executed in order. Each sub-project gets its own implementation plan.

| # | Sub-Project | Depends On | Deliverable |
|---|-------------|------------|-------------|
| 1 | Code Restructuring & Quality | Nothing | Clean architecture, tests, config system |
| 2 | Web UI (Flask + React) | Sub-project 1 | Working web application replacing PyQt5 |
| 3 | AI Vision Model Integration | Sub-project 2 | MCQ + short answer auto-grading |
| 4 | Academic Documentation | Sub-projects 1-3 | PFE thesis document |

---

## 3. Sub-Project 1: Code Restructuring & Quality

### 3.1 New Project Structure

```
SmartGrader/
├── app/
│   ├── __init__.py               # Flask app factory
│   ├── config.py                 # All configuration constants
│   ├── models/
│   │   ├── __init__.py
│   │   ├── exam.py               # Exam, Question, Choice
│   │   ├── student.py            # Student, StudentAnswer
│   │   └── result.py             # Result
│   ├── services/
│   │   ├── __init__.py
│   │   ├── exam_service.py       # Exam CRUD
│   │   ├── sheet_generator.py    # QCM sheet generation (HTML/PDF)
│   │   ├── scanner_service.py    # Scanning orchestration
│   │   ├── grading_service.py    # MCQ + AI grading logic
│   │   └── ai_service.py         # Vision model inference
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── exams.py              # /api/exams/*
│   │   ├── questions.py          # /api/questions/*
│   │   ├── scanning.py           # /api/scan/*
│   │   ├── grading.py            # /api/grade/*
│   │   └── students.py           # /api/students/*
│   ├── scanner/
│   │   ├── __init__.py
│   │   ├── preprocessor.py       # Image preprocessing pipeline
│   │   ├── detector.py           # Unified bubble detector (strategy pattern)
│   │   ├── marker_finder.py      # Triangle/marker detection
│   │   ├── grid_mapper.py        # Bubbles → question grid mapping
│   │   └── answer_reader.py      # Read filled answers from grid
│   └── ai/
│       ├── __init__.py
│       ├── model_loader.py       # Load/manage vision model
│       ├── ocr_pipeline.py       # Handwriting → text
│       ├── answer_evaluator.py   # Grade extracted text vs reference
│       └── prompt_templates.py   # Prompt templates for grading
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── assets/
│   └── package.json
├── tests/
│   ├── test_services/
│   ├── test_scanner/
│   ├── test_ai/
│   └── test_routes/
├── docs/
│   ├── chapters/
│   ├── figures/
│   └── bibliography.bib
├── scripts/
│   ├── init_db.py
│   └── seed_data.py
├── instance/                     # Instance-specific overrides (not in git)
│   └── config.py                 # Local DB path, secrets, environment
├── requirements.txt
├── .gitignore
└── README.md
```

### 3.2 Database Migration

- Replace raw `sqlite3` with **SQLAlchemy ORM**
- Add **Flask-Migrate** (Alembic) for schema migrations
- Connection pooling via SQLAlchemy engine (fixes per-query connection creation)
- Keep SQLite for development; ORM allows PostgreSQL switch later
- Models define relationships explicitly with `relationship()` and `backref`

### 3.3 Scanner Consolidation

Current state: 6 overlapping files (`scanner.py`, `exam_scanner.py`, `circle_detection.py`, `circle_detector.py`, `robust_detection.py`, `single_column_scanner.py`).

New state: 5 focused modules in `app/scanner/` using strategy pattern:

- `preprocessor.py` -- configurable pipeline: load → validate → deskew → crop → enhance → threshold
- `detector.py` -- unified detector with interchangeable algorithms (Hough, contour, template matching) selected via config
- `marker_finder.py` -- triangle/alignment marker detection
- `grid_mapper.py` -- maps detected bubbles to question/choice grid
- `answer_reader.py` -- reads which bubbles are filled, returns answers

All hardcoded thresholds move to `config.py`.

### 3.4 Configuration System

Single `config.py` with all tunable parameters:

```python
class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///smart_grader.db'

    # Sheet generation
    PAGE_SIZE = 'A4'
    MARGIN_MM = {'top': 8, 'left': 12, 'right': 12, 'bottom': 10}

    # Scanner thresholds
    FILL_THRESHOLD = 50
    CIRCLE_AREA_RANGE = (80, 500)
    CIRCULARITY_MIN = 0.75

    # AI model
    VISION_MODEL = 'Qwen/Qwen2.5-VL-3B-Instruct'
    MODEL_DEVICE = 'cuda'
    MAX_TOKENS = 512
```

### 3.5 Logging

- Replace all `print()` with Python `logging` module
- Structured logging: `logger.info("Detected %d circles", count)`
- File + console handlers, configurable log level per environment

### 3.6 Error Handling

- Custom exception classes: `ScannerError`, `DetectionError`, `GradingError`
- Services raise domain exceptions
- Routes catch and return proper HTTP error responses with messages
- No silent failures

### 3.7 Testing

- Framework: `pytest` with fixtures for database, sample images, mock models
- Unit tests for services and scanner modules
- Integration tests for API routes
- Target: 60%+ coverage

---

## 4. Sub-Project 2: Web UI

### 4.1 Backend (Flask)

- App factory pattern with blueprints per route group
- JSON API returning structured responses
- Flask-CORS for frontend communication
- File uploads via multipart/form-data for scanned sheets
- Flask-SocketIO for real-time progress during scanning/grading

### 4.2 Frontend (React + Tailwind + shadcn/ui)

- React with Tailwind CSS and shadcn/ui component library
- Dark/light mode toggle
- Responsive design (works on tablet for teachers in exam halls)
- RTL support for Arabic content
- Skeleton loaders during async operations
- Color-coded grading: green (correct), red (incorrect), amber (uncertain)

### 4.3 Pages

| Page | Purpose |
|------|---------|
| Dashboard | Statistics: exam count, student count, recent grades, pass/fail charts |
| Exams Management | Create/edit/delete exams with inline question editor |
| Question Builder | Dynamic choice creation, preview panel, drag-to-reorder |
| Sheet Generator | Select exam → live preview → download PDF |
| Scanner | Upload image/PDF → real-time progress → visual result overlay |
| AI Grading | Upload short-answer sheets → OCR preview → AI evaluation with confidence |
| Students | Student roster, CSV import, individual grade history |
| Results | Per-exam results, statistics, CSV/PDF export, charts |
| Settings | Thresholds, model parameters, paper size, language |

### 4.4 API Endpoints

```
GET    /api/exams                  → list exams
POST   /api/exams                  → create exam
GET    /api/exams/:id              → exam details with questions
PUT    /api/exams/:id              → update exam
DELETE /api/exams/:id              → delete exam

POST   /api/exams/:id/generate     → generate answer sheet (returns PDF URL)
POST   /api/scan/upload             → upload scanned sheet
POST   /api/scan/process            → run bubble detection + grading
POST   /api/ai/evaluate             → run vision model on short answers

GET    /api/students                → list students
GET    /api/results/exam/:id        → results for an exam
GET    /api/results/student/:id     → all results for a student
POST   /api/results/export          → export to CSV/PDF
```

---

## 5. Sub-Project 3: AI Vision Model Integration

### 5.1 Model Choice

**Qwen2.5-VL-3B-Instruct** with 4-bit quantization (bitsandbytes).

Justification:
- Fits 6-8 GB VRAM with quantization
- Best multilingual vision model at this size (French, Arabic, English)
- Strong built-in OCR capability for handwriting
- Good instruction-following for structured grading output
- Alternative considered: PaliGemma2-3B (weaker on Arabic, less flexible evaluation)

### 5.2 Two-Stage Pipeline

**Stage 1 -- OCR (handwriting → text):**

Input: cropped image of a single answer zone.
Output: extracted text string.

The vision model receives the image with the prompt:
```
Read the handwritten text in this image. The text may be in French, Arabic,
or English. Return ONLY the transcribed text, nothing else.
```

Teacher can verify/correct the OCR output before proceeding to grading.

**Stage 2 -- Evaluation (grade the extracted text):**

Input: extracted text + reference answer or keywords + question context.
Output: JSON with score, feedback, confidence.

Two prompt variants depending on what the teacher provided:

*Model answer mode:*
```
You are grading a student's answer.

Question: {question_text}
Reference answer: {model_answer}
Student's answer: {extracted_text}
Maximum marks: {max_marks}

Grade the student's answer. Return JSON:
{"score": <number>, "max": <number>, "feedback": "<brief explanation>", "confidence": <0-1>}
```

*Keywords/rubric mode:*
```
You are grading a student's answer.

Question: {question_text}
Required concepts: {keywords_list}
Student's answer: {extracted_text}
Maximum marks: {max_marks}

Check which required concepts appear in the answer. Return JSON:
{"score": <number>, "max": <number>, "found_concepts": [...], "missing_concepts": [...], "confidence": <0-1>}
```

### 5.3 Why Two Stages

- Stage 1 output (extracted text) shown to teacher for verification before grading
- If OCR is wrong, teacher corrects it -- grade is based on corrected text
- Each stage can be debugged and improved independently
- Stage 2 can run text-only (no vision) -- faster, and could use a different model

### 5.4 Model Loading & Performance

- Load model once at Flask app startup via `transformers` + `bitsandbytes` (4-bit)
- Keep in GPU memory between requests (no reload per scan)
- Batch processing: when grading a full exam, process all answer zones in sequence
- Expected inference: ~2-4 seconds per answer zone on 6 GB GPU

### 5.5 Improvement Over Time (RAG Feedback Loop)

No fine-tuning (too expensive for 6-8 GB). Instead, a RAG-based feedback loop:

**New database table:**
```sql
CREATE TABLE ai_corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    student_text TEXT NOT NULL,
    ai_score REAL NOT NULL,
    teacher_score REAL NOT NULL,
    teacher_feedback TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);
```

**Flow:**
1. AI grades an answer with a confidence score
2. If confidence < 0.7, flag for manual teacher review
3. Teacher reviews and corrects the score/feedback
4. Correction stored in `ai_corrections`
5. Next time a similar question is graded, retrieve past corrections as few-shot examples in the prompt
6. AI accuracy improves without fine-tuning

**Per-subject prompt tuning:**
- Store which prompt template works best for each subject
- Teachers can customize grading criteria per exam

**Academic justification:**
- RAG-based improvement is well-documented in literature
- Quantitative improvement measurable (accuracy before/after corrections)
- Human-in-the-loop design (confidence threshold) shows responsible AI
- Practical within hardware constraints

---

## 6. Sub-Project 4: Academic Documentation

### 6.1 Thesis Chapter Structure

```
Chapter 1: General Introduction
  - Context and motivation
  - Problematique: "How can we automate exam grading for both MCQ and
    short answers using computer vision and AI?"
  - Objectives
  - Document organization

Chapter 2: State of the Art
  - Existing OMR systems (Remark, GradeCam, ZipGrade) -- comparison table
  - Computer vision for document analysis (Hough transform, contours)
  - Vision language models (LLaVA, Qwen-VL, PaliGemma, GPT-4V)
  - Handwriting recognition (Tesseract vs neural vs VLM)
  - RAG for improving LLM outputs
  - Comparative table: existing solutions vs SmartGrader
  - Gaps identified → justification

Chapter 3: Analysis & Design
  - Functional requirements (use case diagrams)
  - Non-functional requirements (performance, accuracy, hardware)
  - System architecture diagram
  - Database design (ER diagram)
  - API design (endpoint table)
  - AI pipeline design (two-stage diagram)
  - Class diagrams, sequence diagrams

Chapter 4: Implementation
  - Development environment
  - Project structure with explanations
  - Key implementation details per module
  - Screenshots of every UI page
  - Code snippets for critical algorithms

Chapter 5: Testing & Results
  - Test methodology (unit, integration, manual)
  - MCQ scanning accuracy (precision/recall on test set)
  - AI grading accuracy (AI vs teacher grades)
  - Performance benchmarks (time per sheet, inference time)
  - RAG improvement metrics
  - Tables and charts

Chapter 6: Conclusion & Perspectives
  - Summary of achievements
  - Limitations
  - Future work (fine-tuning, mobile, larger models, essay grading)

Appendices
  - Full API reference
  - Database schema
  - Installation guide
  - User manual with screenshots
```

### 6.2 UML Diagrams

All generated with code (PlantUML or Mermaid), stored in `docs/figures/`:

- Use case diagram (teacher, student, system actors)
- Class diagram (models, services, scanner modules)
- Sequence diagrams (3 flows: create exam, scan sheet, AI grade)
- ER diagram (database)
- Deployment diagram (frontend ↔ Flask ↔ SQLite ↔ vision model)
- Activity diagram (scanning pipeline)

---

## 7. Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React + Tailwind CSS + shadcn/ui | Web UI |
| Backend | Flask + Flask-RESTful + Flask-SocketIO | API server |
| ORM | SQLAlchemy + Flask-Migrate | Database access + migrations |
| Database | SQLite (dev) | Data storage |
| Image Processing | OpenCV + NumPy | Bubble detection, preprocessing |
| PDF Generation | pdfkit + wkhtmltopdf | Answer sheet PDF export |
| Vision Model | Qwen2.5-VL-3B-Instruct | OCR + answer evaluation |
| ML Framework | transformers + bitsandbytes | Model loading, 4-bit quantization |
| Testing | pytest | Unit + integration tests |
| Diagrams | PlantUML / Mermaid | UML for documentation |

---

## 8. Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Migration strategy | Incremental | Always have working system; good PFE narrative |
| UI framework | React + Tailwind + shadcn/ui | Modern, polished, well-documented |
| Backend | Flask | User preference; simpler than Django for this scope |
| ORM | SQLAlchemy | Connection pooling, migrations, clean models |
| Vision model | Qwen2.5-VL-3B | Fits VRAM, trilingual, strong OCR |
| Quantization | 4-bit (bitsandbytes) | Required to fit 6-8 GB VRAM |
| AI improvement | RAG feedback loop | No fine-tuning needed; within hardware constraints |
| Scanner architecture | Strategy pattern | One detector module, swappable algorithms |
| Grading pipeline | Two-stage (OCR → evaluate) | Teacher can verify OCR before grading |
| Confidence threshold | 0.7 | Below this → flag for manual review |
