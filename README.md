# SmartGrader

An intelligent exam management and grading platform with computer vision OMR scanning, AI-powered short answer evaluation, online exam delivery with anti-cheat proctoring, and JWT-based authentication. Built as a Final Year Project (PFE) for an Algerian university.

## Features

### Exam Management & OMR Scanning
- **Exam Management** -- Create MCQ exams with 2-6 choices per question, configurable marks
- **Answer Sheet Generation** -- Print A4 QCM sheets with alignment markers, student ID boxes, and bubble grids
- **Optical Scanning** -- Upload scanned sheets; OpenCV detects filled bubbles and auto-grades

### AI Grading
- **AI Grading** -- Qwen2.5-VL-3B vision model reads handwritten answers and scores them
- **RAG Feedback Loop** -- Teacher corrections improve future AI evaluations

### Authentication & User Management
- **JWT Authentication** -- Secure httpOnly cookie-based auth for teachers and students
- **Role-Based Access** -- Teacher, student, and admin roles with enforced permissions
- **Student Login** -- Barcode scan login flow for fast classroom use
- **Admin Panel** -- Teacher account management; bulk student import via CSV
- **Rate Limiting** -- Flask-Limiter protects all auth endpoints

### Online Exam Engine
- **Student Groups** -- Class-based assignment of exams to groups
- **Exam Sessions** -- Scheduled time windows with start/end enforcement
- **Flexible Display** -- All-at-once or one-by-one question display modes
- **Save Modes** -- Auto-save per answer, periodic auto-save, or manual submit
- **Randomization** -- Question and choice order randomization per student
- **Result Visibility** -- Configurable: no result / score only / score + answers
- **Countdown Timer** -- Auto-submits on expiry; student sees live remaining time
- **Teacher Dashboard** -- Live monitoring of active exam sessions

### Anti-Cheat & Proctoring
- **Face Detection** -- Browser-side BlazeFace (TensorFlow.js) detects presence and multiple faces
- **Event Tracking** -- Tab switch, focus loss, copy/paste, and keyboard shortcut events logged
- **Full-Screen Lockdown** -- Optional enforced full-screen mode during exams
- **Webcam Snapshots** -- Periodic (60s) and event-triggered snapshots stored server-side
- **Cheat Response Levels** -- Configurable: log only / warn student / warn + escalate
- **Teacher Snapshot Request** -- On-demand capture from the monitoring dashboard

### General
- **Dashboard & Analytics** -- Real-time stats, bar charts, pass/fail distribution
- **Results & Export** -- View grades by exam, export to CSV, print result certificates
- **Academic Documentation** -- Full 6-chapter PFE thesis with UML diagrams and bibliography

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10, Flask 3.1, SQLAlchemy 2.0, Flask-Migrate |
| Auth | PyJWT, bcrypt, Flask-Limiter |
| Frontend | React 19, Vite, Tailwind CSS 4, shadcn/ui (base-nova), TanStack Query, Recharts |
| Proctoring | TensorFlow.js, BlazeFace model |
| Scanner | OpenCV 4.11 (contour detection, morphological operations, adaptive thresholding) |
| AI Model | Qwen2.5-VL-3B-Instruct (4-bit NF4 quantization via BitsAndBytes) |
| Database | SQLite (~15 tables, cascading foreign keys) |
| Deployment | Gunicorn, Nginx, systemd, Docker, docker-compose |
| Docs | Markdown, PlantUML, Pandoc, xhtml2pdf |

## Quick Start (5 minutes)

### 1. Install & Setup

```bash
# Clone
git clone https://github.com/your-org/SmartGrader.git
cd SmartGrader

# Backend
pip install -r requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

### 2. Create Admin Account & Seed Demo Data

```bash
# Create your first admin teacher account
python -m scripts.create_admin --email admin@school.dz --password admin12345 --name "Admin Teacher"

# Load demo data: 7 exams, 10 students, online exam sessions, results
python -m scripts.seed_data
```

### 3. Start the App

```bash
# Terminal 1: Backend (use port 5050 if 5000 is blocked on Windows)
python run.py --port 5050

# Terminal 2: Frontend
cd frontend && npm run dev
```

### 4. Open & Login

Open **http://localhost:3000** in your browser.

| Role | How to Login | Credentials |
|------|-------------|-------------|
| **Teacher (Admin)** | Email + Password | `admin@school.dz` / `admin12345` |
| **Teacher** | Email + Password | `teacher@smartgrader.dz` / `teacher123` (created by seed) |
| **Student** | Student tab → type matricule | `2026001` through `2026010` |

> **Note:** Students login by typing their matricule number (or scanning their barcode card). No password needed.

### Alternative: LAN Mode (Classroom)

One command serves everything — share the URL with students:

```bash
cd frontend && npm run build && cd ..
python run.py --lan --port 5050
# Prints: "Students can connect at http://192.168.x.x:5050"
```

### Alternative: Docker

```bash
cp .env.example .env          # edit SECRET_KEY
docker-compose up -d
# App at http://localhost:5000
```

See [INSTALL.md](INSTALL.md) for full setup including CUDA/GPU, university server deployment, and SSL configuration.

## Project Structure

```
app/
  __init__.py          # Flask app factory
  config.py            # All configuration
  models/              # SQLAlchemy ORM
    exam.py            # Exam, Question, Choice
    student.py         # Student, StudentAnswer
    result.py          # Result
    user.py            # User (teacher/student/admin accounts)
    group.py           # StudentGroup, StudentGroupMember
    session.py         # ExamSession, ExamAssignment, ExamAttempt, OnlineAnswer
    proctor.py         # ProctorEvent, ProctorSnapshot, CaptureRequest
  services/            # Business logic (exam, grading, scanner, auth, session)
  scanner/             # OpenCV pipeline (preprocess, detect, map, read)
  routes/              # Flask blueprints
    auth.py            # /api/auth/*
    admin.py           # /api/admin/*
    exams.py           # /api/exams/*
    questions.py       # /api/exams/<id>/questions
    students.py        # /api/students/*
    scanning.py        # /api/scan/upload
    grading.py         # /api/results/*
    groups.py          # /api/groups/*
    sessions.py        # /api/sessions/*
    student_exam.py    # /api/student/exams/*
  ai/                  # Vision model (loader, OCR, evaluator, RAG corrections)
frontend/
  src/pages/           # React pages (Dashboard, Exams, Scanner, Students, Results,
  |                    #   Login, ExamTaking, TeacherMonitor, AdminPanel, ...)
  src/components/      # UI components (tables, modals, charts, forms, proctor)
  src/hooks/           # TanStack Query hooks
deploy/                # Nginx config, systemd service, deploy scripts
docs/
  thesis/              # 6 chapters + appendices (Markdown)
  figures/uml/         # 7 PlantUML diagrams
legacy/                # Original PyQt5 desktop app (archived)
sgvideo/               # Remotion showcase video (1920x1080 @ 30fps)
scripts/               # seed_data, create_admin, migrate_data
```

## Documentation

| Document | Description |
|----------|-------------|
| [INSTALL.md](INSTALL.md) | Full installation and setup guide |
| [HOW_IT_WORKS.md](HOW_IT_WORKS.md) | System architecture and pipeline explanations |
| [CHANGELOG.md](CHANGELOG.md) | Version history and release notes |
| [CLAUDE.md](CLAUDE.md) | AI assistant context for Claude Code |
| [TODO.md](TODO.md) | Project roadmap and task tracking |
| [docs/thesis/](docs/thesis/) | Complete PFE thesis (6 chapters + appendices) |

## Screenshots

The application features a modern glassmorphism UI with light/dark mode:

- **Dashboard** -- Stat cards, bar charts, pass/fail distribution
- **Exams** -- Card-row list with search, pagination, print, delete
- **Scanner** -- Split layout with mode cards (MCQ / AI), step progress, upload zone
- **Results** -- Summary stats, card-row results with pass/fail badges, CSV export
- **Exam Taking** -- Student countdown timer, question navigator, auto-save
- **Teacher Monitor** -- Live session dashboard, proctor events, snapshot requests
- **Admin Panel** -- Teacher management, CSV student import
- **Academic Docs** -- Thesis chapters, UML diagrams, bibliography, build tools

## Showcase Video

A 30-second animated showcase of SmartGrader is built with [Remotion](https://www.remotion.dev/) and lives in [`sgvideo/`](sgvideo/). The video uses the same dark theme, colors, and Poppins font as the webapp -- every icon and diagram is a custom SVG component, no external assets required.

### Scenes

| # | Scene | Duration | Description |
|---|-------|----------|-------------|
| 1 | **Intro** | 4.5s | Logo entrance with glow pulse, rotating sparkles, animated gradient title |
| 2 | **Features** | 5.5s | 6 feature cards with staggered spring animation (Exam Management, OMR, AI Grading, Online Exams, Proctoring, Analytics) |
| 3 | **Stats** | 5.2s | 4 stat cards with count-up animation (191 tests, 15+ models, 40+ endpoints, 4 phases) |
| 4 | **Chart** | 5.2s | Animated bar chart showing phase completion and test count |
| 5 | **Architecture** | 5.2s | Layered system diagram: Frontend → Auth → Flask API → AI/ML → Database |
| 6 | **Outro** | 4.7s | Pulsing logo with radiating rings, "Ready for the Future of Examinations" CTA |

**Total:** 905 frames at 30fps = **~30.2 seconds** at **1920x1080**.

### Setup & Render

```bash
cd sgvideo
npm install

# Preview interactively in Remotion Studio (recommended for editing)
npm run dev
# Opens http://localhost:3000 with timeline, scrubber, and live preview

# Render the full video to MP4
npx remotion render SmartGraderShowcase out/smartgrader.mp4

# Render a single still frame (useful for thumbnails)
npx remotion still SmartGraderShowcase out/thumbnail.png --frame=60

# Render as GIF
npx remotion render SmartGraderShowcase out/smartgrader.gif --codec=gif
```

### Stack

| Layer | Technology |
|-------|-----------|
| Video framework | Remotion 4.0 |
| Styling | Tailwind CSS 4 (via `@remotion/tailwind-v4`) |
| Font | Poppins (via `@remotion/google-fonts`) |
| Animations | `useCurrentFrame()`, `spring()`, `interpolate()` |
| Scene sequencing | `<Series>` with `<Series.Sequence>` |
| Icons | Custom SVG components (no assets) |

### Project Structure

```
sgvideo/
  src/
    Root.tsx                  # Composition registration (1920x1080 @ 30fps)
    Composition.tsx           # Series of 6 scenes
    theme.ts                  # Brand colors matching webapp dark mode
    components/
      Background.tsx          # Animated gradient orbs + particles
      Icons.tsx               # 19 custom SVG icon components
    scenes/
      IntroScene.tsx          # Logo + title reveal
      FeaturesScene.tsx       # 6-card grid with spring stagger
      StatsScene.tsx          # Count-up number cards
      ChartScene.tsx          # Animated bar chart
      ArchitectureScene.tsx   # Layered system diagram
      OutroScene.tsx          # Pulsing logo + CTA
```

## API

~40 REST endpoints across 10+ groups under `/api/`:

```
POST           /api/auth/login
POST           /api/auth/student-login
POST           /api/auth/logout
GET            /api/auth/me

GET/POST/PUT   /api/admin/teachers
POST           /api/admin/students/import

GET/POST       /api/exams
GET/PUT/DELETE /api/exams/:id
GET/POST       /api/exams/:id/questions

GET/POST       /api/students
GET/PUT        /api/students/:id

POST           /api/scan/upload

GET/POST       /api/results
GET            /api/results/exam/:id

GET/POST       /api/groups
GET/PUT/DELETE /api/groups/:id
POST           /api/groups/:id/members

GET/POST       /api/sessions
GET/PUT/DELETE /api/sessions/:id
GET            /api/sessions/:id/monitor
POST           /api/sessions/:id/proctor/snapshot

GET            /api/student/exams
POST           /api/student/exams/:id/start
POST           /api/student/exams/:id/answer
POST           /api/student/exams/:id/submit
POST           /api/student/exams/:id/proctor/event
POST           /api/student/exams/:id/proctor/snapshot

GET            /api/ai/status
POST           /api/ai/ocr
POST           /api/ai/evaluate
POST           /api/ai/correct
GET            /api/ai/corrections

GET            /api/health
```

## License

PFE Academic Project -- All rights reserved. v1.0.0
