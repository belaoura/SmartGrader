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
