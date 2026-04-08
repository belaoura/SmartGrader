# TODO

## Sub-Project 1: Code Restructuring (Complete)
- [x] Project scaffolding and tooling
- [x] Configuration system
- [x] Custom exceptions and logging
- [x] SQLAlchemy models
- [x] Database migration from legacy
- [x] Exam service layer
- [x] Grading service layer
- [x] Scanner consolidation
- [x] Sheet generator service
- [x] Flask routes (API)
- [x] Test suite (40 tests passing)
- [x] Entry point and smoke test

## Sub-Project 2: Web UI (Complete)
- [x] Flask backend with blueprints
- [x] React frontend scaffold
- [x] Dashboard page
- [x] Exam management pages
- [x] Scanner upload page
- [x] Results and statistics pages
- [x] Glassmorphism UI redesign (indigo/emerald, backdrop-blur)
- [x] Dark mode support (CSS variables, Tailwind classes)
- [x] Pagination (all tables, 5 items/page)
- [x] Print functionality (QCM sheets, result certificates)
- [x] Academic Docs viewer (thesis chapters, UML diagrams)

## Sub-Project 3: AI Vision Model (Complete)
- [x] Model loader (Qwen2.5-VL-3B with 4-bit quantization)
- [x] OCR pipeline for handwriting extraction
- [x] Answer evaluator with prompt templates
- [x] RAG feedback loop with ai_corrections table
- [x] Confidence threshold and teacher review flow

## Sub-Project 4: Academic Documentation (Complete)
- [x] Chapter 1: General Introduction
- [x] Chapter 2: State of the Art
- [x] Chapter 3: Analysis & Design (UML diagrams)
- [x] Chapter 4: Implementation
- [x] Chapter 5: Testing & Results
- [x] Chapter 6: Conclusion & Perspectives
- [x] 7 PlantUML UML diagrams
- [x] BibTeX bibliography (18 references)
- [x] Appendices (API reference, DB schema, installation guide, user manual)
- [x] Pandoc build script (PDF + DOCX)

## Phase 1: Authentication & User Management (Complete)
- [x] JWT auth with httpOnly cookies
- [x] Teacher login (email/password with bcrypt)
- [x] Student login (barcode scan)
- [x] Role-based access control (teacher, student, admin)
- [x] Admin teacher management (create, edit, deactivate)
- [x] CSV bulk student import
- [x] Rate limiting on auth endpoints (Flask-Limiter)
- [x] User model
- [x] /api/auth/* and /api/admin/* routes
- [x] create_admin CLI script

## Phase 2: Online Exam Engine (Complete)
- [x] StudentGroup and StudentGroupMember models
- [x] ExamSession model with all configuration fields
- [x] ExamAssignment model (session-to-student)
- [x] ExamAttempt model with randomization fields
- [x] OnlineAnswer model with timestamps
- [x] Display modes: all_at_once, one_by_one
- [x] Save modes: auto_each, auto_periodic, manual
- [x] Question and choice randomization per student
- [x] Result visibility configuration
- [x] Countdown timer with auto-submit on expiry
- [x] Server-side attempt expiry enforcement
- [x] Teacher live monitoring dashboard
- [x] /api/groups/*, /api/sessions/*, /api/student/exams/* routes

## Phase 3: Anti-Cheat & Proctoring (Complete)
- [x] ProctorEvent model
- [x] ProctorSnapshot model
- [x] CaptureRequest model
- [x] TensorFlow.js BlazeFace face detection (browser)
- [x] DOM event tracking (tab switch, focus loss, copy/paste, shortcuts)
- [x] Full-screen lockdown mode
- [x] Periodic webcam snapshots (60s interval)
- [x] Event-triggered snapshots
- [x] Cheat response levels (log_only, warn, warn_escalate)
- [x] Teacher on-demand snapshot capture request
- [x] /api/student/exams/*/proctor/* routes
- [x] /api/sessions/*/proctor/* routes

## Phase 4: Deployment (Complete)
- [x] LAN mode (python run.py --lan)
- [x] Optional self-signed SSL (--ssl flag)
- [x] Gunicorn + Nginx + systemd university server setup
- [x] Multi-stage Dockerfile
- [x] docker-compose.yml
- [x] CORS hardening with origin whitelist
- [x] .env configuration with python-dotenv
- [x] .env.example with all required variables
- [x] Test suite expanded to 191 tests
- [x] All documentation updated for v1.0.0
