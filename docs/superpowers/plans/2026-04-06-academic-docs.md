# SmartGrader Academic Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the complete PFE thesis document with 6 chapters, 7 UML diagrams, bibliography, appendices, and a Pandoc build script producing PDF + DOCX.

**Architecture:** Markdown source files in `docs/thesis/`, PlantUML diagrams in `docs/figures/uml/`, built via Pandoc to PDF (XeLaTeX) and DOCX. All content version-controlled.

**Tech Stack:** Markdown, PlantUML, Pandoc, XeLaTeX, BibTeX

---

## File Map

```
docs/
├── thesis/
│   ├── metadata.yaml
│   ├── 00-cover.md
│   ├── 01-introduction.md
│   ├── 02-state-of-art.md
│   ├── 03-analysis-design.md
│   ├── 04-implementation.md
│   ├── 05-testing-results.md
│   ├── 06-conclusion.md
│   ├── 07-appendices.md
│   ├── bibliography.bib
│   └── build.sh
├── figures/
│   └── uml/
│       ├── use-case.puml
│       ├── class-diagram.puml
│       ├── sequence-scan.puml
│       ├── sequence-ai-grade.puml
│       ├── er-diagram.puml
│       ├── deployment.puml
│       └── activity-scanner.puml
```

---

## Task 1: Scaffold + Metadata + Build Script

**Files:**
- Create: `docs/thesis/metadata.yaml`, `docs/thesis/build.sh`, `docs/figures/uml/.gitkeep`

- [ ] **Step 1: Create directories**

```bash
mkdir -p docs/thesis docs/figures/uml docs/figures/generated
```

- [ ] **Step 2: Create metadata.yaml**

Write `docs/thesis/metadata.yaml` with full thesis metadata for Pandoc.

- [ ] **Step 3: Create build.sh**

Write `docs/thesis/build.sh` with PlantUML + Pandoc commands.

- [ ] **Step 4: Create bibliography.bib**

Write `docs/thesis/bibliography.bib` with ~18 academic references.

- [ ] **Step 5: Commit**

```bash
git add docs/thesis/metadata.yaml docs/thesis/build.sh docs/thesis/bibliography.bib docs/figures/
git commit -m "docs: add thesis scaffold, metadata, bibliography, and build script"
```

---

## Task 2: UML Diagrams (7 PlantUML files)

**Files:**
- Create: all 7 `.puml` files in `docs/figures/uml/`

- [ ] **Step 1: Create use-case.puml**
- [ ] **Step 2: Create class-diagram.puml**
- [ ] **Step 3: Create sequence-scan.puml**
- [ ] **Step 4: Create sequence-ai-grade.puml**
- [ ] **Step 5: Create er-diagram.puml**
- [ ] **Step 6: Create deployment.puml**
- [ ] **Step 7: Create activity-scanner.puml**
- [ ] **Step 8: Commit**

```bash
git add docs/figures/uml/
git commit -m "docs: add 7 PlantUML UML diagrams"
```

---

## Task 3: Chapter 1 -- General Introduction

**Files:**
- Create: `docs/thesis/00-cover.md`, `docs/thesis/01-introduction.md`

- [ ] **Step 1: Write cover page**
- [ ] **Step 2: Write Chapter 1 (~3-4 pages): context, problematique, objectives, methodology, document organization**
- [ ] **Step 3: Commit**

```bash
git add docs/thesis/00-cover.md docs/thesis/01-introduction.md
git commit -m "docs: add cover page and Chapter 1 - General Introduction"
```

---

## Task 4: Chapter 2 -- State of the Art

**Files:**
- Create: `docs/thesis/02-state-of-art.md`

- [ ] **Step 1: Write Chapter 2 (~8-10 pages): OMR systems, computer vision, VLMs, handwriting recognition, RAG, comparative synthesis, identified gaps**
- [ ] **Step 2: Commit**

```bash
git add docs/thesis/02-state-of-art.md
git commit -m "docs: add Chapter 2 - State of the Art"
```

---

## Task 5: Chapter 3 -- Analysis & Design

**Files:**
- Create: `docs/thesis/03-analysis-design.md`

- [ ] **Step 1: Write Chapter 3 (~10-12 pages): functional/non-functional requirements, architecture, DB design, API design, AI pipeline, class diagrams, sequence diagrams. Reference all 7 UML diagrams.**
- [ ] **Step 2: Commit**

```bash
git add docs/thesis/03-analysis-design.md
git commit -m "docs: add Chapter 3 - Analysis and Design"
```

---

## Task 6: Chapter 4 -- Implementation

**Files:**
- Create: `docs/thesis/04-implementation.md`

- [ ] **Step 1: Write Chapter 4 (~8-10 pages): dev environment, project structure, backend implementation, AI integration, frontend implementation. Include code snippets.**
- [ ] **Step 2: Commit**

```bash
git add docs/thesis/04-implementation.md
git commit -m "docs: add Chapter 4 - Implementation"
```

---

## Task 7: Chapter 5 -- Testing & Results

**Files:**
- Create: `docs/thesis/05-testing-results.md`

- [ ] **Step 1: Write Chapter 5 (~6-8 pages): test methodology, coverage, MCQ accuracy, AI grading evaluation, performance benchmarks, RAG improvement, discussion.**
- [ ] **Step 2: Commit**

```bash
git add docs/thesis/05-testing-results.md
git commit -m "docs: add Chapter 5 - Testing and Results"
```

---

## Task 8: Chapter 6 + Appendices

**Files:**
- Create: `docs/thesis/06-conclusion.md`, `docs/thesis/07-appendices.md`

- [ ] **Step 1: Write Chapter 6 (~2-3 pages): summary, limitations, future work**
- [ ] **Step 2: Write Appendices: API reference, DB schema, installation guide, user manual**
- [ ] **Step 3: Commit**

```bash
git add docs/thesis/06-conclusion.md docs/thesis/07-appendices.md
git commit -m "docs: add Chapter 6 - Conclusion and Appendices"
```

---

## Task 9: Final Assembly + TODO Update

- [ ] **Step 1: Verify all thesis files exist and are consistent**
- [ ] **Step 2: Update TODO.md to mark Sub-Project 4 complete**
- [ ] **Step 3: Commit**

```bash
git add TODO.md
git commit -m "docs: complete Sub-Project 4 -- Academic Documentation"
```

---

## Summary

| Task | Content | Est. Pages |
|------|---------|-----------|
| 1 | Scaffold, metadata, bibliography, build script | -- |
| 2 | 7 UML diagrams (PlantUML) | -- |
| 3 | Cover + Chapter 1: Introduction | 3-4 |
| 4 | Chapter 2: State of the Art | 8-10 |
| 5 | Chapter 3: Analysis & Design | 10-12 |
| 6 | Chapter 4: Implementation | 8-10 |
| 7 | Chapter 5: Testing & Results | 6-8 |
| 8 | Chapter 6: Conclusion + Appendices | 5-7 |
| 9 | Final assembly + TODO | -- |

**Total: 9 tasks, ~40-50 pages of thesis content**
