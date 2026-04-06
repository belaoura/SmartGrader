# SmartGrader Academic Documentation -- Design Specification

**Date:** 2026-04-06
**Status:** Approved
**Depends on:** Sub-Projects 1-3 -- all complete
**Language:** English
**Format:** Markdown source → Pandoc → PDF (LaTeX) + DOCX

---

## 1. Overview

Create a formal PFE (final-year graduation project) thesis document for SmartGrader. The thesis covers the full project: problem analysis, state of the art, system design with UML diagrams, implementation details, testing results, and future work. Written in Markdown, built to PDF and DOCX via Pandoc.

### Deliverables
- 6 thesis chapters + appendices (~45-55 pages total)
- 7 UML diagrams (PlantUML source + PNG output)
- BibTeX bibliography with academic references
- Pandoc build script producing PDF and DOCX

---

## 2. File Structure

```
docs/
├── thesis/
│   ├── metadata.yaml           # Title, author, university, date, abstract
│   ├── 00-cover.md             # Cover page
│   ├── 01-introduction.md      # Chapter 1
│   ├── 02-state-of-art.md      # Chapter 2
│   ├── 03-analysis-design.md   # Chapter 3
│   ├── 04-implementation.md    # Chapter 4
│   ├── 05-testing-results.md   # Chapter 5
│   ├── 06-conclusion.md        # Chapter 6
│   ├── 07-appendices.md        # Appendices A-D
│   ├── bibliography.bib        # BibTeX references
│   └── build.sh                # Pandoc build → PDF + DOCX
├── figures/
│   ├── uml/                    # PlantUML source (.puml)
│   │   ├── use-case.puml
│   │   ├── class-diagram.puml
│   │   ├── sequence-scan.puml
│   │   ├── sequence-ai-grade.puml
│   │   ├── er-diagram.puml
│   │   ├── deployment.puml
│   │   └── activity-scanner.puml
│   └── generated/              # PNG output
```

### Build Pipeline
1. PlantUML: `.puml` → `.png` in `figures/generated/`
2. Pandoc: all `.md` files + `metadata.yaml` + `bibliography.bib` → `thesis.pdf` (via LaTeX) + `thesis.docx`
3. `build.sh` runs both steps

Requirements: `pandoc`, `texlive-full` (or `texlive-xetex`), `plantuml` (Java-based)

---

## 3. Chapters

### Chapter 1: General Introduction (~3-4 pages)
- Context and motivation: manual grading problems (time, human error, scalability)
- Problematique: "How can we automate exam grading for both MCQ and short written answers using computer vision and AI?"
- Objectives:
  1. Restructure legacy codebase into clean layered architecture
  2. Build modern web UI replacing desktop application
  3. Integrate vision language model for handwriting OCR and AI grading
  4. Produce formal academic documentation
- Methodology: incremental migration approach
- Document organization: one paragraph per chapter

### Chapter 2: State of the Art (~8-10 pages)
- **2.1 Existing OMR Systems:** Remark Office OMR, GradeCam, ZipGrade, Moodle Quiz -- comparison table (features, pricing, limitations, open-source)
- **2.2 Computer Vision for Document Analysis:** Hough transform, contour detection, morphological operations, adaptive thresholding -- with citations
- **2.3 Vision Language Models:** LLaVA, Qwen-VL family, PaliGemma, GPT-4V -- comparison table (parameter count, multilingual support, OCR capability, VRAM requirement)
- **2.4 Handwriting Recognition:** Tesseract OCR, EasyOCR, TrOCR, VLM-based OCR -- comparison of approaches
- **2.5 RAG for LLM Improvement:** retrieval-augmented generation concept, few-shot in-context learning, prompt engineering
- **2.6 Comparative Synthesis:** table comparing all existing solutions vs SmartGrader on 8 criteria
- **2.7 Identified Gaps:** what existing solutions lack → justification for SmartGrader

### Chapter 3: Analysis & Design (~10-12 pages)
- **3.1 Functional Requirements:** use case diagram (teacher creates exam, generates sheet, scans, grades; student takes exam)
- **3.2 Non-Functional Requirements:** performance (< 5s per question grading), accuracy (> 80% OCR), hardware (6-8GB VRAM), security (input validation)
- **3.3 System Architecture:** layered architecture diagram (React frontend → Flask API → Services → Models/Scanner/AI)
- **3.4 Database Design:** ER diagram with 7 tables (exams, questions, choices, students, student_answers, results, ai_corrections)
- **3.5 API Design:** endpoint table (method, path, description, request body, response)
- **3.6 AI Pipeline Design:** two-stage diagram (OCR → Evaluate) with RAG feedback loop
- **3.7 Class Diagrams:** key module relationships
- **3.8 Sequence Diagrams:** MCQ scanning flow, AI short-answer grading flow

### Chapter 4: Implementation (~8-10 pages)
- **4.1 Development Environment:** Python 3.10, Flask 3.1, React 18, Vite, SQLAlchemy, OpenCV, Qwen2.5-VL-3B, Tailwind CSS, shadcn/ui
- **4.2 Project Structure:** folder layout with explanation of each directory
- **4.3 Backend Implementation:**
  - Flask app factory pattern
  - SQLAlchemy models with relationships
  - Service layer pattern (exam_service, grading_service, scanner_service, ai_service)
  - Scanner pipeline: preprocessing → marker detection → bubble detection → grid mapping → answer reading
- **4.4 AI Integration:**
  - Model loading with 4-bit quantization (BitsAndBytesConfig)
  - OCR prompt engineering (full-page approach)
  - Grading with model answer and keywords modes
  - RAG feedback loop: storing corrections, injecting few-shot examples
- **4.5 Frontend Implementation:**
  - React + Vite + Tailwind + shadcn/ui architecture
  - TanStack Query for server state management
  - Dark/light theme with CSS variables
  - Key pages: Dashboard, Scanner (MCQ + AI tabs)
- **4.6 Screenshots:** annotated screenshots of every UI page

### Chapter 5: Testing & Results (~6-8 pages)
- **5.1 Test Methodology:** unit tests (pytest), integration tests (Flask test client), manual testing
- **5.2 Test Coverage:** 56 automated tests -- breakdown by module (models: 10, services: 13, scanner: 11, routes: 8, AI: 16)
- **5.3 MCQ Scanning Accuracy:** precision/recall table on sample sheets, confusion matrix
- **5.4 AI Grading Evaluation:** comparison table (AI score vs teacher score), accuracy percentage, per-language breakdown
- **5.5 Performance Benchmarks:** model loading time, inference time per question, total time per exam sheet
- **5.6 RAG Improvement:** accuracy before corrections vs after N corrections chart
- **5.7 Discussion:** strengths, weaknesses, comparison to state-of-art numbers

### Chapter 6: Conclusion & Perspectives (~2-3 pages)
- Summary of achievements: 4 sub-projects, clean architecture, modern UI, AI grading with RAG
- Limitations: model size constraints (3B parameters), Arabic handwriting recognition challenges, single-GPU requirement, no essay-length support
- Future work: LoRA fine-tuning, mobile app (React Native), larger models when hardware allows, essay grading, multi-page exam support, cloud deployment

### Appendices
- **A:** Full API Reference (all 17 endpoints with examples)
- **B:** Database Schema (CREATE TABLE statements + ER diagram)
- **C:** Installation Guide (step-by-step: Python, Node.js, wkhtmltopdf, GPU setup, model download)
- **D:** User Manual (annotated screenshots of each page with step-by-step instructions)

---

## 4. UML Diagrams (PlantUML)

7 diagrams, all written as `.puml` source files:

| Diagram | File | Description |
|---------|------|-------------|
| Use Case | use-case.puml | Teacher and Student actors, 8 use cases |
| Class Diagram | class-diagram.puml | Models, services, scanner, AI modules |
| Sequence: MCQ Scan | sequence-scan.puml | Upload → detect → map → grade flow |
| Sequence: AI Grade | sequence-ai-grade.puml | Upload → OCR → review → evaluate → correct flow |
| ER Diagram | er-diagram.puml | 7 tables with relationships |
| Deployment | deployment.puml | Browser → Flask → SQLite → GPU/Model |
| Activity: Scanner | activity-scanner.puml | Preprocessing → detection → mapping → reading pipeline |

---

## 5. Bibliography

BibTeX file with ~15-20 references covering:
- OMR systems (Remark, GradeCam papers/docs)
- Hough transform (original Hough 1962, Ballard 1981)
- OpenCV documentation
- Qwen2-VL paper (Wang et al. 2024)
- LLaVA paper (Liu et al. 2023)
- PaliGemma paper (Beyer et al. 2024)
- RAG paper (Lewis et al. 2020)
- Flask documentation
- React documentation
- SQLAlchemy documentation
- Tesseract OCR paper
- BitsAndBytes quantization paper (Dettmers et al. 2022)
- WCAG accessibility guidelines

---

## 6. Build Script

`build.sh`:
```bash
#!/bin/bash
# Generate UML PNGs
plantuml -tpng docs/figures/uml/*.puml -o ../generated/

# Build PDF (via LaTeX)
pandoc docs/thesis/metadata.yaml \
  docs/thesis/0*.md \
  --from markdown \
  --to pdf \
  --pdf-engine=xelatex \
  --bibliography=docs/thesis/bibliography.bib \
  --citeproc \
  --number-sections \
  --toc \
  -o docs/thesis/thesis.pdf

# Build DOCX
pandoc docs/thesis/metadata.yaml \
  docs/thesis/0*.md \
  --from markdown \
  --to docx \
  --bibliography=docs/thesis/bibliography.bib \
  --citeproc \
  --number-sections \
  --toc \
  -o docs/thesis/thesis.docx
```
