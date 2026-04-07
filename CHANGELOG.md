# Changelog

All notable changes to SmartGrader will be documented in this file.

## [0.3.0] - 2026-04-07

### Added
- **Glassmorphism UI redesign** -- Indigo/emerald palette, Poppins/Open Sans fonts, backdrop-blur cards, smooth transitions
- **6 new pages** -- Documentation (API reference), Academic Thesis, AI Configuration, Sample Data, Legacy App, Help & Guide
- **3 preview modals** -- Markdown viewer, JSON viewer with syntax highlighting, PlantUML diagram renderer (via plantuml.com)
- **Image preview modal** -- View scanned sheets and debug pipeline output in fullscreen overlay
- **Pagination** -- All tables (Exams, Students, Results) now paginated at 5 items per page
- **Student edit** -- PUT endpoint + edit form with pre-populated fields
- **Static file serving** -- `/api/files/` serves docs, old files, old sheets, debug output (with path traversal protection)
- **Print functionality** -- A4 print CSS, QCM answer sheet export (matching exact template with alignment marks, bubble circles), result certificate printing
- **Expanded seed data** -- 7 exams (59 questions), 10 students, 50+ results including English (16Q) and History (20Q)
- **Dark mode fixes** -- Sidebar 95% opacity, cards 92%, inline styles replaced with Tailwind classes
- **Scanner redesign** -- Split layout with mode cards, visual step progress, score hero cards, card-row results
- **Table redesign** -- Card-row layout with avatars, hover actions, print buttons, search, count badges
- **Grouped sidebar** -- Main / Documentation / System sections with gradient separators
- **TopBar redesign** -- Glass header with logo, search, notifications, theme toggle, user avatar
- **Welcome banner** -- Dashboard greeting with "Get Started" link
- **Academic Thesis viewer** -- Sub-project progress, chapter cards with "Read Chapter" button, UML diagram preview
- **Thesis PDF builder** -- `build_pdf.py` using xhtml2pdf (no pandoc/XeLaTeX needed)
- **Combined markdown** -- `thesis-combined.md` single-file thesis document

### Fixed
- Documentation page crash (`METHOD_STYLES` not defined)
- Dark mode inline styles on 6 pages
- UML diagram filenames in AcademicDocs (removed wrong numbered prefixes)
- Bibliography filename (`references.bib` -> `bibliography.bib`)
- Build PDF dependency text (was "pandoc", corrected to "xhtml2pdf")
- Markdown preview modal not opening (stopPropagation conflict in ChapterCard)
- Modals rendering inside `<main>` instead of using `createPortal` to body

### Changed
- Sidebar width from 64 to 72 (w-72)
- Version bumped to 0.3.0
- Page sizes: Exams 5/page, Students 5/page, Results 5/page
- Vite proxy target configurable per environment

## [0.2.0] - 2026-04-06

### Changed
- Restructured project from flat layout to layered Flask architecture
- Migrated database layer from raw sqlite3 to SQLAlchemy ORM
- Consolidated 6 scanner files into 5 focused modules
- Replaced print statements with Python logging
- Moved all hardcoded values to centralized configuration

### Added
- Flask app factory with blueprint-based routing
- React 19 frontend with TanStack Query, Recharts dashboards
- Flask-Migrate for database schema migrations
- Custom exception classes for scanner and grading errors
- AI vision model integration (Qwen2.5-VL-3B with 4-bit quantization)
- OCR pipeline for handwriting extraction
- RAG feedback loop with ai_corrections table
- pytest test suite (40+ tests across models, services, scanner, routes)
- Academic documentation (6-chapter PFE thesis, 7 UML diagrams, 18 BibTeX references)
- requirements.txt with pinned dependencies

### Archived
- Legacy PyQt5 UI code moved to `legacy/` directory

## [0.1.0] - 2026-01-01

### Added
- Initial PyQt5 desktop application
- SQLite database with exam, question, choice, student, result tables
- QCM answer sheet generation (HTML + PDF via pdfkit)
- Bubble detection and automatic MCQ grading via OpenCV
- Multiple detection algorithms (Hough, contour, template matching)
