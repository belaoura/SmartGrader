# SmartGrader UI Fixes & Enhancements — Design Spec

**Date:** 2026-04-07
**Scope:** 9 fixes across dark mode, printing, static file serving, modals, seed data, and broken links

---

## 1. Dark Mode Fix

### CSS (`frontend/src/index.css`)

- `--color-sidebar` dark: `rgba(15,23,42,0.60)` → `rgba(15,23,42,0.95)`
- `--color-card` dark: `rgba(15,23,42,0.80)` → `rgba(15,23,42,0.92)`
- `body::before` dark gradients: reduce indigo to 3%, emerald to 2%

### JSX Inline Styles

Audit and fix all 6 new pages (`Documentation.jsx`, `AcademicDocs.jsx`, `AIConfig.jsx`, `SampleData.jsx`, `LegacyCode.jsx`, `Help.jsx`):
- Replace every `style={{ color: "#hex" }}` and `style={{ background: "#hex" }}` with Tailwind classes that respond to the dark variant
- Use `text-foreground`, `text-muted-foreground`, `bg-card`, `bg-muted`, `bg-primary/10`, `border-border` etc.
- Hardcoded light-only colors (white backgrounds, dark text) must use CSS variables or Tailwind dark-aware classes

**Verification:** Toggle dark mode on every page and confirm no light-colored text on light backgrounds or vice versa.

---

## 2. Static File Serving (Backend)

### New file: `app/routes/static_files.py`

```python
# Blueprint: static_files_bp, url_prefix="/api/files"
# Route: GET /<path:filepath>
# Whitelisted directories: "old files", "old sheets", "docs", "debug_output"
# Validates the first path segment is in whitelist
# Uses flask.send_from_directory with project BASE_DIR
# Sets appropriate MIME types
# Rejects path traversal (no ".." segments)
```

### Register in `app/routes/__init__.py`

Add `from .static_files import static_files_bp` and register it in `register_routes()`.

---

## 3. Seed Data

### Expand `scripts/seed_data.py`

**Exams** (5 total):
1. Mathematics - Algebra (existing, 4 questions)
2. Biology - Cell Biology (from answer_key_exam_2.json)
3. Physics - Mechanics (from answer_key_exam_3.json)
4. Chemistry - Organic (from answer_key_exam_4.json)
5. Computer Science - Algorithms (from answer_key_exam_5.json)

Each new exam: parse the corresponding JSON answer key to get question count and create matching Question + Choice records.

**Students** (10 total): Keep existing 3, add 7 more with realistic Algerian names.

**Results**: For each exam, seed 5-8 results with randomized scores (60-100% range) to populate dashboard charts and results page.

**Idempotent**: Check if data exists before inserting (query by title/name).

---

## 4. Print Functionality

### Print CSS in `index.css`

```css
@media print {
  header, aside, .no-print { display: none !important; }
  main { padding: 0 !important; margin: 0 !important; }
  body, body::before { background: white !important; }
  body::before { display: none !important; }
  .glass {
    background: white !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: none !important;
  }
  @page { size: A4; margin: 2cm; }
  body { font-size: 12pt; line-height: 1.5; color: black !important; }
}
```

### ExamDetail.jsx — Enhanced Print

The existing `window.print()` button now works correctly with the print CSS above (sidebar/topbar hidden, A4 page).

Add an "Export PDF" button that:
1. Opens a new browser window
2. Writes a clean HTML document with exam title, questions, choices, answer key
3. Styled for A4 (21cm x 29.7cm, 2cm margins, 12pt serif font)
4. Auto-calls `window.print()` in the new window
5. User saves as PDF via browser print dialog

---

## 5. Quick Links (Documentation.jsx)

Replace all 4 `alert()` placeholders:

| Link | Action |
|------|--------|
| Thesis PDF | `window.open("/api/files/docs/thesis/thesis.pdf", "_blank")` |
| GitHub Repository | `window.open("https://github.com/", "_blank")` with note "Update URL in source" — or show the git remote if configured |
| Installation Guide | Open MarkdownPreviewModal with `docs/thesis/07-appendices.md` (scrolled to Appendix C) |
| User Manual | Open MarkdownPreviewModal with `docs/thesis/07-appendices.md` (scrolled to Appendix D) |

---

## 6. AcademicDocs.jsx Fixes

### Text corrections
- Build PDF dependency: "Python 3.10+, pandoc, xelatex" → "Python 3.10+, markdown, xhtml2pdf, pyyaml"
- Bibliography filename: `references.bib` → `bibliography.bib`

### UML diagram filename fixes
| Current (wrong) | Correct |
|-----------------|---------|
| `01-use-case.puml` | `use-case.puml` |
| `02-class-diagram.puml` | `class-diagram.puml` |
| `03-sequence-create.puml` | `sequence-scan.puml` |
| `04-sequence-scan.puml` | `sequence-ai-grade.puml` |
| `05-sequence-ai.puml` | `activity-scanner.puml` |
| `06-er-diagram.puml` | `er-diagram.puml` |
| `07-deployment.puml` | `deployment.puml` |

### Button fixes
- "Download Thesis PDF" → `window.open("/api/files/docs/thesis/thesis.pdf", "_blank")`
- "Browse docs/ Folder" → `navigate("/documentation")`
- Each chapter card: click opens MarkdownPreviewModal for that chapter's `.md` file
- Each UML card: click opens PumlPreviewModal for that diagram

---

## 7. UML Diagram Preview Modal

### New component: `frontend/src/components/ui/puml-preview-modal.jsx`

```
Props: { open, onClose, filename, title }
```

**Behavior:**
1. When `open` becomes true, fetch `/api/files/docs/figures/uml/<filename>`
2. Encode the PlantUML source using the PlantUML text encoding algorithm:
   - Deflate the UTF-8 text
   - Encode with PlantUML's custom base64 variant (0-9, A-Z, a-z, -, _)
3. Set `<img src="https://www.plantuml.com/plantuml/svg/<encoded>" />`
4. Show in a large modal (max-w-4xl, max-h-[80vh] with overflow scroll)
5. Modal has: title, close button (X), the rendered SVG image
6. Loading state: skeleton while image loads
7. Error fallback: if image fails to load, show raw `.puml` source in a `<pre>` code block

**PlantUML encoding:** Implement the standard algorithm (deflate + custom base64). This is a well-documented ~30 line function. Use the browser's `CompressionStream` API for deflate, or bundle a tiny pako-based deflate.

Actually, simpler approach: use the PlantUML server's plain-text endpoint which accepts the source directly via URL encoding. The server supports `https://www.plantuml.com/plantuml/svg/~h<hex-encoded-text>` format. We'll use the standard deflate encoding for compactness.

---

## 8. Markdown Preview Modal

### New component: `frontend/src/components/ui/markdown-preview-modal.jsx`

```
Props: { open, onClose, filePath, title }
```

**Behavior:**
1. When `open` becomes true, fetch `/api/files/<filePath>` as text
2. Convert markdown to HTML:
   - Use a simple client-side converter (no new dependencies)
   - Handle: headings (#-######), bold/italic, code blocks, tables, lists, links, blockquotes
   - A basic regex-based converter is sufficient for thesis markdown
3. Render in a scrollable modal (max-w-4xl, max-h-[80vh])
4. Apply typography CSS: serif font for body, proper heading sizes, table borders, code block styling
5. Modal has: title, close button, print button (prints just the modal content), the rendered HTML

**Print from modal:** The print button creates a new window with the rendered HTML + A4 print styles, then calls `window.print()`.

---

## 9. JSON Preview Modal

### New component: `frontend/src/components/ui/json-preview-modal.jsx`

```
Props: { open, onClose, filename, title }
```

**Behavior:**
1. When `open` becomes true, fetch `/api/files/old files/<filename>` as JSON
2. Pretty-print with `JSON.stringify(data, null, 2)`
3. Apply simple syntax highlighting via CSS classes:
   - Strings: green
   - Numbers: blue
   - Keys: indigo (primary color)
   - Booleans/null: amber
4. Render in a scrollable `<pre>` block inside a modal (max-w-3xl, max-h-[80vh])
5. Modal has: title, close button, copy button (copies JSON to clipboard)

### SampleData.jsx fixes
- Update the inline preview template to match the real JSON structure
- Wire "View Full JSON" buttons to open JsonPreviewModal with the correct filename
- Wire "Open" buttons on exam sheets to `window.open("/api/files/old files/<name>", "_blank")`
- Wire "Print" buttons to open file in new tab then print

---

## File Map

### New files
```
app/routes/static_files.py          — Flask static file serving route
frontend/src/components/ui/puml-preview-modal.jsx   — PlantUML diagram modal
frontend/src/components/ui/markdown-preview-modal.jsx — Markdown viewer modal
frontend/src/components/ui/json-preview-modal.jsx    — JSON viewer modal
```

### Modified files
```
frontend/src/index.css               — Dark mode fixes + print CSS
frontend/src/pages/Documentation.jsx — Quick links fixes
frontend/src/pages/AcademicDocs.jsx  — Filename fixes, button fixes, modal integration
frontend/src/pages/SampleData.jsx    — JSON modal, file links, preview fixes
frontend/src/pages/ExamDetail.jsx    — Export PDF button
frontend/src/pages/LegacyCode.jsx    — Dark mode inline style fixes
frontend/src/pages/AIConfig.jsx      — Dark mode inline style fixes
frontend/src/pages/Help.jsx          — Dark mode inline style fixes
app/routes/__init__.py               — Register static files blueprint
scripts/seed_data.py                 — Expanded seed data
```

---

## Dependencies

- **No new npm packages** — markdown rendering via simple regex converter, PlantUML via external server, JSON highlighting via CSS
- **No new pip packages** — Flask's `send_from_directory` handles file serving
- **External service**: `plantuml.com` for UML rendering (internet required for diagram preview only)

---

## Testing Checklist

- [ ] Dark mode: all 13 pages render correctly with no contrast issues
- [ ] Print: ExamDetail prints A4 without sidebar/topbar
- [ ] Export PDF: clean exam sheet opens in new window, printable
- [ ] Static files: `/api/files/docs/thesis/thesis.pdf` serves the PDF
- [ ] Static files: `/api/files/old files/answer_key_exam_1.json` serves JSON
- [ ] Static files: path traversal rejected (e.g. `../../../etc/passwd`)
- [ ] Seed data: `python -m scripts.seed_data` creates 5 exams, 10 students, results
- [ ] Dashboard charts populated with seed data
- [ ] UML modal: clicking a diagram card shows rendered SVG from PlantUML server
- [ ] Markdown modal: clicking a thesis chapter shows rendered content
- [ ] JSON modal: "View Full JSON" shows prettified, highlighted JSON
- [ ] Quick Links: Thesis PDF opens in new tab, Install/User Manual open modals
- [ ] AcademicDocs: correct filenames, correct dependency text, download button works
