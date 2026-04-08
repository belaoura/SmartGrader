#!/usr/bin/env python3
"""
SmartGrader Thesis PDF Builder
================================
Converts the thesis markdown files into a single PDF document.

Usage:
    python docs/thesis/build_pdf.py

Dependencies:
    pip install markdown xhtml2pdf pyyaml

The script reads all 0*.md files in the same directory as itself, combines
them with proper HTML structure, applies academic CSS styling, and outputs
thesis.pdf in the same directory.
"""

import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Dependency check — friendly error messages before any heavy imports
# ---------------------------------------------------------------------------
_missing = []
try:
    import markdown
except ImportError:
    _missing.append("markdown")

try:
    import yaml
except ImportError:
    _missing.append("pyyaml")

try:
    from xhtml2pdf import pisa
except ImportError:
    _missing.append("xhtml2pdf")

if _missing:
    print("ERROR: Missing required dependencies: " + ", ".join(_missing))
    print()
    print("Install them with:")
    print("    pip install " + " ".join(_missing))
    print()
    print("Or install all at once using the provided requirements file:")
    print("    pip install -r docs/thesis/requirements-docs.txt")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
THESIS_DIR = Path(__file__).parent.resolve()
OUTPUT_PDF = THESIS_DIR / "thesis.pdf"
METADATA_FILE = THESIS_DIR / "metadata.yaml"

# ---------------------------------------------------------------------------
# CSS — academic document styling
# ---------------------------------------------------------------------------
ACADEMIC_CSS = """
/* ── Page setup ─────────────────────────────────────────────────────────── */
@page {
    size: A4;
    margin: 2.5cm;
}

/* ── Base typography ─────────────────────────────────────────────────────── */
body {
    font-family: "Times New Roman", Times, serif;
    font-size: 12pt;
    line-height: 1.5;
    color: #000000;
    text-align: justify;
    hyphens: auto;
}

/* ── Headings ────────────────────────────────────────────────────────────── */
h1 {
    font-size: 18pt;
    font-weight: bold;
    text-align: center;
    margin-top: 0;
    margin-bottom: 24pt;
    page-break-before: always;
    border-bottom: 2px solid #000000;
    padding-bottom: 6pt;
}

/* The very first h1 (cover / TOC) should NOT force a page break */
h1.no-break {
    page-break-before: avoid;
}

h2 {
    font-size: 14pt;
    font-weight: bold;
    margin-top: 18pt;
    margin-bottom: 6pt;
}

h3 {
    font-size: 13pt;
    font-weight: bold;
    margin-top: 12pt;
    margin-bottom: 4pt;
}

h4 {
    font-size: 12pt;
    font-weight: bold;
    font-style: italic;
    margin-top: 10pt;
    margin-bottom: 4pt;
}

/* ── Paragraphs ──────────────────────────────────────────────────────────── */
p {
    margin-top: 0;
    margin-bottom: 8pt;
    text-indent: 0;
}

/* ── Ordered / unordered lists ───────────────────────────────────────────── */
ul, ol {
    margin-top: 4pt;
    margin-bottom: 8pt;
    padding-left: 20pt;
}

li {
    margin-bottom: 3pt;
}

/* ── Blockquotes (problem statement, etc.) ───────────────────────────────── */
blockquote {
    margin: 12pt 24pt;
    padding: 6pt 12pt;
    border-left: 3px solid #555555;
    font-style: italic;
    color: #333333;
}

/* ── Code blocks ─────────────────────────────────────────────────────────── */
pre {
    font-family: "Courier New", Courier, monospace;
    font-size: 9pt;
    line-height: 1.3;
    background-color: #f5f5f5;
    border: 1px solid #cccccc;
    border-left: 3px solid #666666;
    padding: 8pt 10pt;
    margin: 10pt 0;
    white-space: pre-wrap;
    word-wrap: break-word;
    page-break-inside: avoid;
}

code {
    font-family: "Courier New", Courier, monospace;
    font-size: 9.5pt;
    background-color: #f0f0f0;
    padding: 1pt 3pt;
    border-radius: 2pt;
}

pre code {
    background-color: transparent;
    padding: 0;
    font-size: 9pt;
}

/* ── Tables ──────────────────────────────────────────────────────────────── */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 10pt 0;
    font-size: 10pt;
    page-break-inside: avoid;
}

th {
    background-color: #e8e8e8;
    border: 1px solid #999999;
    padding: 5pt 8pt;
    font-weight: bold;
    text-align: left;
}

td {
    border: 1px solid #bbbbbb;
    padding: 4pt 8pt;
    vertical-align: top;
}

tr:nth-child(even) td {
    background-color: #fafafa;
}

/* ── Figure captions / italic paragraphs used as captions ───────────────── */
em {
    font-style: italic;
}

/* table captions that appear as italic paragraphs after tables */
p > em:only-child {
    display: block;
    text-align: center;
    font-size: 10pt;
    color: #444444;
    margin-top: -6pt;
    margin-bottom: 10pt;
}

/* ── Cover page elements ─────────────────────────────────────────────────── */
.cover-page {
    text-align: center;
    page-break-after: always;
}

.cover-title {
    font-size: 24pt;
    font-weight: bold;
    margin-top: 40pt;
    margin-bottom: 8pt;
}

.cover-subtitle {
    font-size: 16pt;
    margin-bottom: 30pt;
}

.cover-rule {
    border: none;
    border-top: 2px solid #000000;
    margin: 20pt 0;
}

.cover-label {
    font-size: 11pt;
    font-weight: bold;
}

.cover-value {
    font-size: 11pt;
    margin-bottom: 6pt;
}

/* ── Table of contents ───────────────────────────────────────────────────── */
.toc-container {
    page-break-after: always;
}

.toc-title {
    font-size: 18pt;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20pt;
    border-bottom: 2px solid #000000;
    padding-bottom: 6pt;
}

.toc-entry {
    font-size: 11pt;
    margin-bottom: 4pt;
}

.toc-entry.level-1 {
    font-weight: bold;
    margin-top: 8pt;
    font-size: 12pt;
}

.toc-entry.level-2 {
    padding-left: 16pt;
}

.toc-entry.level-3 {
    padding-left: 32pt;
    font-size: 10pt;
    color: #333333;
}

/* ── Abstract box ────────────────────────────────────────────────────────── */
.abstract-box {
    border: 1px solid #aaaaaa;
    padding: 14pt 16pt;
    margin: 20pt 0;
    background-color: #fafafa;
    page-break-inside: avoid;
}

.abstract-title {
    font-size: 13pt;
    font-weight: bold;
    text-align: center;
    margin-bottom: 8pt;
}

/* ── Horizontal rules ────────────────────────────────────────────────────── */
hr {
    border: none;
    border-top: 1px solid #aaaaaa;
    margin: 14pt 0;
}
"""

# ---------------------------------------------------------------------------
# Markdown extensions to use
# ---------------------------------------------------------------------------
MD_EXTENSIONS = [
    "tables",
    "fenced_code",
    "codehilite",
    "toc",
    "nl2br",
    "attr_list",
    "def_list",
    "abbr",
    "footnotes",
    "meta",
]

# Safe fallback extensions — codehilite and footnotes sometimes cause issues
MD_EXTENSIONS_FALLBACK = [
    "tables",
    "fenced_code",
    "toc",
    "nl2br",
    "attr_list",
]


def load_metadata() -> dict:
    """Parse metadata.yaml, returning a dict with at least title/author/date."""
    defaults = {
        "title": "SmartGrader",
        "subtitle": "Final Year Project (PFE) Thesis",
        "author": "Student Name",
        "date": "2026",
        "institute": "University Name",
        "abstract": "",
        "keywords": [],
    }
    if not METADATA_FILE.exists():
        print(f"  [warn] metadata.yaml not found, using defaults")
        return defaults

    with open(METADATA_FILE, "r", encoding="utf-8") as fh:
        content = fh.read()
    # Strip leading YAML front-matter delimiters if present
    content = re.sub(r"^---\s*\n", "", content)
    content = re.sub(r"\n---\s*$", "", content)

    try:
        data = yaml.safe_load(content) or {}
    except yaml.YAMLError as exc:
        print(f"  [warn] Could not parse metadata.yaml: {exc}")
        return defaults

    for key, val in defaults.items():
        data.setdefault(key, val)

    # keywords may be a list or comma-separated string
    if isinstance(data.get("keywords"), str):
        data["keywords"] = [k.strip() for k in data["keywords"].split(",")]

    return data


def collect_chapter_files() -> list:
    """Return sorted list of 0*.md files in the thesis directory."""
    files = sorted(THESIS_DIR.glob("0*.md"))
    return files


def preprocess_markdown(text: str, filename: str) -> str:
    """
    Strip LaTeX-specific constructs that xhtml2pdf cannot handle and
    normalise the markdown text for HTML conversion.
    """
    # Remove LaTeX environments: \\begin{...} ... \\end{...}
    text = re.sub(
        r"\\begin\{[^}]+\}.*?\\end\{[^}]+\}",
        "",
        text,
        flags=re.DOTALL,
    )
    # Remove individual LaTeX commands like \newpage, \vspace, \rule, etc.
    text = re.sub(r"\\[a-zA-Z]+(\{[^}]*\})*(\[[^\]]*\])*", " ", text)
    # Remove \\ line breaks used in LaTeX
    text = re.sub(r"\\\\(\[[\d.]+cm\])?", " ", text)
    # Remove HTML comments (TODO notes, figure placeholders, etc.)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    # Collapse multiple blank lines to at most two
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def md_to_html(text: str) -> str:
    """Convert markdown text to an HTML fragment."""
    md = markdown.Markdown(extensions=MD_EXTENSIONS)
    try:
        html = md.convert(text)
    except Exception:
        # Fall back to a smaller set of extensions
        md = markdown.Markdown(extensions=MD_EXTENSIONS_FALLBACK)
        html = md.convert(text)
    return html


def build_cover_html(meta: dict) -> str:
    """Generate a styled cover page from metadata."""
    keywords_str = ", ".join(meta.get("keywords", []))
    abstract_html = ""
    if meta.get("abstract"):
        abstract_text = meta["abstract"].strip()
        abstract_html = f"""
        <div class="abstract-box">
            <div class="abstract-title">Abstract</div>
            <p>{abstract_text}</p>
            <p><strong>Keywords:</strong> {keywords_str}</p>
        </div>
        """

    return f"""
    <div class="cover-page">
        <p style="font-size:13pt; font-weight:bold;">
            People's Democratic Republic of Algeria
        </p>
        <p style="font-size:11pt;">
            Ministry of Higher Education and Scientific Research
        </p>
        <p style="font-size:13pt; font-weight:bold; margin-top:12pt;">
            {meta.get('institute', 'University Name')}
        </p>
        <p style="font-size:11pt;">Faculty of Sciences and Technology</p>
        <p style="font-size:11pt; margin-bottom:20pt;">
            Department of Computer Science
        </p>

        <hr class="cover-rule" />

        <p style="font-size:15pt; font-weight:bold; margin-top:16pt;">
            End-of-Studies Project (PFE)
        </p>
        <p style="font-size:11pt;">For the degree of Master in Computer Science</p>
        <p style="font-size:11pt; margin-bottom:20pt;">Speciality: Software Engineering</p>

        <hr class="cover-rule" />

        <div class="cover-title">{meta.get('title', 'SmartGrader')}</div>
        <div class="cover-subtitle">{meta.get('subtitle', '')}</div>

        <hr class="cover-rule" />

        <table style="width:100%; margin-top:30pt; border:none;">
            <tr>
                <td style="border:none; text-align:left; vertical-align:top; width:50%;">
                    <span class="cover-label">Presented by:</span><br/>
                    <span class="cover-value">{meta.get('author', '[Student Name]')}</span>
                </td>
                <td style="border:none; text-align:right; vertical-align:top; width:50%;">
                    <span class="cover-label">Supervised by:</span><br/>
                    <span class="cover-value">[Supervisor Name]</span>
                </td>
            </tr>
        </table>

        <p style="margin-top:40pt; font-size:12pt;">
            Academic Year {meta.get('date', '2025--2026')}
        </p>
    </div>
    {abstract_html}
    """


def extract_headings(html_fragment: str) -> list:
    """
    Extract (level, text) tuples from an HTML fragment for the TOC.
    Only levels 1, 2, 3 are collected.
    """
    pattern = re.compile(
        r"<h([123])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL
    )
    headings = []
    for match in pattern.finditer(html_fragment):
        level = int(match.group(1))
        # Strip any inner HTML tags to get plain text
        raw = match.group(2)
        text = re.sub(r"<[^>]+>", "", raw).strip()
        headings.append((level, text))
    return headings


def build_toc_html(all_headings: list) -> str:
    """Generate a table-of-contents HTML block from collected headings."""
    entries = []
    for level, text in all_headings:
        cls = f"toc-entry level-{level}"
        entries.append(f'<div class="{cls}">{text}</div>')

    return f"""
    <div class="toc-container">
        <div class="toc-title">Table of Contents</div>
        {''.join(entries)}
    </div>
    """


def mark_first_h1(html: str) -> str:
    """
    The very first <h1> should not trigger a page break.
    Add class="no-break" to it.
    """
    return html.replace("<h1>", '<h1 class="no-break">', 1)


def assemble_html(cover_html: str, toc_html: str, chapters_html: list) -> str:
    """Wrap everything in a full HTML document with embedded CSS."""
    body_parts = [cover_html, toc_html] + chapters_html
    body = "\n".join(body_parts)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>SmartGrader Thesis</title>
    <style>
{ACADEMIC_CSS}
    </style>
</head>
<body>
{body}
</body>
</html>
"""


def link_callback(uri: str, rel: str) -> str:
    """
    Resolve relative image/resource URIs to absolute filesystem paths so
    xhtml2pdf can load them.  The markdown sources reference images as
    ``../figures/generated/foo.png`` which, relative to the thesis/ directory,
    points to ``docs/figures/generated/foo.png``.
    """
    # Already an absolute path or a data URI — pass through untouched
    if uri.startswith("data:") or os.path.isabs(uri):
        return uri

    # Resolve relative to the thesis directory
    candidate = (THESIS_DIR / uri).resolve()
    if candidate.exists():
        return str(candidate)

    # Fall back: try relative to the repo root
    candidate2 = (THESIS_DIR.parent.parent / uri).resolve()
    if candidate2.exists():
        return str(candidate2)

    # Return as-is and let xhtml2pdf report the error
    return uri


def convert_html_to_pdf(html_content: str, output_path: Path) -> bool:
    """Use xhtml2pdf/pisa to render HTML → PDF. Returns True on success."""
    with open(output_path, "wb") as pdf_file:
        result = pisa.CreatePDF(
            html_content.encode("utf-8"),
            dest=pdf_file,
            encoding="utf-8",
            link_callback=link_callback,
        )
    return not result.err


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  SmartGrader Thesis PDF Builder")
    print("=" * 60)
    print()

    # 1. Load metadata
    print("[1/5] Loading metadata.yaml ...")
    meta = load_metadata()
    print(f"       Title   : {meta['title']}")
    print(f"       Author  : {meta['author']}")
    print(f"       Date    : {meta['date']}")

    # 2. Collect chapter files
    print()
    print("[2/5] Collecting chapter files ...")
    chapter_files = collect_chapter_files()
    if not chapter_files:
        print("  ERROR: No chapter files (0*.md) found in", THESIS_DIR)
        sys.exit(1)
    for f in chapter_files:
        print(f"       {f.name}")

    # 3. Convert each chapter to HTML
    print()
    print("[3/5] Converting markdown to HTML ...")
    chapters_html = []
    all_headings = []

    for i, filepath in enumerate(chapter_files):
        print(f"       [{i+1}/{len(chapter_files)}] {filepath.name}")
        with open(filepath, "r", encoding="utf-8") as fh:
            raw = fh.read()

        # Skip 00-cover.md — we generate the cover from metadata instead
        if filepath.name == "00-cover.md":
            continue

        cleaned = preprocess_markdown(raw, filepath.name)
        html_fragment = md_to_html(cleaned)
        chapters_html.append(html_fragment)
        all_headings.extend(extract_headings(html_fragment))

    # 4. Build cover and TOC
    print()
    print("[4/5] Building cover page and table of contents ...")
    cover_html = build_cover_html(meta)
    toc_html = build_toc_html(all_headings)

    # 5. Assemble full document
    full_html = assemble_html(cover_html, toc_html, chapters_html)

    # Mark first h1 so it doesn't add an extra page break at the very top
    full_html = mark_first_h1(full_html)

    # Optionally save intermediate HTML for debugging
    debug_html = THESIS_DIR / "thesis_debug.html"
    with open(debug_html, "w", encoding="utf-8") as fh:
        fh.write(full_html)
    print(f"       (Debug HTML saved to {debug_html.name})")

    # 6. Render to PDF
    print()
    print("[5/5] Rendering PDF ...")
    print(f"       Output: {OUTPUT_PDF}")

    success = convert_html_to_pdf(full_html, OUTPUT_PDF)

    print()
    if success:
        size_kb = OUTPUT_PDF.stat().st_size // 1024
        print(f"  SUCCESS: thesis.pdf generated ({size_kb} KB)")
        print(f"  Location: {OUTPUT_PDF}")
    else:
        print("  ERROR: PDF generation failed.")
        print("  Tip: Check thesis_debug.html in the thesis directory for")
        print("       any HTML that may have caused xhtml2pdf to fail.")
        sys.exit(1)

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
