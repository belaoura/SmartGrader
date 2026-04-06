# Appendices

## Appendix A: Full API Reference

SmartGrader exposes a RESTful API with 18 endpoints organised into six functional groups. All endpoints are prefixed with `/api/` and return JSON responses. Error responses follow a consistent format: `{"error": "<message>"}` with an appropriate HTTP status code.

### A.1 Health Check

| # | Method | Path | Description |
|---|--------|------|-------------|
| 1 | GET | `/api/health` | Returns application status and version |

**Example Request:**
```
GET /api/health
```

**Example Response (200):**
```json
{"status": "ok", "version": "0.2.0"}
```

### A.2 Exam Endpoints

| # | Method | Path | Description |
|---|--------|------|-------------|
| 2 | GET | `/api/exams` | List all examinations |
| 3 | POST | `/api/exams` | Create a new examination |
| 4 | GET | `/api/exams/<exam_id>` | Get a single examination by ID |
| 5 | PUT | `/api/exams/<exam_id>` | Update an examination |
| 6 | DELETE | `/api/exams/<exam_id>` | Delete an examination (cascades) |

**Example Request (Create):**
```
POST /api/exams
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
{
  "id": 1,
  "title": "Biology Midterm",
  "subject": "Biology",
  "date": "2026-03-15",
  "total_marks": 20.0
}
```

**Example Request (List):**
```
GET /api/exams
```

**Example Response (200):**
```json
[
  {"id": 1, "title": "Biology Midterm", "subject": "Biology", "date": "2026-03-15", "total_marks": 20.0},
  {"id": 2, "title": "History Final", "subject": "History", "date": "2026-04-01", "total_marks": 30.0}
]
```

### A.3 Question Endpoints

| # | Method | Path | Description |
|---|--------|------|-------------|
| 7 | GET | `/api/exams/<exam_id>/questions` | List questions for an exam |
| 8 | POST | `/api/exams/<exam_id>/questions` | Create a question with choices |

**Example Request (Create Question):**
```
POST /api/exams/1/questions
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

**Example Response (201):**
```json
{
  "id": 1,
  "exam_id": 1,
  "question_text": "Which organelle produces ATP?",
  "choices_number": 4,
  "marks": 2.0,
  "choices": [
    {"id": 1, "label": "A", "text": "Nucleus", "is_correct": false},
    {"id": 2, "label": "B", "text": "Mitochondria", "is_correct": true},
    {"id": 3, "label": "C", "text": "Ribosome", "is_correct": false},
    {"id": 4, "label": "D", "text": "Golgi apparatus", "is_correct": false}
  ]
}
```

### A.4 Student Endpoints

| # | Method | Path | Description |
|---|--------|------|-------------|
| 9 | GET | `/api/students` | List all students |
| 10 | POST | `/api/students` | Register a new student |
| 11 | GET | `/api/students/<student_id>` | Get a single student by ID |

**Example Request (Create Student):**
```
POST /api/students
Content-Type: application/json

{
  "name": "Amina Boucherit",
  "matricule": "202312345",
  "email": "amina.b@university.dz"
}
```

**Example Response (201):**
```json
{
  "id": 1,
  "name": "Amina Boucherit",
  "matricule": "202312345",
  "email": "amina.b@university.dz"
}
```

### A.5 Scanning and Grading Endpoints

| # | Method | Path | Description |
|---|--------|------|-------------|
| 12 | POST | `/api/scan/upload` | Upload and scan an answer sheet image |
| 13 | GET | `/api/results/exam/<exam_id>` | Get all results for an exam |
| 14 | POST | `/api/results` | Save a grading result |

**Example Request (Upload Scan):**
```
POST /api/scan/upload
Content-Type: multipart/form-data

file: [answer_sheet.png]
exam_id: 1
```

**Example Response (200):**
```json
{
  "exam_id": 1,
  "total_marks": 20,
  "obtained_marks": 16,
  "percentage": 80.0,
  "answered": 10,
  "total_questions": 10,
  "details": [
    {"question_id": 1, "detected": "B", "correct": "B", "is_correct": true, "marks": 2},
    {"question_id": 2, "detected": "A", "correct": "C", "is_correct": false, "marks": 2}
  ]
}
```

### A.6 AI Endpoints

| # | Method | Path | Description |
|---|--------|------|-------------|
| 15 | GET | `/api/ai/status` | Get AI model status (loaded, device, memory) |
| 16 | POST | `/api/ai/ocr` | Extract handwritten text from an image |
| 17 | POST | `/api/ai/evaluate` | Evaluate a student answer against criteria |
| 18 | POST | `/api/ai/correct` | Submit a teacher correction (RAG) |
| 19 | GET | `/api/ai/corrections/<question_id>` | List corrections for a question |

**Example Request (OCR):**
```
POST /api/ai/ocr
Content-Type: multipart/form-data

file: [exam_page.png]
questions: [1, 2, 3]
```

**Example Response (200):**
```json
{
  "answers": [
    {"question": 1, "text": "La mitochondrie est l'organite qui produit l'ATP"},
    {"question": 2, "text": "Le noyau contient l'ADN"},
    {"question": 3, "text": "La photosynthese se deroule dans le chloroplaste"}
  ]
}
```

**Example Request (Evaluate):**
```
POST /api/ai/evaluate
Content-Type: application/json

{
  "question_id": 1,
  "student_text": "La mitochondrie est l'organite qui produit l'ATP",
  "mode": "model_answer"
}
```

**Example Response (200):**
```json
{
  "score": 3.5,
  "max": 4,
  "feedback": "Correct identification of the mitochondria. Missing mention of the process (oxidative phosphorylation).",
  "confidence": 0.85
}
```

**Example Request (Correct):**
```
POST /api/ai/correct
Content-Type: application/json

{
  "question_id": 1,
  "student_text": "La mitochondrie est l'organite qui produit l'ATP",
  "ai_score": 3.5,
  "ai_feedback": "Missing process name",
  "teacher_score": 4.0,
  "teacher_feedback": "Full marks: student correctly identified the organelle. Process name not required at this level."
}
```

**Example Response (201):**
```json
{
  "id": 1,
  "question_id": 1,
  "student_text": "La mitochondrie est l'organite qui produit l'ATP",
  "ai_score": 3.5,
  "ai_feedback": "Missing process name",
  "teacher_score": 4.0,
  "teacher_feedback": "Full marks: student correctly identified the organelle. Process name not required at this level.",
  "created_at": "2026-04-06T10:30:00"
}
```

---

## Appendix B: Database Schema

The SmartGrader database uses SQLite and comprises seven tables with foreign key constraints and cascade deletion rules. The following SQL statements define the complete schema.

### B.1 Core Tables

```sql
PRAGMA foreign_keys = ON;

-- Students
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    matricule TEXT UNIQUE NOT NULL,
    email TEXT
);

-- Exams
CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    subject TEXT,
    date TEXT,
    total_marks REAL
);

-- Questions
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_choices_number INTEGER NOT NULL,
    marks REAL NOT NULL,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
);

-- Choices
CREATE TABLE IF NOT EXISTS choices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    choice_label TEXT NOT NULL,
    choice_text TEXT NOT NULL,
    is_correct INTEGER DEFAULT 0,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- Student Answers
CREATE TABLE IF NOT EXISTS student_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_choice_id INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY (selected_choice_id) REFERENCES choices(id)
);

-- Results
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
```

### B.2 AI Corrections Table

```sql
-- AI Corrections (RAG feedback loop)
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

### B.3 Indexes

```sql
CREATE INDEX IF NOT EXISTS idx_questions_exam ON questions(exam_id);
CREATE INDEX IF NOT EXISTS idx_choices_question ON choices(question_id);
CREATE INDEX IF NOT EXISTS idx_answers_student ON student_answers(student_id);
CREATE INDEX IF NOT EXISTS idx_answers_question ON student_answers(question_id);
CREATE INDEX IF NOT EXISTS idx_results_exam ON results(exam_id);
```

### B.4 Entity-Relationship Summary

The database follows a hierarchical structure centred on the `exams` table. Each exam contains multiple questions, each question contains multiple choices, and students submit answers that reference specific choices. Results aggregate scores at the exam-student level. The `ai_corrections` table is linked to individual questions and stores the feedback loop data for RAG-based improvement.

All foreign keys use `ON DELETE CASCADE` to maintain referential integrity: deleting an exam automatically removes all associated questions, choices, student answers, and results.

---

## Appendix C: Installation Guide

This appendix provides step-by-step instructions for installing and running SmartGrader on a local machine.

### C.1 Prerequisites

- **Operating System:** Windows 10/11 or Linux (Ubuntu 22.04+)
- **Python:** 3.10 or higher
- **Node.js:** 18 or higher (for frontend build)
- **GPU:** NVIDIA GPU with at least 6 GB VRAM and CUDA 12.x drivers (required for AI grading only)
- **wkhtmltopdf:** Required for PDF answer sheet generation

### C.2 Python Environment Setup

```bash
# Clone the repository
git clone https://github.com/your-org/SmartGrader.git
cd SmartGrader

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install Python dependencies
pip install -r requirements.txt
```

The `requirements.txt` file includes Flask, SQLAlchemy, Flask-Migrate, Flask-CORS, OpenCV (opencv-python-headless), NumPy, pdfkit, and pytest. The AI dependencies (PyTorch, transformers, bitsandbytes, accelerate) are listed in a separate `requirements-ai.txt` file.

### C.3 CUDA and PyTorch Setup

AI grading requires a CUDA-compatible GPU. Install the appropriate PyTorch version for your CUDA driver:

```bash
# For CUDA 12.1 (check your driver version with nvidia-smi)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install AI dependencies
pip install -r requirements-ai.txt
```

Verify GPU availability:

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### C.4 Vision Model Download

The Qwen2.5-VL-3B-Instruct model is downloaded automatically on first use. Alternatively, pre-download it:

```bash
python -c "
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
Qwen2VLForConditionalGeneration.from_pretrained('Qwen/Qwen2.5-VL-3B-Instruct')
AutoProcessor.from_pretrained('Qwen/Qwen2.5-VL-3B-Instruct')
"
```

The model files are cached in `~/.cache/huggingface/hub/` and require approximately 6 GB of disk space (before quantisation).

### C.5 wkhtmltopdf Installation

**Windows:**

Download and install from https://wkhtmltopdf.org/downloads.html. Add the installation directory to the system PATH.

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install wkhtmltopdf
```

### C.6 Database Initialisation

```bash
# Initialise the database (creates instance/smart_grader.db)
flask db upgrade

# Alternatively, initialise from the raw SQL schema
sqlite3 instance/smart_grader.db < schema.sql
```

### C.7 Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

The frontend development server starts on `http://localhost:5173` and proxies API requests to the Flask backend.

### C.8 Running the Application

```bash
# Terminal 1: Start the Flask backend
flask run --host=0.0.0.0 --port=5000

# Terminal 2: Start the React frontend (development)
cd frontend && npm run dev

# Or build for production
cd frontend && npm run build
```

For production deployment, the frontend build output (`frontend/dist/`) can be served by Flask or a dedicated web server (Nginx, Apache).

### C.9 Running Tests

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run a specific test module
pytest tests/test_models/

# Run tests with coverage report
pytest --cov=app --cov-report=html
```

---

## Appendix D: User Manual

This appendix provides a step-by-step guide for using each page of the SmartGrader application.

### D.1 Dashboard

The Dashboard page is the landing page of the application. It displays:

- **Summary statistics:** total number of examinations, total number of students, average grading percentage, and number of recent grading sessions.
- **Score distribution chart:** a bar chart (Recharts) showing the distribution of student scores across percentage ranges (0--20%, 20--40%, 40--60%, 60--80%, 80--100%).
- **Recent examinations:** a list of the five most recently created or graded examinations with their titles, dates, and question counts.

No user action is required on this page; it updates automatically when data changes in other parts of the application.

<!-- Figure D.1: Dashboard page -->

### D.2 Exams

The Exams page displays a sortable, searchable table of all examinations.

**To create a new examination:**

1. Click the "New Exam" button in the top-right corner.
2. Fill in the examination title (required), subject, date, and total marks.
3. Click "Create" to save the examination.

**To edit an examination:**

1. Click the edit icon on the examination row.
2. Modify the desired fields.
3. Click "Save" to apply changes.

**To delete an examination:**

1. Click the delete icon on the examination row.
2. Confirm the deletion in the dialog. Note: this permanently deletes all associated questions, choices, student answers, and results.

<!-- Figure D.2: Exams page -->

### D.3 Exam Detail

The Exam Detail page displays a single examination's metadata and its questions. Navigate to this page by clicking an examination title in the Exams list.

**To add a question:**

1. Click "Add Question" below the questions list.
2. Enter the question text, number of choices, and marks allocated.
3. For each choice, enter the label (A, B, C, D), text, and select the correct answer.
4. Click "Save Question" to add the question to the examination.

**To generate an answer sheet:**

1. Ensure the examination has at least one question.
2. Click "Generate Sheet" to produce a printable A4 PDF answer sheet.
3. The PDF opens in a new browser tab for printing.

<!-- Figure D.3: Exam Detail page -->

### D.4 Scanner -- MCQ Tab

The Scanner page provides two tabs: MCQ and AI. The MCQ tab processes scanned MCQ answer sheets.

**To scan an MCQ answer sheet:**

1. Select the MCQ tab.
2. Select the examination from the dropdown menu.
3. Click "Upload" or drag and drop the scanned answer sheet image (PNG, JPG, or PDF).
4. The system processes the image and displays the detected answers with a visual overlay showing detected bubbles.
5. Review the results: correct answers are highlighted in green, incorrect in red, and unanswered questions in grey.
6. Optionally, select a student from the dropdown to associate the result.
7. Click "Save Result" to persist the grading.

<!-- Figure D.4: Scanner MCQ tab -->

### D.5 Scanner -- AI Tab

The AI tab processes handwritten answer sheets using the vision-language model.

**To grade a handwritten answer sheet:**

1. Select the AI tab.
2. Verify that the AI model is loaded (the status indicator in the top-right shows "Model Loaded" in green). If not loaded, the model will load automatically on first use (approximately 15 seconds).
3. Select the examination and the specific question to evaluate.
4. Upload the scanned page containing the student's handwritten answer.
5. Click "Run OCR" to extract the handwritten text. The extracted text appears in the OCR result panel.
6. Review the extracted text for accuracy. If the OCR result is incorrect, manually edit the text.
7. Click "Evaluate" to score the extracted answer against the question's grading criteria.
8. Review the AI's score, feedback, and confidence level.
9. If the AI's score is incorrect, enter the correct score and optional feedback in the correction form, then click "Submit Correction." This correction is stored for the RAG feedback loop and will improve future evaluations.

<!-- Figure D.5: Scanner AI tab -->

### D.6 Students

The Students page manages the student registry.

**To register a new student:**

1. Click "Add Student" in the top-right corner.
2. Enter the student's name (required), matricule (required, must be unique), and email (optional).
3. Click "Save" to register the student.

**To search for a student:**

1. Type the student's name or matricule in the search field.
2. The table filters in real time as you type.

<!-- Figure D.6: Students page -->

### D.7 Results

The Results page displays grading results with filtering and sorting capabilities.

**To view results for a specific examination:**

1. Select the examination from the filter dropdown.
2. The table displays all students' scores for that examination, sorted by percentage (highest first).

**To view all results:**

1. Clear the examination filter to display results across all examinations.
2. Click column headers to sort by student name, examination title, score, percentage, or grading date.

<!-- Figure D.7: Results page -->

### D.8 Settings

The Settings page provides application configuration options.

**Theme selection:**

1. Click the theme toggle button to switch between light and dark modes.
2. The theme preference is saved automatically and persists across browser sessions.

**AI model status:**

1. The Settings page displays the current AI model status: model name, loaded state, GPU device, and VRAM usage.
2. If the model is not loaded, it will be loaded automatically when an AI grading request is made.

**Scanner configuration:**

1. Advanced users can adjust scanner thresholds (fill threshold, area bounds, circularity minimum) from the Settings page.
2. Changes take effect on the next scanning operation.

<!-- Figure D.8: Settings page -->
