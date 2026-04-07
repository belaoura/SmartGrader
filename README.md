# SmartGrader

An intelligent exam management and grading system with computer vision scanning and AI-powered short answer evaluation. Built as a Final Year Project (PFE) for an Algerian university.

## Features

- **Exam Management** -- Create MCQ exams with 2-6 choices per question, configurable marks
- **Answer Sheet Generation** -- Print A4 QCM sheets with alignment markers, student ID boxes, and bubble grids
- **Optical Scanning** -- Upload scanned sheets; OpenCV detects filled bubbles and auto-grades
- **AI Grading** -- Qwen2.5-VL-3B vision model reads handwritten answers and scores them
- **RAG Feedback Loop** -- Teacher corrections improve future AI evaluations
- **Dashboard & Analytics** -- Real-time stats, bar charts, pass/fail distribution
- **Results & Export** -- View grades by exam, export to CSV, print result certificates
- **Academic Documentation** -- Full 6-chapter PFE thesis with UML diagrams and bibliography

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10, Flask 3.1, SQLAlchemy 2.0, Flask-Migrate |
| Frontend | React 19, Vite, Tailwind CSS 4, shadcn/ui (base-nova), TanStack Query, Recharts |
| Scanner | OpenCV 4.11 (contour detection, morphological operations, adaptive thresholding) |
| AI Model | Qwen2.5-VL-3B-Instruct (4-bit NF4 quantization via BitsAndBytes) |
| Database | SQLite (7 tables, cascading foreign keys) |
| Docs | Markdown, PlantUML, Pandoc, xhtml2pdf |

## Quick Start

```bash
# Clone
git clone https://github.com/your-org/SmartGrader.git
cd SmartGrader

# Backend
pip install -r requirements.txt
python -m scripts.seed_data   # seed 7 exams, 10 students, 50+ results
python run.py                 # Flask API at http://localhost:5000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev                   # React app at http://localhost:3000
```

See [INSTALL.md](INSTALL.md) for detailed setup including CUDA/GPU configuration.

## Project Structure

```
app/
  __init__.py          # Flask app factory
  config.py            # All configuration
  models/              # SQLAlchemy ORM (Exam, Question, Choice, Student, Result)
  services/            # Business logic (exam, grading, scanner)
  scanner/             # OpenCV pipeline (preprocess, detect, map, read)
  routes/              # Flask blueprints (exams, questions, students, scanning, grading, ai)
  ai/                  # Vision model (loader, OCR, evaluator, RAG corrections)
frontend/
  src/pages/           # React pages (Dashboard, Exams, Scanner, Students, Results, ...)
  src/components/      # UI components (tables, modals, charts, forms)
  src/hooks/           # TanStack Query hooks
docs/
  thesis/              # 6 chapters + appendices (Markdown)
  figures/uml/         # 7 PlantUML diagrams
legacy/                # Original PyQt5 desktop app (archived)
scripts/               # Seed data, migration tools
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
- **Academic Docs** -- Thesis chapters, UML diagrams, bibliography, build tools

## API

18 REST endpoints under `/api/`:

```
GET/POST       /api/exams
GET/PUT/DELETE /api/exams/:id
GET/POST       /api/exams/:id/questions
GET/POST       /api/students
GET/PUT        /api/students/:id
POST           /api/scan/upload
GET/POST       /api/results
GET            /api/ai/status
POST           /api/ai/ocr | /api/ai/evaluate | /api/ai/correct
GET            /api/health
```

## License

PFE Academic Project -- All rights reserved.
