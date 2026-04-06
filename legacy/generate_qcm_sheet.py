#!/usr/bin/env python3
"""
QCM Exam Sheet Generator with Smart Grading Features
FIXED VERSION - Correct column filling (left full → right full → next page)
               and no question overflow past page borders.
               NOW WITH PDF EXPORT!
"""

import sqlite3
import os
import sys
import math
import json
from datetime import datetime

try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except ImportError:
    PDFKIT_AVAILABLE = False
    print("⚠️  pdfkit not installed. PDF export disabled.")
    print("   Install with: pip install pdfkit")
    print("   Also install wkhtmltopdf from: https://wkhtmltopdf.org/downloads.html")

# =========================
# CONFIGURATION
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "smart_grader.db")
TEMPLATE_PATH = os.path.join(BASE_DIR, "qcm_template.html")

# A4 page dimensions in mm
PAGE_HEIGHT_MM = 297
PAGE_WIDTH_MM = 210

# Margins
TOP_MARGIN_MM = 8
BOTTOM_MARGIN_MM = 8
LEFT_MARGIN_MM = 12
RIGHT_MARGIN_MM = 12

# Fixed element heights (must match CSS exactly)
HEADER_HEIGHT_MM = 28        # 5 rows × 4.5mm + border + padding
MINIMAL_HEADER_HEIGHT_MM = 10
STUDENT_SECTION_HEIGHT_MM = 36
INSTRUCTION_HEIGHT_MM = 8    # instruction bar + margin
PAGE_NUMBER_HEIGHT_MM = 6    # page-number bar + margin-top
GRID_GAP_MM = 2              # gap between student section and grid

# Typography — 9pt × line-height 1.3
LINE_HEIGHT_MM = 4.3          # slightly conservative to avoid overflow
OPTION_SPACING_MM = 1.2       # gap between options (matches CSS gap: 1mm + safety)
QUESTION_BOTTOM_MM = 3.5      # margin-bottom + padding-bottom + dotted border
MIN_QUESTION_HEIGHT_MM = 10

# Estimate chars that fit in one column (~85 mm content width at 9pt ≈ 2.1 chars/mm)
CHARS_PER_LINE = 62           # conservative — prevents underestimating wrapping

# Safety buffer subtracted from available height to prevent any overflow
HEIGHT_SAFETY_BUFFER_MM = 4

# Smart grading flags
SMART_GRADING_ENABLED = True
GENERATE_ANSWER_KEY = True
INCLUDE_OMR_MARKERS = True


# ─────────────────────────────────────────────
# AVAILABLE HEIGHT CALCULATION
# ─────────────────────────────────────────────

def calculate_available_height(is_first_page: bool) -> float:
    """
    Return the usable height (per column) for questions on a given page.
    All fixed elements are subtracted PLUS a safety buffer.
    """
    fixed = TOP_MARGIN_MM + BOTTOM_MARGIN_MM + STUDENT_SECTION_HEIGHT_MM + PAGE_NUMBER_HEIGHT_MM + GRID_GAP_MM

    if is_first_page:
        fixed += HEADER_HEIGHT_MM + INSTRUCTION_HEIGHT_MM
    else:
        fixed += MINIMAL_HEADER_HEIGHT_MM

    available = PAGE_HEIGHT_MM - fixed - HEIGHT_SAFETY_BUFFER_MM
    return max(available, 30)   # never return a nonsensical value


CONTENT_HEIGHT_FIRST_PAGE  = calculate_available_height(True)
CONTENT_HEIGHT_OTHER_PAGES = calculate_available_height(False)


# ─────────────────────────────────────────────
# DATABASE HELPERS
# ─────────────────────────────────────────────

def get_connection():
    return sqlite3.connect(DB_PATH)


def get_exam_info(exam_id):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT id, title, subject, date, total_marks
        FROM exams WHERE id = ?
    """, (exam_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'title': row[1], 'subject': row[2],
                'date': row[3] or "", 'total_marks': row[4] or ""}
    return None


def fetch_questions_with_answers(exam_id):
    """Fetch questions and compute a conservative height for each."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT id, question_text FROM questions
        WHERE exam_id = ? ORDER BY id
    """, (exam_id,))
    questions = cur.fetchall()

    data = []
    print(f"\n📊 Processing {len(questions)} questions:")

    for idx, (q_id, q_text) in enumerate(questions):
        cur.execute("""
            SELECT choice_label, choice_text, is_correct
            FROM choices WHERE question_id = ? ORDER BY choice_label
        """, (q_id,))
        choices = cur.fetchall()

        if not choices:
            choices = [('A','Option A',1),('B','Option B',0),
                       ('C','Option C',0),('D','Option D',0)]

        # Correct answer
        correct_answer = next((lbl for lbl,_,ok in choices if ok), choices[0][0])

        # ── Height calculation ──────────────────────────────────────────
        # Question text lines  (add 1 extra line for safety on long texts)
        q_chars  = len(q_text) + 8   # +8 for the "N." prefix
        q_lines  = max(1, math.ceil(q_chars / CHARS_PER_LINE))

        # Options
        option_line_counts = []
        for _, ct, _ in choices:
            # +4 chars for "○ X " prefix
            lines = max(1, math.ceil((len(ct) + 4) / CHARS_PER_LINE))
            option_line_counts.append(lines)

        total_option_lines = sum(option_line_counts)

        height = (
            q_lines * LINE_HEIGHT_MM
            + total_option_lines * LINE_HEIGHT_MM
            + len(choices) * OPTION_SPACING_MM
            + QUESTION_BOTTOM_MM
        )
        height = max(height, MIN_QUESTION_HEIGHT_MM)

        data.append({
            'id': q_id, 'text': q_text, 'choices': choices,
            'correct_answer': correct_answer,
            'q_lines': q_lines,
            'option_lines': total_option_lines,
            'option_line_counts': option_line_counts,
            'height': height,
            'index': idx, 'number': idx + 1
        })
        print(f"   Q{idx+1}: {height:.1f}mm  ({q_lines}q + {total_option_lines}opt lines)")

    conn.close()
    return data


# ─────────────────────────────────────────────
# ANSWER KEY
# ─────────────────────────────────────────────

def generate_answer_key(questions, exam_info):
    key = {
        'exam_id': exam_info['id'], 'exam_title': exam_info['title'],
        'subject': exam_info['subject'], 'date': exam_info['date'],
        'total_questions': len(questions), 'total_marks': exam_info['total_marks'],
        'answers': {},
        'metadata': {'generated': datetime.now().isoformat(), 'version': '1.0', 'format': 'smart_grader_v1'}
    }
    for q in questions:
        correct = next((lbl for lbl,_,ok in q['choices'] if ok), q['choices'][0][0])
        key['answers'][str(q['id'])] = {
            'question_number': q['index'] + 1,
            'correct_answer': correct,
            'question_text': q['text'][:100] + ('...' if len(q['text']) > 100 else '')
        }
    path = os.path.join(BASE_DIR, f"answer_key_exam_{exam_info['id']}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(key, f, indent=2, ensure_ascii=False)
    print(f"   ✅ Answer key saved: {path}")
    return path


# ─────────────────────────────────────────────
# QUESTION DISTRIBUTION  ← FIXED LOGIC
# ─────────────────────────────────────────────

def _balance_columns(pool, cap):
    """
    Given a flat list of questions that are known to fit in two columns of
    height `cap`, find the split index that makes the two column heights as
    equal as possible while respecting the reading order (left top→bottom,
    right top→bottom).

    Strategy: try every possible split point i (1 … len-1) and pick the one
    that minimises |height(left) - height(right)|, as long as BOTH sides stay
    within `cap`.  Fall back to the simple midpoint split if nothing better
    is found.
    """
    n = len(pool)
    if n <= 1:
        return pool, []

    cumulative = []
    running = 0.0
    for q in pool:
        running += q['height']
        cumulative.append(running)
    total_h = cumulative[-1]

    best_split = n // 2          # default: half by count
    best_diff  = float('inf')

    for i in range(1, n):
        lh = cumulative[i - 1]
        rh = total_h - lh
        # Both columns must fit within cap
        if lh <= cap and rh <= cap:
            diff = abs(lh - rh)
            if diff < best_diff:
                best_diff  = diff
                best_split = i

    return pool[:best_split], pool[best_split:]


def distribute_questions_to_pages(questions):
    """
    Filling rules
    ─────────────
    • Normal pages: fill LEFT column completely first, then RIGHT column,
      then move to the next page.  No blank space is left in a column unless
      there are genuinely no more questions.

    • Last page (no more questions remain after placing on this page):
      if the questions placed here fit inside TWO columns with room to spare
      (i.e. total height ≤ 2 × cap), redistribute them so that the left and
      right column heights are as equal as possible.  This avoids a dense
      left column sitting next to a near-empty right column.

    Returns: list of pages, each page = {'left': [...], 'right': [...]}
    """
    if not questions:
        return []

    pages     = []
    remaining = list(questions)
    page_num  = 1

    print(f"\n📄 DISTRIBUTING {len(questions)} QUESTIONS:")
    print(f"   Page 1  capacity: {CONTENT_HEIGHT_FIRST_PAGE:.1f}mm/column")
    print(f"   Page 2+ capacity: {CONTENT_HEIGHT_OTHER_PAGES:.1f}mm/column")

    while remaining:
        cap = CONTENT_HEIGHT_FIRST_PAGE if page_num == 1 else CONTENT_HEIGHT_OTHER_PAGES

        # ── Step 1: collect every question that fits on this page ──────
        #   (left column first, then right column)
        left_col,  left_h  = [], 0.0
        for q in remaining:
            if left_h + q['height'] <= cap:
                left_col.append(q)
                left_h += q['height']
            else:
                break

        after_left = remaining[len(left_col):]
        right_col, right_h = [], 0.0
        for q in after_left:
            if right_h + q['height'] <= cap:
                right_col.append(q)
                right_h += q['height']
            else:
                break

        # ── Edge case: nothing fits → force the next question ──────────
        if not left_col and not right_col:
            print(f"   ⚠️  Page {page_num}: question too tall, forcing placement")
            pages.append({'left': [remaining[0]], 'right': []})
            remaining = remaining[1:]
            page_num += 1
            continue

        placed    = left_col + right_col
        remaining = remaining[len(placed):]

        # ── Step 2: if this is the LAST page, balance the columns ──────
        #
        #   Condition: no questions left AND the placed questions fit in
        #   two columns (total height ≤ 2 × cap, which is always true here
        #   because we just filled them that way).  We balance whenever the
        #   right column exists (i.e. there are at least 2 questions).
        #
        if not remaining and right_col:
            left_col, right_col = _balance_columns(placed, cap)
            left_h  = sum(q['height'] for q in left_col)
            right_h = sum(q['height'] for q in right_col)
            print(f"   ↳ last-page balance applied")

        pages.append({'left': left_col, 'right': right_col})

        fill_l = (left_h  / cap) * 100
        fill_r = (right_h / cap) * 100 if right_col else 0
        print(f"   Page {page_num}: L={len(left_col)}q ({fill_l:.0f}%) "
              f"R={len(right_col)}q ({fill_r:.0f}%)  remaining={len(remaining)}")
        page_num += 1

    placed_total = sum(len(p['left']) + len(p['right']) for p in pages)
    print(f"   TOTAL: {len(pages)} page(s) | {placed_total} questions placed")
    return pages


# ─────────────────────────────────────────────
# HTML BUILDERS
# ─────────────────────────────────────────────

def _esc(text):
    return text.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')


def build_question_html(question_data, question_number):
    q_text  = question_data['text']
    choices = question_data['choices']
    olc     = question_data['option_line_counts']

    opts_html = ""
    for i, (label, text, is_correct) in enumerate(choices):
        ml = " multi-line" if olc[i] > 1 else ""
        ga = ""
        if SMART_GRADING_ENABLED:
            ga = (f' data-qid="{question_data["id"]}" data-opt="{label}"'
                  f' data-correct="{str(bool(is_correct)).lower()}"')
            if GENERATE_ANSWER_KEY and is_correct:
                ga += ' data-correct-answer="true"'
        opts_html += f"""
        <div class="option{ml}"{ga}>
            <div class="circle"></div>
            <div class="option-text">{_esc(text)}</div>
        </div>"""

    ml_q = " multi-line" if question_data['q_lines'] > 1 else ""
    qa   = ""
    if SMART_GRADING_ENABLED:
        qa = (f' data-qid="{question_data["id"]}" data-qnum="{question_number}"'
              f' data-correct-answer="{question_data["correct_answer"]}"')

    return f"""
    <div class="question" data-question-id="{question_data['id']}" data-question-number="{question_number}"{qa}>
        <div class="q-text{ml_q}">
            <span class="q-number">{question_number}.</span>
            <span class="q-text-content">{_esc(q_text)}</span>
        </div>
        <div class="options">{opts_html}
        </div>
    </div>"""


def build_omr_markers():
    if not INCLUDE_OMR_MARKERS:
        return ""
    return """
    <div class="omr-marker top-left"></div>
    <div class="omr-marker top-right"></div>
    <div class="omr-marker bottom-left"></div>
    <div class="omr-marker bottom-right"></div>"""


def build_page_html(page_data, page_num, total_pages, is_first_page, start_number, exam_info=None):
    """Build one A4 page from {'left': [...], 'right': [...]}."""
    left_col  = page_data['left']
    right_col = page_data['right']

    if not left_col and not right_col:
        return ""

    # Build column HTML
    left_html, right_html = "", ""
    for i, q in enumerate(left_col):
        left_html += build_question_html(q, start_number + i)
    for i, q in enumerate(right_col):
        right_html += build_question_html(q, start_number + len(left_col) + i)

    # Header
    if is_first_page:
        header_html = f"""
        <div class="header">
            <div class="header-row"><div class="header-label">INSTITUTION:</div><div class="underline">___________________________</div></div>
            <div class="header-row"><div class="header-label">DEPARTMENT:</div><div class="underline">___________________________</div></div>
            <div class="header-row"><div class="header-label">EXAM:</div><div class="underline">{_esc(exam_info.get('title','') if exam_info else '')}</div></div>
            <div class="header-row"><div class="header-label">SUBJECT:</div><div class="underline">{_esc(exam_info.get('subject','') if exam_info else '')}</div></div>
            <div class="header-row"><div class="header-label">DATE:</div><div class="underline">{_esc(exam_info.get('date','') if exam_info else '')}</div></div>
        </div>"""
        instruction_html = """
        <div class="instruction-text">✦ CHOOSE THE CORRECT ANSWER FOR EACH QUESTION ✦</div>"""
    else:
        header_html = f"""
        <div class="header minimal">
            <div class="header-row"><div class="header-label">EXAM CONTINUED — PAGE {page_num}</div></div>
        </div>"""
        instruction_html = ""

    # Student section
    name_boxes = ''.join(['<span class="name-box"></span>' for _ in range(20)])
    fname_boxes= ''.join(['<span class="name-box"></span>' for _ in range(18)])
    id_boxes   = ''.join(['<span class="id-box"></span>'   for _ in range(14)])
    student_html = f"""
    <div class="student-section">
        <div class="qr-area">
            <div class="qr-placeholder">
                <div class="qr-corner"></div><div class="qr-corner"></div>
                <div class="qr-corner"></div><div class="qr-corner"></div>
                <div class="qr-label">ID</div>
            </div>
        </div>
        <div class="info-row">
            <div class="info-label">LAST NAME:</div>
            <div class="box-row">{name_boxes}</div>
        </div>
        <div class="info-row">
            <div class="info-label">FIRST NAME:</div>
            <div class="box-row">{fname_boxes}</div>
        </div>
        <div class="info-row">
            <div class="info-label">STUDENT ID:</div>
            <div class="box-row">{id_boxes}</div>
        </div>
    </div>"""

    return f"""
    <div class="page">
        <div class="align top-left"></div>
        <div class="align top-right"></div>
        <div class="align bottom-left"></div>
        <div class="align bottom-right"></div>
        {build_omr_markers()}
        <div class="page-content">
            {header_html}
            {student_html}
            {instruction_html}
            <div class="questions-markers-top">
                <div class="section-marker"></div>
                <div class="section-marker"></div>
            </div>
            <div class="questions-grid">
                <div class="vertical-divider"></div>
                <div class="column">{left_html}</div>
                <div class="column">{right_html}</div>
            </div>
            <div class="questions-markers-bottom">
                <div class="section-marker"></div>
                <div class="section-marker"></div>
            </div>
            <div class="page-number">Page {page_num} of {total_pages}</div>
        </div>
    </div>"""


# ─────────────────────────────────────────────
# TEMPLATE
# ─────────────────────────────────────────────

def create_updated_template():
    """Write the CSS template (line-height aligned with Python constants)."""
    tmpl = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>QCM Answer Sheet</title>
<style>
@page { size: A4; margin: 0; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: "Times New Roman", serif;
    background: white;
    width: 210mm;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}

/* ── PAGE ─────────────────────────────────────── */
.page {
    width: 210mm;
    height: 297mm;
    position: relative;
    background: white;
    page-break-after: always;
    break-after: page;
    margin: 0 auto;
    /* Padding must match TOP/BOTTOM/LEFT/RIGHT_MARGIN_MM in Python */
    padding: 8mm 12mm 8mm 12mm;
    overflow: hidden;          /* ← prevents any content from overflowing */
}

.page-content {
    width: 100%;
    height: 100%;              /* fills the padded area exactly */
    display: flex;
    flex-direction: column;
    overflow: hidden;          /* belt-and-suspenders */
}

/* ── HEADER ───────────────────────────────────── */
.header {
    border: 1pt solid black;
    padding: 2mm 3mm;
    margin-bottom: 2mm;
    background: white;
    flex-shrink: 0;
}
.header.minimal {
    border: 1pt dashed black;
    padding: 1.5mm 2mm;
    text-align: center;
}
.header-row {
    display: flex;
    align-items: flex-end;
    margin-bottom: 1.5mm;
    height: 4.5mm;
}
.header-label {
    font-weight: bold;
    min-width: 25mm;
    margin-right: 2mm;
    font-size: 9pt;
}
.underline {
    flex: 1;
    border-bottom: 0.5pt solid black;
    height: 3.5mm;
    margin-bottom: 0.5mm;
    font-size: 9pt;
    padding-left: 2mm;
}

/* ── STUDENT SECTION ──────────────────────────── */
.student-section {
    border: 1pt solid black;
    padding: 2.5mm 3mm;
    margin-bottom: 2mm;
    position: relative;
    min-height: 36mm;
    background: white;
    flex-shrink: 0;
}
.qr-area {
    position: absolute;
    top: 2.5mm; right: 3mm;
    width: 17mm; height: 17mm;
    border: 0.5pt solid black;
    display: flex;
    justify-content: center;
    align-items: center;
    background: white;
}
.qr-placeholder { width: 100%; height: 100%; position: relative; }
.qr-corner {
    position: absolute;
    width: 2.5mm; height: 2.5mm;
    border: 0.3mm solid #666;
}
.qr-corner:nth-child(1){top:1.5mm;left:1.5mm;border-right:none;border-bottom:none;}
.qr-corner:nth-child(2){top:1.5mm;right:1.5mm;border-left:none;border-bottom:none;}
.qr-corner:nth-child(3){bottom:1.5mm;left:1.5mm;border-right:none;border-top:none;}
.qr-corner:nth-child(4){bottom:1.5mm;right:1.5mm;border-left:none;border-top:none;}
.qr-label {
    position: absolute; top:50%; left:50%;
    transform:translate(-50%,-50%);
    font-size:10pt; font-weight:bold; color:#666;
}
.info-row { margin-bottom: 2mm; width: calc(100% - 21mm); max-width: 140mm; }
.info-row:last-child { margin-bottom: 0; }
.info-label { font-weight:bold; margin-bottom:0.3mm; font-size:8.5pt; text-transform:uppercase; }
.box-row { display:flex; gap:0.5mm; flex-wrap:wrap; }
.name-box { width:3.8mm; height:3.8mm; border:0.5pt solid black; display:inline-block; }
.id-box   { width:4.3mm; height:4.3mm; border:0.5pt solid black; display:inline-block; }

/* ── INSTRUCTION ──────────────────────────────── */
.instruction-text {
    text-align: center;
    font-size: 9pt;
    font-weight: bold;
    font-style: italic;
    margin-bottom: 2mm;
    padding: 1mm;
    background-color: #f9f9f9;
    border-left: 2pt solid #333;
    border-right: 2pt solid #333;
    color: #333;
    letter-spacing: 0.3px;
    text-transform: uppercase;
    flex-shrink: 0;
}

/* ── QUESTIONS GRID ───────────────────────────── */
.questions-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 5mm;
    position: relative;
    flex: 1 1 0;      /* takes remaining height */
    min-height: 0;
    overflow: hidden; /* clips anything that exceeds the allocated space */
}
.vertical-divider {
    position: absolute;
    top: 0; bottom: 0;
    left: calc(50% - 2.5mm);  /* sits in the column-gap */
    width: 0.5pt;
    background: black;
    pointer-events: none;
}
.column {
    display: flex;
    flex-direction: column;
    overflow: hidden;   /* ← key: column itself does NOT scroll/overflow */
    min-width: 0;
}

/* ── INDIVIDUAL QUESTION ──────────────────────── */
.question {
    margin-bottom: 2.5mm;
    padding-bottom: 0.5mm;
    border-bottom: 1pt solid #000;
    break-inside: avoid;
    page-break-inside: avoid;
    flex-shrink: 0;   /* questions never squish themselves */
}
.question:last-child { border-bottom: none; margin-bottom: 0; }

.q-text {
    font-weight: bold;
    margin-bottom: 1mm;
    line-height: 4.3mm;   /* must match LINE_HEIGHT_MM in Python */
    font-size: 9pt;
    display: flex;
    gap: 1.5mm;
    align-items: flex-start;
    word-wrap: break-word;
    overflow-wrap: break-word;
    hyphens: auto;
}
.q-number {
    font-weight: bold;
    min-width: 6.5mm;
    flex-shrink: 0;
    font-size: 9pt;
    white-space: nowrap;
}
.q-text-content {
    flex: 1;
    word-wrap: break-word;
    overflow-wrap: break-word;
    hyphens: auto;
}

.options {
    display: flex;
    flex-direction: column;
    gap: 1mm;
    margin-left: 8mm;
    width: calc(100% - 8mm);
}
.option {
    display: flex;
    align-items: flex-start;
    gap: 1.2mm;
    font-size: 9pt;
    word-wrap: break-word;
    overflow-wrap: break-word;
}
.circle {
    min-width: 2.8mm; width: 2.8mm; height: 2.8mm;
    border: 0.5pt solid black;
    border-radius: 50%;
    display: flex;
    align-items: center; justify-content: center;
    font-size: 6pt; font-weight: bold;
    flex-shrink: 0;
    background: white;
    margin-top: 0.5mm;
}
.option-text {
    flex: 1;
    min-width: 0;
    line-height: 4.3mm;   /* must match LINE_HEIGHT_MM */
    font-size: 9pt;
    word-wrap: break-word;
    overflow-wrap: break-word;
    hyphens: auto;
}

/* ── ALIGNMENT MARKS ──────────────────────────── */
.align { position:absolute; width:3mm; height:3mm; background:black; z-index:10; }
.align.top-left    { top:2mm;    left:2mm;  }
.align.top-right   { top:2mm;    right:2mm; }
.align.bottom-left { bottom:2mm; left:2mm;  }
.align.bottom-right{ bottom:2mm; right:2mm; }

/* ── SECTION MARKERS ─────────────────────────── */
/* Small black TRIANGLES at left and right edges of question section */
.questions-markers-top,
.questions-markers-bottom {
    display: flex;
    justify-content: space-between;
    padding: 0 2mm;
    flex-shrink: 0;
}
.section-marker {
    width: 0;
    height: 0;
}
.questions-markers-top .section-marker {
    border-left: 4mm solid transparent;
    border-right: 4mm solid transparent;
    border-top: 6mm solid black;
}
.questions-markers-bottom .section-marker {
    border-left: 4mm solid transparent;
    border-right: 4mm solid transparent;
    border-bottom: 6mm solid black;
}

.omr-marker {
    position:absolute; width:2mm; height:2mm;
    background:transparent; border:0.2mm solid #00f;
    opacity:0.3; z-index:5; pointer-events:none;
}
.omr-marker.top-left    { top:5mm;    left:5mm;  }
.omr-marker.top-right   { top:5mm;    right:5mm; }
.omr-marker.bottom-left { bottom:5mm; left:5mm;  }
.omr-marker.bottom-right{ bottom:5mm; right:5mm; }

/* ── PAGE NUMBER ──────────────────────────────── */
.page-number {
    text-align:center;
    font-size:7pt;
    margin-top:2mm;
    color:#333;
    font-family:Arial,sans-serif;
    border-top:0.2pt dotted #999;
    padding-top:1mm;
    flex-shrink:0;
}

/* ── PRINT ────────────────────────────────────── */
@media print {
    @page { size: A4; margin: 0; }
    body { width: 210mm; }
    .page {
        width:210mm; height:297mm;
        padding:8mm 12mm 8mm 12mm;
        page-break-after:always;
        break-after:page;
        overflow:hidden;
    }
    .header,.student-section,.qr-area,.name-box,.id-box,.circle {
        border:0.5pt solid black !important;
        background:white !important;
        -webkit-print-color-adjust:exact;
        print-color-adjust:exact;
    }
    .instruction-text {
        border-left:2pt solid black !important;
        border-right:2pt solid black !important;
        background-color:#f9f9f9 !important;
        -webkit-print-color-adjust:exact;
        print-color-adjust:exact;
    }
    .vertical-divider,.align { background:black !important; border-color:black !important; print-color-adjust:exact; }
    .underline { border-bottom:0.5pt solid black !important; }
}

/* ── SCREEN PREVIEW ───────────────────────────── */
@media screen {
    body { background:#e0e0e0; display:flex; flex-direction:column; align-items:center; padding:20px 0; }
    .page { box-shadow:0 0 15px rgba(0,0,0,0.3); margin-bottom:25px; border:1px solid #ccc; }
}

/* Clearfix */
.student-section::after { content:""; display:table; clear:both; }
</style>
</head>
<body>
    {{PAGES_HTML}}
</body>
</html>"""
    with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
        f.write(tmpl)
    print(f"✅ Template written (line-height = {LINE_HEIGHT_MM}mm, buffer = {HEIGHT_SAFETY_BUFFER_MM}mm)")


# ─────────────────────────────────────────────
# MAIN GENERATOR
# ─────────────────────────────────────────────

def generate_exam_sheet(exam_id):
    print("=" * 70)
    print("📝 QCM EXAM SHEET GENERATOR — FIXED DISTRIBUTION")
    print("=" * 70)

    create_updated_template()

    exam_info = get_exam_info(exam_id)
    if not exam_info:
        print(f"❌ Exam ID {exam_id} not found"); return None

    print(f"\n📋 {exam_info['title']} | {exam_info['subject']} | {exam_info['date']}")

    questions = fetch_questions_with_answers(exam_id)
    if not questions:
        print("❌ No questions found"); return None

    print(f"\n📏 Heights — P1: {CONTENT_HEIGHT_FIRST_PAGE:.1f}mm/col  "
          f"P2+: {CONTENT_HEIGHT_OTHER_PAGES:.1f}mm/col  "
          f"buffer: {HEIGHT_SAFETY_BUFFER_MM}mm")

    pages = distribute_questions_to_pages(questions)

    if GENERATE_ANSWER_KEY:
        print("\n🔑 Generating answer key...")
        generate_answer_key(questions, exam_info)

    print(f"\n📄 Building {len(pages)} page(s)...")
    pages_html     = ""
    q_counter      = 1

    for i, page_data in enumerate(pages):
        pages_html += build_page_html(
            page_data,
            page_num     = i + 1,
            total_pages  = len(pages),
            is_first_page= (i == 0),
            start_number = q_counter,
            exam_info    = exam_info if i == 0 else None
        )
        placed = len(page_data['left']) + len(page_data['right'])
        print(f"   Page {i+1}: {placed} questions  "
              f"(L={len(page_data['left'])} R={len(page_data['right'])})")
        q_counter += placed

    total_placed = q_counter - 1
    if total_placed == len(questions):
        print(f"\n✅ All {len(questions)} questions placed correctly.")
    else:
        print(f"\n⚠️  {total_placed}/{len(questions)} questions placed.")

    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()
    final_html = template.replace("{{PAGES_HTML}}", pages_html)

    html_out = os.path.join(BASE_DIR, f"qcm_exam_{exam_id}_final.html")
    with open(html_out, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f"\n📄 HTML Output: {html_out}  ({os.path.getsize(html_out):,} bytes)")

    pdf_out = None
    if PDFKIT_AVAILABLE:
        print("\n📑 Converting to PDF...")
        try:
            pdf_out = os.path.join(BASE_DIR, f"qcm_exam_{exam_id}_final.pdf")
            pdfkit.from_string(final_html, pdf_out)
            print(f"✅ PDF Output: {pdf_out}  ({os.path.getsize(pdf_out):,} bytes)")
        except Exception as e:
            print(f"⚠️  PDF generation failed: {e}")
            pdf_out = None
    else:
        print("\n⚠️  Skipping PDF (pdfkit not installed)")
        print("   Install: pip install pdfkit")
        print("   And download wkhtmltopdf from: https://wkhtmltopdf.org/downloads.html")

    return html_out, pdf_out


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def list_available_exams():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT e.id, e.title, e.subject, COUNT(q.id)
        FROM exams e LEFT JOIN questions q ON e.id = q.exam_id
        GROUP BY e.id ORDER BY e.id
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}"); return 1

    exams = list_available_exams()
    if not exams:
        print("❌ No exams found."); return 1

    print("\n📋 Available Exams:")
    for e in exams:
        print(f"   ID {e[0]}: {e[1]} ({e[2]}) — {e[3]} questions")

    exam_id = None
    if len(sys.argv) > 1:
        try: exam_id = int(sys.argv[1])
        except ValueError: pass

    if not exam_id:
        try: exam_id = int(input("\n🔢 Enter Exam ID: "))
        except (ValueError, KeyboardInterrupt):
            print("❌ Cancelled."); return 1

    if not get_exam_info(exam_id):
        print(f"❌ Exam {exam_id} not found."); return 1

    try:
        result = generate_exam_sheet(exam_id)
        if result:
            html_path, pdf_path = result
            print("\n" + "="*50)
            print("🎉 GENERATION COMPLETE!")
            print("="*50)
            if html_path:
                print(f"📄 HTML: {html_path}")
            if pdf_path:
                print(f"📑 PDF:  {pdf_path}")
            return 0
        return 1
    except Exception as e:
        import traceback
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())