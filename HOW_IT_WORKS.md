# How SmartGrader Works

A technical overview of the system architecture, scanning pipeline, AI grading flow, online exam engine, and anti-cheat proctoring.

## System Architecture

```
Browser (React 19)          Flask API (Python)                  Storage
+--------------------+      +-------------------------+         +-------------+
| Dashboard          |      | Auth / Admin            |         | SQLite DB   |
| Exams              | <--> | /api/exams              | <-----> | (~15 tables)|
| Scanner            | JWT  | /api/students           |         +-------------+
| Students           | HTTP | /api/scan/upload        |
| Results            | JSON | /api/results            |         +-------------+
| Login              |      | /api/groups             |         | Qwen2.5-VL  |
| ExamTaking         |      | /api/sessions           | <-----> | (GPU/CUDA)  |
| TeacherMonitor     |      | /api/student/exams      |         +-------------+
| AdminPanel         |      | /api/ai/*               |
+--------------------+      +-------------------------+         +-------------+
        |                                                        | uploads/    |
        | TensorFlow.js                                          | (snapshots) |
        | (face detection,                                       +-------------+
        |  event tracking)
        v
  ProctorClient (browser)
```

**Four-tier design:**
1. **React SPA** -- Handles all UI, state management (TanStack Query), routing, and in-browser proctoring
2. **Flask API** -- Thin HTTP layer over service modules, JWT auth middleware, no business logic in routes
3. **Services** -- All logic lives here: exam CRUD, scanner pipeline, grading, auth, session lifecycle, proctor events
4. **Storage** -- SQLite for structured data, filesystem for uploaded images and webcam snapshots

## Authentication Flow

```
Teacher/Admin                   Student
     |                             |
     | POST /api/auth/login        | POST /api/auth/student-login
     | {email, password}           | {barcode}
     |                             |
     v                             v
 bcrypt verify              Lookup by barcode
     |                             |
     +----------JWT issue----------+
                  |
        httpOnly cookie (SameSite=Strict)
                  |
        Subsequent requests carry cookie automatically
                  |
        @require_auth decorator verifies JWT, injects g.current_user
        @require_role('teacher') / @require_role('admin') enforces roles
```

Passwords are hashed with bcrypt (cost factor 12). JWTs are short-lived and stored only in httpOnly cookies -- never in localStorage or sessionStorage. Rate limiting (Flask-Limiter) prevents brute-force attacks on login endpoints.

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

## Online Exam System

The online exam engine allows teachers to assign exams to student groups with configurable delivery and submission settings.

```
Teacher creates ExamSession
  |-- links to Exam
  |-- links to StudentGroup (class)
  |-- sets: start_time, end_time, display_mode, save_mode,
  |         randomize, result_visibility, cheat_response
  |
  v
Students in the group see the exam in their portal
  |
  v
Student clicks Start --> ExamAttempt created, timer begins
  |
  |-- display_mode=all_at_once  --> Full paper rendered at once
  |-- display_mode=one_by_one   --> One question at a time, Next button
  |
  v
Student answers questions
  |-- save_mode=auto_each     --> POST /answer on every selection
  |-- save_mode=auto_periodic --> Periodic background POST every N seconds
  |-- save_mode=manual        --> Answers held client-side until Submit
  |
  v
Timer expires OR student clicks Submit
  --> POST /submit
  --> Server marks attempt as submitted, grades MCQ answers immediately
  --> Result visibility applies: none / score_only / score_and_answers

Teacher monitors via GET /sessions/:id/monitor
  --> Live list: who started, who submitted, elapsed time, cheat event count
```

### Randomization

When `randomize=true`, the server generates a per-student permutation of question order and choice order at attempt start. The permutation is stored in `ExamAttempt` so results can be mapped back to canonical question numbering for grading.

### Auto-Submit on Expiry

The server records `started_at` in `ExamAttempt`. Any answer-save or submit request after `started_at + duration` is rejected. A background job (or on next request) auto-submits attempts that exceeded the window.

## Anti-Cheat & Proctoring System

Proctoring runs entirely in the browser during an exam attempt and reports to the server.

```
Student Browser (ExamTaking page)
  |
  +-- TensorFlow.js BlazeFace
  |     Polls webcam every 2 seconds
  |     Detects: no face, multiple faces
  |     --> POST /proctor/event {type: "face_absent" | "multiple_faces", ...}
  |     --> POST /proctor/snapshot (base64 JPEG) on each event
  |
  +-- DOM Event Listeners
  |     visibilitychange  --> tab switch
  |     blur              --> window focus loss
  |     copy/paste        --> clipboard events
  |     keydown           --> blocked shortcuts (Ctrl+C, Alt+Tab, F12, etc.)
  |     --> POST /proctor/event {type: "tab_switch" | "focus_loss" | ...}
  |
  +-- Periodic Snapshot (every 60 seconds)
  |     --> POST /proctor/snapshot (base64 JPEG)
  |
  +-- Full-Screen Lockdown (if enabled)
        requestFullscreen() on attempt start
        fullscreenchange listener --> event if exited

Server actions per cheat_response setting:
  log_only       --> Store ProctorEvent, no visible effect
  warn           --> Return {action: "warn"} in response; client shows warning overlay
  warn_escalate  --> Return {action: "block"} after N warnings; client freezes exam

Teacher actions:
  GET  /sessions/:id/proctor         --> list all events for session
  POST /sessions/:id/proctor/snapshot --> insert CaptureRequest
  Student browser polls for CaptureRequest and uploads snapshot immediately
```

### Stored Data

| Model | What it stores |
|-------|----------------|
| ProctorEvent | type, timestamp, attempt_id, metadata (face count, key pressed) |
| ProctorSnapshot | image path, timestamp, trigger (periodic/event/teacher_request) |
| CaptureRequest | session_id, requested_at, fulfilled_at |

## Database Schema

~15 tables with cascading foreign keys:

```
users (id, email, password_hash, role, is_active)

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

students (id, name, matricule, email, barcode)

student_groups (id, name, teacher_id)
  |
  +-- student_group_members (group_id, student_id)

exam_sessions (id, exam_id, group_id, start_time, end_time,
               display_mode, save_mode, randomize, result_visibility,
               cheat_response)
  |
  +-- exam_assignments (session_id, student_id)
  |
  +-- exam_attempts (id, session_id, student_id, started_at, submitted_at,
  |                  question_order, choice_order, score)
  |     |
  |     +-- online_answers (id, attempt_id, question_id, selected_choice_id, answered_at)
  |     |
  |     +-- proctor_events (id, attempt_id, type, timestamp, metadata)
  |     |
  |     +-- proctor_snapshots (id, attempt_id, image_path, timestamp, trigger)
  |
  +-- capture_requests (id, session_id, requested_at, fulfilled_at)
```

## Frontend Architecture

```
React 19 + Vite
  |
  +-- Pages (20+)
  |     Authentication: Login
  |     Teacher: Dashboard, Exams, ExamDetail, Scanner, Students, Results,
  |              TeacherMonitor, Settings, Documentation, AcademicDocs,
  |              AIConfig, SampleData, LegacyCode, Help, AdminPanel
  |     Student: StudentPortal, ExamTaking
  |
  +-- Hooks (TanStack Query)
  |     useExams, useStudents, useResults, useAI, useSession, useProctor
  |     Auto-caching (30s stale time), optimistic updates, cache invalidation
  |
  +-- Components
  |     Layout: AppLayout, Sidebar (grouped nav), TopBar (glass header)
  |     Auth: LoginForm, BarcodeScan
  |     Exam Taking: QuestionNavigator, CountdownTimer, AnswerGrid, ProctorOverlay
  |     Proctoring: FaceDetector (TF.js BlazeFace), EventTracker, SnapshotUploader
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

~40 endpoints across 10+ resource groups:

| Group | Endpoints | Key Operations |
|-------|-----------|---------------|
| Auth | 4 | Login (teacher + student), logout, current user |
| Admin | 3 | Teacher management, CSV student import |
| Exams | 5 | CRUD + statistics |
| Questions | 2 | List + create with choices |
| Students | 3 | CRUD |
| Scanning | 1 | Upload image, detect bubbles, grade |
| Results | 2 | List by exam + save |
| Groups | 4 | CRUD + member management |
| Sessions | 5 | Teacher session management + live monitor |
| Student Exam | 5 | Start, answer, submit, proctor event, snapshot |
| AI | 5 | Status, OCR, evaluate, correct, list corrections |

## Deployment Modes

| Mode | Command | Use Case |
|------|---------|----------|
| Development | `python run.py` + `npm run dev` | Local development, two processes |
| LAN | `python run.py --lan` | Classroom, single process serves frontend |
| LAN + SSL | `python run.py --lan --ssl` | Classroom with self-signed HTTPS |
| University | Gunicorn + Nginx + systemd | Production server |
| Docker | `docker-compose up -d` | Containerized, portable deployment |

## Print & Export

- **QCM Sheet Print** -- Opens a new window with the exact A4 answer sheet template (alignment marks, bubble circles, student boxes) and triggers browser print
- **Result Certificate** -- Generates an A4 printable result card with student name, exam, score, pass/fail
- **CSV Export** -- Downloads results as a CSV file
- **Thesis PDF** -- Built from Markdown via xhtml2pdf (Python) or Pandoc (LaTeX)
