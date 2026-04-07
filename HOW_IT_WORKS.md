# How SmartGrader Works

A technical overview of the system architecture, scanning pipeline, and AI grading flow.

## System Architecture

```
Browser (React 19)          Flask API (Python)           Storage
+------------------+        +------------------+        +-------------+
| Dashboard        | <----> | /api/exams       | <----> | SQLite DB   |
| Exams            |  HTTP  | /api/students    |        | (7 tables)  |
| Scanner          |  JSON  | /api/scan/upload |        +-------------+
| Students         |        | /api/results     |
| Results          |        | /api/ai/*        | <----> +-------------+
| Settings         |        +------------------+        | Qwen2.5-VL  |
+------------------+                                    | (GPU/CUDA)  |
                                                        +-------------+
```

**Three-tier design:**
1. **React SPA** -- Handles all UI, state management (TanStack Query), routing
2. **Flask API** -- Thin HTTP layer over service modules, no business logic in routes
3. **Services** -- All logic lives here: exam CRUD, scanner pipeline, grading, AI evaluation

## MCQ Optical Scanning Pipeline

When a teacher uploads a scanned answer sheet, OpenCV processes it in 5 stages:

```
Scanned Image
     |
     v
[1. Preprocessor]  -- Deskew, crop, grayscale, adaptive threshold
     |                 (app/scanner/preprocessor.py)
     v
[2. Marker Finder] -- Detect triangle alignment markers at corners
     |                 (app/scanner/marker_finder.py)
     v
[3. Detector]      -- Find bubble contours, filter by area + circularity
     |                 (app/scanner/detector.py)
     v
[4. Grid Mapper]   -- Map bubbles to question/choice grid coordinates
     |                 (app/scanner/grid_mapper.py)
     v
[5. Answer Reader] -- Apply FILL_THRESHOLD to determine selected answers
     |                 (app/scanner/answer_reader.py)
     v
Detected Answers --> Compare with answer key --> Score + Result
```

### Key Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| FILL_THRESHOLD | 0.35 | Min fill ratio for a bubble to be "selected" |
| CIRCLE_AREA_MIN | 100 | Min contour area (px^2) to be a bubble |
| CIRCLE_AREA_MAX | 5000 | Max contour area to filter noise |
| CIRCULARITY_MIN | 0.5 | Min circularity score (4*pi*area/perimeter^2) |

### Answer Sheet Format

The printable QCM sheet includes:
- **Corner alignment marks** -- 3mm black squares for deskew/registration
- **Triangle section markers** -- Top and bottom of the question area
- **Header** -- Institution, department, exam title, subject, date
- **Student section** -- Name boxes (20 chars), ID boxes (14 digits), QR area
- **Two-column question grid** -- Questions with empty bubble circles (O)
- **Page numbers** -- Multi-page support (8 questions per page)

## AI Short Answer Grading

For handwritten/typed short answers, the AI pipeline has 3 stages:

```
Student Answer Image
     |
     v
[Stage 1: OCR]
  Model: Qwen2.5-VL-3B-Instruct (4-bit quantized)
  Input: Cropped image of student's answer
  Output: Extracted text
  Prompt: "Extract the handwritten text from this image..."
     |
     v
[Stage 2: Evaluation]
  Input: Extracted text + question + reference answer
  Mode: model_answer (compare to ideal) or keywords (check key terms)
  Output: Score (0 to max_marks) + feedback + confidence (0-1)
  Prompt: "Evaluate this student answer against the model answer..."
     |
     v
[Stage 3: RAG Correction Loop]
  If confidence < 0.7: flagged for teacher review
  Teacher submits correction (correct score + feedback)
  Correction stored in ai_corrections table
  Future evaluations retrieve similar corrections to improve accuracy
     |
     v
Score + Feedback --> Saved as Result
```

### Model Configuration

| Setting | Value |
|---------|-------|
| Model | Qwen/Qwen2.5-VL-3B-Instruct |
| Quantization | 4-bit NF4 (BitsAndBytes) |
| VRAM Usage | ~6-8 GB |
| Load Time | ~15 seconds |
| OCR Speed | ~3-5 seconds per image |
| Evaluation Speed | ~2 seconds per answer |

## Database Schema

7 tables with cascading foreign keys:

```
exams (id, title, subject, date, total_marks)
  |
  +-- questions (id, exam_id, question_text, marks)
  |     |
  |     +-- choices (id, question_id, label, text, is_correct)
  |     |
  |     +-- student_answers (id, student_id, question_id, selected_choice_id)
  |     |
  |     +-- ai_corrections (id, question_id, student_text, ai_score, teacher_score, ...)
  |
  +-- results (id, student_id, exam_id, score, percentage, graded_at)

students (id, name, matricule, email)
```

## Frontend Architecture

```
React 19 + Vite
  |
  +-- Pages (Dashboard, Exams, ExamDetail, Scanner, Students, Results, Settings,
  |          Documentation, AcademicDocs, AIConfig, SampleData, LegacyCode, Help)
  |
  +-- Hooks (TanStack Query)
  |     useExams, useStudents, useResults, useAI
  |     Auto-caching (30s stale time), optimistic updates, cache invalidation
  |
  +-- Components
  |     Layout: AppLayout, Sidebar (grouped nav), TopBar (glass header)
  |     Tables: Card-row design with pagination, hover actions, print buttons
  |     Modals: Markdown, JSON, PlantUML, Image preview (createPortal to body)
  |     Charts: Recharts (BarChart, PieChart with indigo/emerald colors)
  |
  +-- Theme
        Glassmorphism (backdrop-blur, translucent cards)
        Indigo primary + Emerald success
        Poppins headings + Open Sans body
        Light/Dark mode via CSS variables + data-theme attribute
```

## API Endpoints

18 endpoints across 7 resource groups:

| Group | Endpoints | Key Operations |
|-------|-----------|---------------|
| Exams | 5 | CRUD + statistics |
| Questions | 2 | List + create with choices |
| Students | 3 | CRUD |
| Scanning | 1 | Upload image, detect bubbles, grade |
| Results | 2 | List by exam + save |
| AI | 5 | Status, OCR, evaluate, correct, list corrections |
| Files | 1 | Serve static files (docs, old files, debug output) |

## Print & Export

- **QCM Sheet Print** -- Opens a new window with the exact A4 answer sheet template (alignment marks, bubble circles, student boxes) and triggers browser print
- **Result Certificate** -- Generates an A4 printable result card with student name, exam, score, pass/fail
- **CSV Export** -- Downloads results as a CSV file
- **Thesis PDF** -- Built from Markdown via xhtml2pdf (Python) or Pandoc (LaTeX)
