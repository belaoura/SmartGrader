# Chapter 3: Analysis and Design

This chapter presents the requirements analysis and system design for SmartGrader. We begin by defining the functional and non-functional requirements derived from the problem statement in Chapter 1 and the gaps identified in Chapter 2. We then describe the system architecture, database schema, REST API specification, AI grading pipeline, authentication architecture, online examination flow, and anti-cheat architecture. UML diagrams formalise the design throughout.

## 3.1 Functional Requirements

The functional requirements of SmartGrader are organised around the activities of three primary actors: the **Teacher** (who manages examinations, monitors sessions, and reviews results), the **Student** (who takes online examinations and whose paper sheets are processed), and the **System** (which performs automated processing, proctoring, and enforcement).

### 3.1.1 Use Case Diagram

The use case diagram in Figure 3.1 illustrates the principal interactions between actors and system functions.

![Use Case Diagram](../figures/generated/use-case.png)

*Figure 3.1: Use Case Diagram for SmartGrader*

### 3.1.2 Use Case Descriptions

The following use case descriptions elaborate the principal functional requirements:

**UC-01: Manage Examinations.** The teacher creates a new examination by specifying a title, subject, date, and total marks. The teacher can view the list of all examinations, edit an existing examination's metadata, or delete an examination. Deleting an examination cascades to all associated questions, choices, student answers, and results.

**UC-02: Manage Questions.** For each examination, the teacher defines one or more questions. Each question specifies the question text, the number of answer choices, and the marks allocated to the question. For MCQ questions, the teacher defines the choice labels (A, B, C, D, etc.), choice texts, and designates the correct answer(s).

**UC-03: Generate Answer Sheet.** The system generates a printable A4 answer sheet in PDF format for the examination. The sheet includes OMR alignment markers, a student identification section, and a grid of answer bubbles corresponding to the examination's questions. The layout is computed dynamically based on the number of questions and choices.

**UC-04: Manage Students.** The teacher registers students in the system by providing their name, matriculation number (matricule), and optionally their email address. The matriculation number serves as a unique identifier. Students may also be imported in bulk via a CSV file.

**UC-05: Scan MCQ Answer Sheets.** The teacher uploads a scanned image of a completed answer sheet. The scanner pipeline preprocesses the image (greyscale conversion, adaptive thresholding, morphological cleaning), detects the four corner markers, establishes a coordinate transformation, locates the answer bubbles, determines which bubbles are filled, maps the detected answers to questions, and computes the score by comparison with the correct answers.

**UC-06: AI-Assisted Grading.** The teacher uploads a scanned image of a handwritten answer sheet and selects a question for evaluation. The AI pipeline performs two stages: first, the OCR stage extracts the student's handwritten text using the vision language model; second, the evaluation stage scores the extracted text against the model answer and grading criteria. The teacher can review and optionally correct the AI's output.

**UC-07: Submit Correction.** When the teacher disagrees with the AI-assigned score, they submit a correction specifying the correct score and optional feedback. This correction is stored in the database and used by the RAG mechanism to improve future evaluations of the same question.

**UC-08: View Results.** The teacher views grading results aggregated by examination, including individual student scores, percentages, and grading timestamps.

**UC-09: Authenticate.** Users (teachers and students) authenticate using a username and password. Upon successful authentication, the system issues a signed JWT containing the user's identity and role. The JWT is presented on all subsequent requests. Students may also authenticate by scanning a personal barcode that encodes their student identifier.

**UC-10: Create Student Groups.** The teacher creates named groups of students to facilitate the assignment of examination sessions. Groups can be created manually or populated by selecting students from the registry.

**UC-11: Schedule Online Exam Session.** The teacher schedules an online examination session by associating an existing examination with a student group, setting a start time and duration, and activating the session. Once active, enrolled students can access the examination through the student interface during the allotted window.

**UC-12: Take Online Exam.** An authenticated student navigates to the active examination session. The student interface presents questions sequentially or all at once, with a countdown timer showing remaining time. Each answer is persisted to the server as the student progresses. When the timer expires or the student submits manually, the examination is finalised and no further changes are permitted. The system grades MCQ questions automatically upon submission.

**UC-13: Monitor Proctoring.** The teacher accesses the proctoring dashboard during an active session to monitor all enrolled students. The dashboard displays the live status of each student (connected, disconnected, warning count), the timeline of proctoring events (face not detected, tab switch, fullscreen exit), and captured webcam snapshots. The teacher can view an individual student's complete event log and snapshots. Upon exceeding a configurable warning threshold, the system automatically flags or terminates the student's session.

## 3.2 Non-Functional Requirements

Beyond the functional capabilities described above, SmartGrader must satisfy the following non-functional requirements:

### 3.2.1 Performance

- **MCQ Scanning:** The scanner pipeline shall process a single scanned answer sheet in under 3 seconds on standard hardware.
- **AI Grading:** The AI pipeline shall complete the OCR and evaluation of a single question in under 5 seconds on a GPU with at least 6 GB of VRAM.
- **API Response Time:** All non-AI API endpoints shall respond within 500 milliseconds under normal load.
- **Online Exam Polling:** Answer persistence and proctoring event submission shall complete within 1 second on a LAN connection.
- **Face Detection Frequency:** The ProctorEngine shall perform a face presence check at a minimum interval of once per second without degrading examination page responsiveness.

### 3.2.2 Accuracy

- **Bubble Detection:** The MCQ scanner shall achieve a bubble detection accuracy of at least 95% on answer sheets scanned at 300 DPI or higher.
- **Handwriting OCR:** The VLM-based OCR shall achieve a character-level accuracy of at least 80% on clearly written handwritten text in Arabic, French, and English.
- **AI Grading:** The AI evaluation shall produce scores within one grade point of the teacher's score for at least 70% of evaluated answers, with this percentage expected to improve through RAG corrections.

### 3.2.3 Hardware Requirements

- **Minimum GPU:** NVIDIA GPU with 6 GB VRAM (e.g., GTX 1660, RTX 3060) for 4-bit quantised model inference.
- **Recommended GPU:** NVIDIA GPU with 8 GB VRAM (e.g., RTX 3070, RTX 4060) for improved inference speed.
- **CPU-Only Mode:** The system shall remain functional without a GPU, with AI features gracefully disabled and appropriate user notification.
- **Storage:** At least 10 GB of free disk space for the model weights, database, and uploaded scan images.
- **Student Devices:** The student examination interface requires only a modern web browser with webcam access for proctoring. No installation is required.

### 3.2.4 Security and Data Integrity

- **Input Validation:** All API endpoints shall validate input data types, lengths, and formats before processing.
- **File Upload Security:** Uploaded files shall be validated against an allowlist of permitted extensions (PDF, PNG, JPG, JPEG, TIFF, BMP) and a maximum file size of 50 MB.
- **Foreign Key Integrity:** The database shall enforce referential integrity through foreign key constraints with cascading deletes where appropriate.
- **Local Processing:** All data processing, including AI inference, shall occur locally on the deployment machine. No student data shall be transmitted to external services.
- **JWT Security:** Access tokens shall be signed with a configurable secret key, set a short expiration (e.g., 24 hours), and carry only the minimum required claims (user ID, role).
- **CORS Policy:** In production mode, the API shall enforce a strict CORS policy limiting cross-origin requests to the configured frontend origin.

## 3.3 System Architecture

SmartGrader follows a layered architecture that separates concerns across four principal tiers: the presentation layer (frontend), the API layer (Flask routes), the business logic layer (services), and the data access layer (models and database).

### 3.3.1 Deployment Architecture

The deployment diagram in Figure 3.2 illustrates the physical arrangement of system components across the three supported deployment modes.

![Deployment Diagram](../figures/generated/deployment.png)

*Figure 3.2: Deployment Diagram*

**Single-Machine (Development/LAN) Mode:** The Flask application is served by the Gunicorn WSGI server, optionally behind an Nginx reverse proxy for LAN deployments. The React frontend is served as static files from Nginx or directly from Flask. The SQLite database resides on the local file system.

**University Server Mode:** The Nginx reverse proxy handles SSL/TLS termination, CORS header injection, and static file serving. Gunicorn runs as a systemd service, accepting requests forwarded from Nginx. Multiple Gunicorn worker processes provide concurrency for simultaneous student sessions.

**Docker Mode:** The application is containerised using Docker Compose with separate services for the Flask backend, Nginx reverse proxy, and an optional database backup cron job. Environment variables configure the deployment-specific secrets, origins, and port bindings.

### 3.3.2 Logical Architecture

The logical architecture follows the Model-Service-Route pattern:

- **Models** (`app/models/`): SQLAlchemy ORM classes that define the database schema and provide data access methods. Each model includes a `to_dict()` method for JSON serialisation.
- **Services** (`app/services/`): Stateless service modules that encapsulate business logic, including examination management, grading computation, scanner pipeline orchestration, AI model interaction, session management, and proctoring event processing.
- **Routes** (`app/routes/`): Flask blueprint modules that define REST API endpoints, handle request parsing and validation, enforce JWT authentication via decorators, and format HTTP responses.
- **Scanner** (`app/scanner/`): A dedicated module implementing the computer vision pipeline for MCQ answer sheet processing.
- **AI** (`app/ai/`): A dedicated module managing the vision language model lifecycle, prompt construction, inference execution, and RAG retrieval.
- **Auth** (`app/auth/`): JWT token generation, validation, and role-enforcement decorators.

### 3.3.3 Authentication Architecture

The JWT authentication flow proceeds as follows:

1. **Login:** The client submits credentials (username + password) to `POST /api/auth/login`. The Auth service verifies the password hash using bcrypt and, on success, generates a signed JWT containing the user's ID, role, and expiration timestamp.
2. **Token Storage:** The React frontend stores the JWT in memory (or optionally in `localStorage`) and attaches it to all subsequent requests via the `Authorization: Bearer <token>` header.
3. **Request Validation:** Flask route decorators (`@require_auth`, `@require_role("teacher")`) intercept each request, extract the token from the header, verify the signature using the application secret key, check the expiration, and inject the decoded user claims into the request context.
4. **Barcode Login:** Students can authenticate by scanning a QR/barcode printed on their identity card. The barcode encodes the student's matricule, which the backend uses to look up the student account and issue a student-role JWT.

### 3.3.4 Online Examination Flow

The online examination subsystem implements the following flow:

1. **Session Creation:** The teacher creates an ExamSession record associating an Exam with a StudentGroup, setting a start time and duration. ExamAssignment records are created for each student in the group.
2. **Session Activation:** On reaching the start time (or on manual teacher activation), the session becomes accessible to enrolled students.
3. **Attempt Initiation:** When a student navigates to the active session, the system creates an ExamAttempt record capturing the start timestamp and setting the status to `in_progress`.
4. **Answer Persistence:** As the student selects answers, each selection triggers a `POST /api/exam/attempt/<id>/answer` request that creates or updates an OnlineAnswer record. Answers are persisted server-side, making the attempt resumable if the student's connection is interrupted.
5. **Auto-Submission:** A JavaScript timer in the browser tracks the remaining time. On expiry, the frontend submits the attempt automatically via `POST /api/exam/attempt/<id>/submit`. The backend also enforces the deadline server-side: attempts exceeding their deadline are finalisd by a background check.
6. **Grading:** On submission, the grading service reads all OnlineAnswer records for the attempt, compares each answer to the correct choice, and computes the total score. The result is stored in the ExamAttempt record.

### 3.3.5 Anti-Cheat Architecture

The anti-cheat system employs a hybrid client-server architecture:

**Client-side (ProctorEngine):** A JavaScript module running within the student examination page:
- Loads TensorFlow.js and the BlazeFace model on session start.
- Runs face detection at a configurable interval (default: 1 second) using the student's webcam stream.
- Detects and reports events: face not detected, multiple faces detected, tab switch (`visibilitychange`), fullscreen exit (`fullscreenchange`), window blur (`blur`), copy-paste attempts (`copy`, `paste` events).
- Captures periodic webcam snapshots (JPEG, configurable interval) and transmits them to the server.
- Maintains a local warning counter; on exceeding the threshold, displays a mandatory warning dialog and optionally triggers auto-submission.

**Server-side (ProctorService):** Receives and persists all ProctorEvent and ProctorSnapshot records. Enforces the maximum warning threshold by marking the attempt as terminated if the threshold is exceeded. Provides the proctoring dashboard API endpoints for teacher consumption.

**Teacher Dashboard:** Polls the server at regular intervals to display the live status of each student. Displays warning counts, event timelines, and snapshot thumbnails. Allows the teacher to manually flag or terminate individual attempts.

## 3.4 Database Design

The SmartGrader database comprises fifteen tables that capture the entities and relationships of the complete examination management domain. The entity-relationship diagram in Figure 3.3 provides a visual representation of the schema.

![Entity-Relationship Diagram](../figures/generated/er-diagram.png)

*Figure 3.3: Entity-Relationship Diagram*

### 3.4.1 Original Core Tables (Phase 1–2)

The following tables constitute the original schema supporting exam management and MCQ scanning.

**Table: `exams`**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique examination identifier |
| `title` | TEXT | NOT NULL | Examination title |
| `subject` | TEXT | | Subject or course name |
| `date` | TEXT | | Examination date (ISO format) |
| `total_marks` | REAL | | Maximum achievable score |

**Table: `questions`**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique question identifier |
| `exam_id` | INTEGER | FK → exams(id) | Parent examination |
| `question_text` | TEXT | NOT NULL | Question text |
| `question_choices_number` | INTEGER | NOT NULL | Number of answer choices (0 = short-answer) |
| `marks` | REAL | NOT NULL | Marks allocated |

**Table: `choices`**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique choice identifier |
| `question_id` | INTEGER | FK → questions(id) | Parent question |
| `choice_label` | TEXT | NOT NULL | Choice label (A, B, C, D) |
| `choice_text` | TEXT | NOT NULL | Choice text |
| `is_correct` | INTEGER | DEFAULT 0 | Correct answer flag |

**Table: `students`**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique student identifier |
| `name` | TEXT | NOT NULL | Student full name |
| `matricule` | TEXT | UNIQUE, NOT NULL | Matriculation number |
| `email` | TEXT | | Email address |

**Table: `student_answers`** — stores MCQ scanner detected answers.

**Table: `results`** — stores aggregated grading outcomes.

**Table: `ai_corrections`** — stores teacher corrections for the RAG feedback loop.

### 3.4.2 New Tables: Authentication (Phase 1)

**Table: `users`**

The `users` table stores credentials for all system users (teachers and students).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique user identifier |
| `username` | TEXT | UNIQUE, NOT NULL | Login username |
| `password_hash` | TEXT | NOT NULL | bcrypt password hash |
| `role` | TEXT | NOT NULL | `teacher` or `student` |
| `student_id` | INTEGER | FK → students(id), NULLABLE | Associated student record (for student accounts) |
| `created_at` | TEXT | NOT NULL | Account creation timestamp |

### 3.4.3 New Tables: Online Examination Engine (Phase 2)

**Table: `student_groups`**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Group identifier |
| `name` | TEXT | NOT NULL | Group name (e.g., "L3 Informatique Groupe A") |
| `description` | TEXT | | Optional description |
| `created_at` | TEXT | NOT NULL | Creation timestamp |

**Table: `group_members`** (association table)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `group_id` | INTEGER | FK → student_groups(id) | Group reference |
| `student_id` | INTEGER | FK → students(id) | Student reference |

**Table: `exam_sessions`**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Session identifier |
| `exam_id` | INTEGER | FK → exams(id) | Examination assigned |
| `group_id` | INTEGER | FK → student_groups(id) | Student group |
| `start_time` | TEXT | NOT NULL | Scheduled start (ISO format) |
| `duration_minutes` | INTEGER | NOT NULL | Allotted duration |
| `status` | TEXT | NOT NULL | `scheduled`, `active`, `closed` |
| `created_at` | TEXT | NOT NULL | Creation timestamp |

**Table: `exam_attempts`**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Attempt identifier |
| `session_id` | INTEGER | FK → exam_sessions(id) | Parent session |
| `student_id` | INTEGER | FK → students(id) | Student |
| `started_at` | TEXT | NOT NULL | Attempt start timestamp |
| `submitted_at` | TEXT | | Submission timestamp (null if in progress) |
| `status` | TEXT | NOT NULL | `in_progress`, `submitted`, `terminated` |
| `score` | REAL | | Computed score (set on submission) |
| `percentage` | REAL | | Score as percentage |

**Table: `online_answers`**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Answer record identifier |
| `attempt_id` | INTEGER | FK → exam_attempts(id) | Parent attempt |
| `question_id` | INTEGER | FK → questions(id) | Question answered |
| `selected_choice_id` | INTEGER | FK → choices(id), NULLABLE | Selected choice |
| `answered_at` | TEXT | NOT NULL | Timestamp of last selection |

### 3.4.4 New Tables: Proctoring (Phase 3)

**Table: `proctor_events`**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Event identifier |
| `attempt_id` | INTEGER | FK → exam_attempts(id) | Associated attempt |
| `event_type` | TEXT | NOT NULL | `face_missing`, `multiple_faces`, `tab_switch`, `fullscreen_exit`, `window_blur`, `copy_paste` |
| `severity` | TEXT | NOT NULL | `warning`, `info` |
| `details` | TEXT | | Additional context (JSON string) |
| `occurred_at` | TEXT | NOT NULL | Event timestamp |

**Table: `proctor_snapshots`**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Snapshot identifier |
| `attempt_id` | INTEGER | FK → exam_attempts(id) | Associated attempt |
| `image_path` | TEXT | NOT NULL | Path to stored JPEG snapshot |
| `face_detected` | INTEGER | NOT NULL | Whether a face was detected in this snapshot (1/0) |
| `captured_at` | TEXT | NOT NULL | Capture timestamp |

### 3.4.5 Database Indexes

The database defines indexes to optimise query performance on the most frequently accessed foreign key and status columns:

- Original indexes: `idx_questions_exam`, `idx_choices_question`, `idx_answers_student`, `idx_answers_question`, `idx_results_exam`
- New indexes: `idx_attempts_session`, `idx_attempts_student`, `idx_online_answers_attempt`, `idx_proctor_events_attempt`, `idx_proctor_snapshots_attempt`, `idx_sessions_status`

## 3.5 API Design

SmartGrader exposes a RESTful API comprising approximately 40 endpoints organised into resource groups. All endpoints are prefixed with `/api/` and return JSON. Protected endpoints require a valid JWT in the `Authorization: Bearer` header.

### 3.5.1 Examination Endpoints (unchanged)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/exams` | List all examinations |
| POST | `/api/exams` | Create a new examination |
| GET | `/api/exams/<id>` | Get a specific examination |
| PUT | `/api/exams/<id>` | Update an examination |
| DELETE | `/api/exams/<id>` | Delete an examination (cascade) |
| GET | `/api/exams/<id>/questions` | List questions for an examination |
| POST | `/api/exams/<id>/questions` | Add a question to an examination |

### 3.5.2 Student and User Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/students` | List all students |
| POST | `/api/students` | Register a student |
| GET | `/api/students/<id>` | Get a student by ID |
| POST | `/api/students/import` | Bulk import students from CSV |

### 3.5.3 Authentication Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | Public | Register a teacher account |
| POST | `/api/auth/login` | Public | Login; returns JWT |
| POST | `/api/auth/barcode-login` | Public | Student barcode login; returns JWT |
| GET | `/api/auth/me` | Required | Get current user profile |
| POST | `/api/auth/logout` | Required | Invalidate token (client-side) |

### 3.5.4 Student Group Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/groups` | Teacher | List all student groups |
| POST | `/api/groups` | Teacher | Create a group |
| GET | `/api/groups/<id>` | Teacher | Get a group with members |
| PUT | `/api/groups/<id>` | Teacher | Update group name/description |
| DELETE | `/api/groups/<id>` | Teacher | Delete a group |
| POST | `/api/groups/<id>/members` | Teacher | Add students to a group |
| DELETE | `/api/groups/<id>/members/<sid>` | Teacher | Remove a student from a group |

### 3.5.5 Exam Session Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/sessions` | Teacher | List all exam sessions |
| POST | `/api/sessions` | Teacher | Create a session |
| GET | `/api/sessions/<id>` | Teacher | Get session details |
| PUT | `/api/sessions/<id>/activate` | Teacher | Activate a scheduled session |
| PUT | `/api/sessions/<id>/close` | Teacher | Close an active session |
| GET | `/api/sessions/<id>/attempts` | Teacher | List all attempts for a session |

### 3.5.6 Student Exam Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/exam/active` | Student | Get the student's active session |
| POST | `/api/exam/attempt` | Student | Begin an examination attempt |
| GET | `/api/exam/attempt/<id>` | Student | Get attempt state and questions |
| POST | `/api/exam/attempt/<id>/answer` | Student | Save or update an answer |
| POST | `/api/exam/attempt/<id>/submit` | Student | Submit the attempt |

### 3.5.7 Proctoring Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/proctor/event` | Student | Report a proctoring event |
| POST | `/api/proctor/snapshot` | Student | Upload a webcam snapshot |
| GET | `/api/proctor/attempt/<id>/events` | Teacher | Get events for an attempt |
| GET | `/api/proctor/attempt/<id>/snapshots` | Teacher | Get snapshots for an attempt |

### 3.5.8 Scanning, Results, and AI Endpoints (unchanged)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/scan/upload` | Upload a scanned answer sheet |
| GET | `/api/results/exam/<id>` | Get results for an examination |
| POST | `/api/results` | Save a grading result |
| GET | `/api/health` | Health check |
| GET | `/api/ai/status` | AI model status |
| POST | `/api/ai/ocr` | OCR on scanned image |
| POST | `/api/ai/evaluate` | Evaluate extracted answer |
| POST | `/api/ai/correct` | Submit teacher correction |
| GET | `/api/ai/corrections/<id>` | List corrections for a question |

## 3.6 AI Pipeline Design

The AI grading pipeline implements a two-stage process -- OCR followed by Evaluation -- augmented by a RAG feedback loop. This design is unchanged from the original system and is documented in full in the previous chapter's sequence diagrams. The pipeline accepts scanned paper answer sheets, not online submissions (which are digital text and are graded directly).

### 3.6.1 Pipeline Overview

**Stage 1: Optical Character Recognition.** The teacher uploads a scanned image and selects the question to be graded. The system sends the full-page image to the Qwen2.5-VL-3B-Instruct model together with an OCR prompt.

**Stage 2: Semantic Evaluation.** The transcribed text is submitted to the model with an evaluation prompt including the question text, model answer, optional keywords, marks, and any retrieved RAG corrections as few-shot examples.

### 3.6.2 RAG Feedback Loop

The RAG feedback loop operates as described in Section 3.6 of the original design: teacher corrections are stored in the `ai_corrections` table and retrieved as few-shot examples on subsequent evaluations of the same question, enabling progressive improvement in grading accuracy without model fine-tuning.

## 3.7 Class Diagram

The class diagram in Figure 3.5 presents the principal classes and their relationships across the backend application, including the new models introduced in Phases 1 through 3.

![Class Diagram](../figures/generated/class-diagram.png)

*Figure 3.5: Class Diagram*

The class diagram reveals the following structural organisation:

**Original Model Classes:** `Exam`, `Question`, `Choice`, `Student`, `StudentAnswer`, `Result`, and `AICorrection` correspond directly to the original seven database tables.

**New Model Classes (Phases 1–3):** `User` (authentication), `StudentGroup`, `GroupMember` (group management), `ExamSession`, `ExamAttempt`, `OnlineAnswer` (online exam engine), `ProctorEvent`, and `ProctorSnapshot` (proctoring).

**Service Classes:** `ExamService`, `GradingService`, `ScannerService`, `AIService`, `AuthService`, `SessionService`, `ExamTakeService`, and `ProctorService` encapsulate the business logic for their respective domains.

**Route Blueprints:** Separate blueprint modules handle each resource group: exams, questions, students, scanning, grading, AI, auth, groups, sessions, student exam, and proctoring.

## 3.8 Sequence Diagrams

### 3.8.1 MCQ Scanning Sequence

The MCQ scanning sequence diagram (Figure 3.6) depicts the flow initiated when a teacher uploads a scanned answer sheet for automated MCQ grading. The pipeline proceeds through preprocessing, marker detection, perspective correction, bubble detection, grid mapping, fill detection, answer comparison, and result return. This is unchanged from the original design.

![MCQ Scanning Sequence Diagram](../figures/generated/sequence-scan.png)

*Figure 3.6: Sequence Diagram for MCQ Scanning*

### 3.8.2 Online Examination Sequence

The online examination sequence proceeds as follows:

1. The teacher activates an exam session via the dashboard.
2. The student authenticates and receives a JWT.
3. The student requests their active session; the server returns session metadata and the list of questions.
4. An ExamAttempt record is created on the server.
5. For each question, the student selects an answer; the frontend sends a `POST /api/exam/attempt/<id>/answer` request that persists the OnlineAnswer record.
6. Concurrently, the ProctorEngine sends `POST /api/proctor/event` requests for detected integrity events and periodic `POST /api/proctor/snapshot` uploads.
7. On timer expiry (client) or deadline enforcement (server), `POST /api/exam/attempt/<id>/submit` is called, triggering automatic MCQ grading and finalisation of the attempt record.

### 3.8.3 AI Grading Sequence

The AI grading sequence (Figure 3.4) follows the two-stage pipeline described in Section 3.6. The key interactions are: OCR request, teacher review, evaluation request with RAG context, score delivery, and optional correction submission.

![AI Grading Sequence Diagram](../figures/generated/sequence-ai-grade.png)

*Figure 3.4: Sequence Diagram for AI-Assisted Grading*
