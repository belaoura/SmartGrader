#!/usr/bin/env python3
"""
SmartGrader UML Diagram Generator
===================================
Generates PNG diagrams for the thesis using Pillow (PIL).
No PlantUML or external tools required.

Usage:
    python scripts/generate_diagrams.py

Output:
    docs/figures/generated/*.png
"""

import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent.resolve()
OUT_DIR = ROOT / "docs" / "figures" / "generated"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
WHITE       = (255, 255, 255)
BLACK       = (0, 0, 0)
DARK_GREY   = (60, 60, 60)
MED_GREY    = (130, 130, 130)
LIGHT_GREY  = (220, 220, 220)
BG          = (248, 248, 248)

BLUE        = (30, 90, 180)
LIGHT_BLUE  = (210, 225, 250)
ACTOR_BLUE  = (50, 110, 200)
ACTOR_FILL  = (200, 220, 255)

GREEN       = (30, 130, 60)
LIGHT_GREEN = (195, 235, 205)
SERVICE_GREEN = (40, 140, 70)
SERVICE_FILL  = (200, 235, 210)

ORANGE      = (200, 110, 20)
LIGHT_ORANGE = (255, 225, 185)

PURPLE      = (110, 50, 160)
LIGHT_PURPLE = (225, 205, 250)

RED         = (180, 40, 40)
LIGHT_RED   = (250, 200, 200)

TEAL        = (20, 140, 140)
LIGHT_TEAL  = (195, 235, 235)

YELLOW      = (200, 170, 0)
LIGHT_YELLOW = (255, 245, 180)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def new_image(w, h, bg=WHITE):
    img = Image.new("RGB", (w, h), bg)
    return img, ImageDraw.Draw(img)


def try_font(size):
    """Return a truetype or default bitmap font at approximately `size`."""
    font_candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/Arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in font_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def try_font_bold(size):
    bold_candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/tahomabd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for path in bold_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return try_font(size)


def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def centered_text(draw, cx, cy, text, font, color=BLACK):
    w, h = text_size(draw, text, font)
    draw.text((cx - w // 2, cy - h // 2), text, font=font, fill=color)


def wrapped_text(draw, cx, cy, text, font, color=BLACK, max_width=180, line_gap=4):
    """Draw text centered at (cx, cy), wrapping at max_width pixels."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        w, _ = text_size(draw, test, font)
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    _, lh = text_size(draw, "Ag", font)
    total_h = len(lines) * (lh + line_gap)
    y = cy - total_h // 2
    for line in lines:
        lw, _ = text_size(draw, line, font)
        draw.text((cx - lw // 2, y), line, font=font, fill=color)
        y += lh + line_gap


def rounded_rect(draw, x0, y0, x1, y1, fill, outline, radius=8, width=2):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)


def arrow(draw, x1, y1, x2, y2, color=DARK_GREY, width=2, head=8):
    """Draw an arrow from (x1,y1) to (x2,y2)."""
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    # Arrowhead
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    a1x = x2 - head * math.cos(angle - math.pi / 6)
    a1y = y2 - head * math.sin(angle - math.pi / 6)
    a2x = x2 - head * math.cos(angle + math.pi / 6)
    a2y = y2 - head * math.sin(angle + math.pi / 6)
    draw.polygon([(x2, y2), (int(a1x), int(a1y)), (int(a2x), int(a2y))], fill=color)


def dashed_line(draw, x1, y1, x2, y2, color=MED_GREY, width=1, dash=8):
    """Draw a dashed line."""
    import math
    length = math.hypot(x2 - x1, y2 - y1)
    if length == 0:
        return
    dx = (x2 - x1) / length
    dy = (y2 - y1) / length
    pos = 0
    drawing = True
    while pos < length:
        end_pos = min(pos + dash, length)
        if drawing:
            draw.line([
                (int(x1 + dx * pos), int(y1 + dy * pos)),
                (int(x1 + dx * end_pos), int(y1 + dy * end_pos)),
            ], fill=color, width=width)
        pos += dash
        drawing = not drawing


def title_bar(draw, img_w, title, font_bold, font_sm):
    """Draw a professional title bar at the top of a diagram."""
    draw.rectangle([0, 0, img_w, 50], fill=BLUE)
    centered_text(draw, img_w // 2, 25, title, font_bold, WHITE)


def save(img, name):
    path = OUT_DIR / name
    img.save(path, "PNG", dpi=(150, 150))
    size_kb = path.stat().st_size // 1024
    print(f"  Saved: {name}  ({size_kb} KB)")


# ---------------------------------------------------------------------------
# 1. Use-Case Diagram
# ---------------------------------------------------------------------------
def generate_use_case():
    W, H = 1200, 780
    img, draw = new_image(W, H, BG)
    fb = try_font_bold(16)
    fn = try_font(13)
    fsm = try_font(11)
    title_bar(draw, W, "SmartGrader — Use Case Diagram", fb, fn)

    # System boundary
    draw.rectangle([200, 80, 1000, 720], fill=WHITE, outline=DARK_GREY, width=2)
    w, _ = text_size(draw, "SmartGrader System", fb)
    draw.text((600 - w // 2, 85), "SmartGrader System", font=fb, fill=DARK_GREY)

    # Actor helper
    def actor(x, y, label, color=ACTOR_BLUE):
        # Head
        draw.ellipse([x - 18, y - 18, x + 18, y + 18], fill=ACTOR_FILL, outline=color, width=2)
        centered_text(draw, x, y, label[0], fn, color)
        # Body
        draw.line([(x, y + 18), (x, y + 55)], fill=color, width=3)
        draw.line([(x - 22, y + 30), (x + 22, y + 30)], fill=color, width=3)
        draw.line([(x, y + 55), (x - 18, y + 85)], fill=color, width=3)
        draw.line([(x, y + 55), (x + 18, y + 85)], fill=color, width=3)
        centered_text(draw, x, y + 103, label, fsm, color)

    # Use-case ellipse helper
    def usecase(cx, cy, text, fill=LIGHT_BLUE, outline=BLUE):
        draw.ellipse([cx - 95, cy - 30, cx + 95, cy + 30], fill=fill, outline=outline, width=2)
        wrapped_text(draw, cx, cy, text, fsm, DARK_GREY, max_width=175)

    # Actors
    actor(55, 180, "Teacher", ACTOR_BLUE)
    actor(55, 490, "Admin", BLUE)
    actor(1145, 330, "Student", GREEN)

    # Use cases — teacher side
    uc_data_teacher = [
        (420, 130, "Manage Exams"),
        (420, 210, "Generate Answer Sheets"),
        (420, 290, "Scan MCQ Sheet"),
        (420, 370, "AI Grade Short Answers"),
        (420, 450, "Review & Correct AI Grades"),
        (420, 530, "View Results"),
        (420, 610, "Manage Students"),
    ]
    for cx, cy, label in uc_data_teacher:
        usecase(cx, cy, label)

    # Use cases — student side
    uc_data_student = [
        (750, 250, "Take Online Exam"),
        (750, 370, "Monitor Proctoring"),
        (750, 490, "Authenticate (Barcode)"),
    ]
    for cx, cy, label in uc_data_student:
        usecase(cx, cy, label, LIGHT_GREEN, GREEN)

    # Admin use cases
    uc_data_admin = [
        (420, 690, "Create Groups & Sessions"),
    ]
    for cx, cy, label in uc_data_admin:
        usecase(cx, cy, label, LIGHT_ORANGE, ORANGE)

    # Connections — Teacher
    for cx, cy, _ in uc_data_teacher:
        draw.line([(105, 215), (cx - 95, cy)], fill=ACTOR_BLUE, width=1)
    # Connections — Admin
    draw.line([(105, 525), (325, 690)], fill=BLUE, width=1)
    # Connections — Student
    for cx, cy, _ in uc_data_student:
        draw.line([(1095, 365), (cx + 95, cy)], fill=GREEN, width=1)

    # Include / extend annotations
    dashed_line(draw, 420, 160, 420, 180, MED_GREY, 1)  # visual separation
    draw.text((510, 305), "<<include>>", font=fsm, fill=MED_GREY)
    arrow(draw, 420, 290, 420, 240, MED_GREY, 1)

    draw.text((510, 415), "<<extend>>", font=fsm, fill=MED_GREY)
    dashed_line(draw, 420, 450, 420, 390, MED_GREY, 1)

    save(img, "use-case.png")


# ---------------------------------------------------------------------------
# 2. ER Diagram
# ---------------------------------------------------------------------------
def generate_er_diagram():
    W, H = 1200, 820
    img, draw = new_image(W, H, BG)
    fb = try_font_bold(15)
    fn = try_font(12)
    fsm = try_font(10)
    title_bar(draw, W, "SmartGrader — Entity-Relationship Diagram", fb, fn)

    def entity(x, y, name, attrs, fill=LIGHT_BLUE, outline=BLUE, w=210, row_h=22):
        header_h = 30
        total_h = header_h + len(attrs) * row_h + 8
        # Header
        draw.rectangle([x, y, x + w, y + header_h], fill=outline, outline=outline)
        centered_text(draw, x + w // 2, y + header_h // 2, name, fb, WHITE)
        # Body
        draw.rectangle([x, y + header_h, x + w, y + total_h], fill=fill, outline=outline, width=1)
        for i, attr in enumerate(attrs):
            yt = y + header_h + 6 + i * row_h
            is_pk = attr.startswith("PK ")
            is_fk = attr.startswith("FK ")
            color = RED if is_pk else ORANGE if is_fk else DARK_GREY
            prefix = ""
            if is_pk:
                prefix = "PK "
                attr = attr[3:]
            elif is_fk:
                prefix = "FK "
                attr = attr[3:]
            draw.text((x + 8, yt), prefix + attr, font=fsm if is_fk else fn, fill=color)
        return x + w // 2, y + total_h // 2, y + total_h  # cx, cy, bottom

    # Entities layout
    entities = {}

    # Row 1
    entities["Exam"] = entity(50, 70, "Exam", [
        "PK id", "title", "subject", "date", "total_marks"
    ])
    entities["Question"] = entity(330, 70, "Question", [
        "PK id", "FK exam_id", "question_text", "choices_number", "marks"
    ])
    entities["Choice"] = entity(620, 70, "Choice", [
        "PK id", "FK question_id", "choice_label", "choice_text", "is_correct"
    ])
    entities["AICorrection"] = entity(900, 70, "AICorrection", [
        "PK id", "FK question_id", "student_text", "ai_score",
        "ai_feedback", "teacher_score", "teacher_feedback"
    ])

    # Row 2
    entities["Student"] = entity(50, 390, "Student", [
        "PK id", "name", "matricule", "email"
    ])
    entities["StudentAnswer"] = entity(330, 390, "StudentAnswer", [
        "PK id", "FK student_id", "FK question_id", "FK selected_choice_id"
    ])
    entities["Result"] = entity(620, 390, "Result", [
        "PK id", "FK student_id", "FK exam_id",
        "score", "percentage", "graded_at"
    ])
    entities["ExamSession"] = entity(900, 390, "ExamSession", [
        "PK id", "FK exam_id", "scheduled_at", "duration_min", "status"
    ])

    # Row 3
    entities["StudentGroup"] = entity(50, 620, "StudentGroup", [
        "PK id", "name", "year_level"
    ])
    entities["ExamAttempt"] = entity(330, 620, "ExamAttempt", [
        "PK id", "FK session_id", "FK student_id",
        "started_at", "submitted_at", "score"
    ])
    entities["OnlineAnswer"] = entity(620, 620, "OnlineAnswer", [
        "PK id", "FK attempt_id", "FK question_id",
        "FK selected_choice_id", "answered_at"
    ])
    entities["ProctorEvent"] = entity(900, 620, "ProctorEvent", [
        "PK id", "FK attempt_id", "event_type",
        "severity", "timestamp", "frame_path"
    ])

    def rel(e1, cx1, cy1, e2, cx2, cy2, label=""):
        arrow(draw, cx1, cy1, cx2, cy2, MED_GREY, 1, 7)
        if label:
            mx = (cx1 + cx2) // 2
            my = (cy1 + cy2) // 2
            draw.text((mx + 3, my - 14), label, font=fsm, fill=MED_GREY)

    # Relationships using midpoints
    # Exam -> Question
    rel("", 155, 145, "", 330, 145, "1→N")
    # Question -> Choice
    rel("", 540, 145, "", 620, 145, "1→N")
    # Question -> AICorrection
    rel("", 830, 145, "", 900, 145, "1→N")
    # Student -> StudentAnswer
    rel("", 155, 450, "", 330, 450, "1→N")
    # Question -> StudentAnswer (vertical)
    arrow(draw, 435, 210, 435, 390, MED_GREY, 1, 7)
    draw.text((440, 295), "1→N", font=fsm, fill=MED_GREY)
    # Choice -> StudentAnswer
    arrow(draw, 725, 210, 540, 390, MED_GREY, 1, 7)
    # Student -> Result
    arrow(draw, 155, 520, 620, 450, MED_GREY, 1, 7)
    # Exam -> Result
    arrow(draw, 155, 170, 725, 390, MED_GREY, 1, 7)
    # Exam -> ExamSession
    arrow(draw, 155, 160, 1005, 390, MED_GREY, 1, 7)
    # ExamSession -> ExamAttempt
    arrow(draw, 1005, 500, 435, 620, MED_GREY, 1, 7)
    draw.text((700, 550), "1→N", font=fsm, fill=MED_GREY)
    # ExamAttempt -> OnlineAnswer
    rel("", 540, 680, "", 620, 680, "1→N")
    # ExamAttempt -> ProctorEvent
    rel("", 750, 680, "", 900, 680, "1→N")
    # Student -> StudentGroup (via group_members)
    arrow(draw, 155, 580, 155, 620, MED_GREY, 1, 7)

    # Legend
    draw.rectangle([50, 760, 600, 790], fill=WHITE, outline=LIGHT_GREY)
    draw.text((60, 765), "PK = Primary Key     FK = Foreign Key     →  = relationship direction", font=fsm, fill=DARK_GREY)

    save(img, "er-diagram.png")


# ---------------------------------------------------------------------------
# 3. Class Diagram
# ---------------------------------------------------------------------------
def generate_class_diagram():
    W, H = 1200, 820
    img, draw = new_image(W, H, BG)
    fb = try_font_bold(14)
    fn = try_font(11)
    fsm = try_font(10)
    title_bar(draw, W, "SmartGrader — Class Diagram", fb, fn)

    def draw_class(x, y, name, attrs, methods, fill, outline, w=175):
        attr_h = max(len(attrs), 1) * 18 + 8
        meth_h = max(len(methods), 1) * 18 + 8
        total_h = 30 + attr_h + meth_h
        # Header
        rounded_rect(draw, x, y, x + w, y + 30, fill=outline, outline=outline, radius=4)
        centered_text(draw, x + w // 2, y + 15, name, fb, WHITE)
        # Attributes section
        draw.rectangle([x, y + 30, x + w, y + 30 + attr_h], fill=fill, outline=outline, width=1)
        for i, attr in enumerate(attrs):
            draw.text((x + 7, y + 38 + i * 18), attr, font=fsm, fill=DARK_GREY)
        # Methods section
        draw.rectangle([x, y + 30 + attr_h, x + w, y + total_h], fill=(245, 245, 255) if fill == LIGHT_BLUE else fill, outline=outline, width=1)
        for i, m in enumerate(methods):
            draw.text((x + 7, y + 38 + attr_h + i * 18), m, font=fsm, fill=DARK_GREY)
        cx = x + w // 2
        cy = y + total_h // 2
        return cx, y, y + total_h  # cx, top, bottom

    # Models package
    draw.rectangle([30, 58, 600, 480], fill=(250, 250, 255), outline=BLUE, width=2)
    draw.text((35, 62), "«Models»", font=fb, fill=BLUE)

    mx = {}
    mx["Exam"] = draw_class(45, 85, "Exam",
        ["+id: Integer", "+title: String", "+subject: String", "+total_marks: Float"],
        ["+to_dict()", "+get_statistics()"],
        LIGHT_BLUE, BLUE)
    mx["Question"] = draw_class(240, 85, "Question",
        ["+id: Integer", "+exam_id: Integer", "+question_text: Text", "+marks: Float"],
        ["+to_dict(include_choices)"],
        LIGHT_BLUE, BLUE)
    mx["Choice"] = draw_class(430, 85, "Choice",
        ["+id: Integer", "+question_id: Integer", "+choice_label: String", "+is_correct: Bool"],
        ["+to_dict()"],
        LIGHT_BLUE, BLUE)
    mx["Student"] = draw_class(45, 300, "Student",
        ["+id: Integer", "+name: String", "+matricule: String", "+email: String"],
        ["+to_dict()"],
        LIGHT_BLUE, BLUE)
    mx["Result"] = draw_class(240, 300, "Result",
        ["+id: Integer", "+student_id: Integer", "+exam_id: Integer", "+score: Float", "+percentage: Float"],
        ["+to_dict()"],
        LIGHT_BLUE, BLUE)
    mx["AICorrection"] = draw_class(430, 300, "AICorrection",
        ["+question_id: Integer", "+student_text: Text", "+ai_score: Float", "+teacher_score: Float"],
        ["+to_dict()"],
        LIGHT_BLUE, BLUE)

    # Services package
    draw.rectangle([630, 58, 1170, 480], fill=(250, 255, 250), outline=GREEN, width=2)
    draw.text((635, 62), "«Services»", font=fb, fill=GREEN)

    sx = {}
    sx["ExamService"] = draw_class(645, 85, "ExamService",
        [],
        ["+create_exam(data)", "+get_all_exams()", "+get_exam_by_id(id)", "+create_question()", "+get_statistics(id)"],
        LIGHT_GREEN, GREEN)
    sx["GradingService"] = draw_class(845, 85, "GradingService",
        [],
        ["+grade_mcq_answers(exam_id, answers)", "+save_result(data)", "+get_results_for_exam(id)"],
        LIGHT_GREEN, GREEN)
    sx["ScannerService"] = draw_class(645, 290, "ScannerService",
        [],
        ["+load_image(file)", "+scan_and_grade(file, exam_id)", "+full_preprocess(img)"],
        LIGHT_GREEN, GREEN)
    sx["AIService"] = draw_class(845, 290, "AIService",
        [],
        ["+run_ocr(file, question_ids)", "+run_evaluation(answers)", "+save_correction(data)"],
        LIGHT_GREEN, GREEN)

    # Scanner package
    draw.rectangle([30, 495, 600, 720], fill=(255, 252, 240), outline=ORANGE, width=2)
    draw.text((35, 499), "«Scanner Pipeline»", font=fb, fill=ORANGE)

    draw_class(45, 515, "ImagePreprocessor",
        [],
        ["+to_grayscale()", "+threshold()", "+deskew()", "+full_preprocess()"],
        LIGHT_ORANGE, ORANGE)
    draw_class(240, 515, "BubbleDetector",
        ["+fill_threshold: float"],
        ["+detect(image, top_y, bottom_y)", "-_filter_contours()", "-_remove_duplicates()"],
        LIGHT_ORANGE, ORANGE)
    draw_class(430, 515, "MarkerFinder",
        [],
        ["+find_triangles(image)", "+find_section_boundaries(triangles)"],
        LIGHT_ORANGE, ORANGE)

    # AI package
    draw.rectangle([630, 495, 1170, 720], fill=(252, 240, 255), outline=PURPLE, width=2)
    draw.text((635, 499), "«AI Inference»", font=fb, fill=PURPLE)

    draw_class(645, 515, "ModelLoader",
        ["+model_id: str", "+quantization: str"],
        ["+get_model()", "+generate(image, prompt)", "+is_loaded()", "+get_status()"],
        LIGHT_PURPLE, PURPLE)
    draw_class(845, 515, "AnswerEvaluator",
        [],
        ["+evaluate_answer(q_id, text, ref)", "+build_rag_context()", "+parse_grade_response()"],
        LIGHT_PURPLE, PURPLE)

    # Relationships (simplified)
    # Exam 1-N Question
    arrow(draw, 217, 140, 240, 140, BLUE, 2, 7)
    # Question 1-N Choice
    arrow(draw, 415, 140, 430, 140, BLUE, 2, 7)
    # Student 1-N Result
    arrow(draw, 217, 355, 240, 355, BLUE, 2, 7)

    # Services -> Models
    dashed_line(draw, 645, 160, 520, 160, MED_GREY, 1)
    dashed_line(draw, 845, 200, 415, 355, MED_GREY, 1)
    dashed_line(draw, 720, 400, 630, 400, MED_GREY, 1)
    dashed_line(draw, 920, 400, 625, 400, MED_GREY, 1)

    save(img, "class-diagram.png")


# ---------------------------------------------------------------------------
# 4. Deployment Diagram
# ---------------------------------------------------------------------------
def generate_deployment():
    W, H = 1200, 800
    img, draw = new_image(W, H, BG)
    fb = try_font_bold(15)
    fn = try_font(13)
    fsm = try_font(11)
    title_bar(draw, W, "SmartGrader — Deployment Diagram", fb, fn)

    def node(x, y, w, h, label, fill, outline, icon=""):
        # Node 3D effect
        offset = 10
        draw.rectangle([x + offset, y + offset, x + w + offset, y + h + offset],
                       fill=(200, 200, 200), outline=DARK_GREY, width=1)
        rounded_rect(draw, x, y, x + w, y + h, fill=fill, outline=outline, radius=6, width=2)
        centered_text(draw, x + w // 2, y + 20, label, fb, outline)
        draw.line([x, y + 35, x + w, y + 35], fill=outline, width=1)
        return x + w // 2, y + h // 2

    def artifact(x, y, w, h, label, fill, outline):
        rounded_rect(draw, x, y, x + w, y + h, fill=fill, outline=outline, radius=4, width=1)
        centered_text(draw, x + w // 2, y + h // 2, label, fn, outline)

    # === LAN Mode (left side) ===
    draw.rectangle([30, 60, 560, 760], fill=(245, 248, 255), outline=BLUE, width=2)
    draw.text((35, 65), "LAN / Classroom Mode", font=fb, fill=BLUE)

    # Browser node
    node(50, 90, 200, 120, "Teacher Browser", LIGHT_BLUE, BLUE)
    artifact(70, 125, 160, 35, "React SPA", LIGHT_BLUE, BLUE)

    node(50, 240, 200, 120, "Student Browser", LIGHT_GREEN, GREEN)
    artifact(70, 275, 160, 35, "React SPA (exam)", LIGHT_GREEN, GREEN)

    # Server node
    node(290, 90, 240, 380, "Application Server", LIGHT_ORANGE, ORANGE)
    artifact(305, 125, 205, 30, "Flask API  :5001", LIGHT_ORANGE, ORANGE)
    artifact(305, 165, 205, 30, "ExamService", WHITE, ORANGE)
    artifact(305, 200, 205, 30, "GradingService", WHITE, ORANGE)
    artifact(305, 235, 205, 30, "ScannerService  (OpenCV)", WHITE, ORANGE)
    artifact(305, 270, 205, 30, "AIService", WHITE, ORANGE)
    draw.line([305, 310, 510, 310], fill=ORANGE, width=1)
    artifact(305, 315, 205, 30, "SQLite Database", LIGHT_YELLOW, YELLOW)
    artifact(305, 355, 205, 30, "File Store (uploads/)", WHITE, ORANGE)
    artifact(305, 390, 205, 55, "Qwen2.5-VL-3B\n(4-bit, GPU)", LIGHT_PURPLE, PURPLE)

    # Connections LAN
    arrow(draw, 250, 150, 290, 200, MED_GREY, 2)
    arrow(draw, 250, 295, 290, 260, MED_GREY, 2)
    draw.text((255, 165), "HTTP/REST", font=fsm, fill=MED_GREY)

    # === University Mode (right side) ===
    draw.rectangle([610, 60, 1170, 760], fill=(245, 255, 248), outline=GREEN, width=2)
    draw.text((615, 65), "University / Production Mode", font=fb, fill=GREEN)

    node(625, 90, 200, 100, "Client Browsers", LIGHT_BLUE, BLUE)
    artifact(645, 120, 160, 35, "React SPA + HTTPS", LIGHT_BLUE, BLUE)

    node(870, 90, 260, 100, "Reverse Proxy", LIGHT_GREEN, GREEN)
    artifact(890, 120, 220, 35, "Nginx  :443  (SSL/TLS)", LIGHT_GREEN, GREEN)

    node(870, 225, 260, 130, "App Cluster", LIGHT_ORANGE, ORANGE)
    artifact(890, 255, 220, 30, "Gunicorn  (4 workers)", LIGHT_ORANGE, ORANGE)
    artifact(890, 295, 220, 30, "Flask WSGI App", WHITE, ORANGE)

    node(625, 250, 200, 130, "Docker Option", LIGHT_PURPLE, PURPLE)
    artifact(645, 280, 160, 30, "docker-compose.yml", LIGHT_PURPLE, PURPLE)
    artifact(645, 320, 160, 30, "nginx + app + db", WHITE, PURPLE)

    node(870, 390, 260, 100, "Database Server", LIGHT_YELLOW, YELLOW)
    artifact(890, 415, 220, 35, "PostgreSQL  or  SQLite", LIGHT_YELLOW, YELLOW)

    node(870, 520, 260, 120, "GPU Server", LIGHT_PURPLE, PURPLE)
    artifact(890, 550, 220, 30, "Qwen2.5-VL-3B (4-bit)", LIGHT_PURPLE, PURPLE)
    artifact(890, 590, 220, 30, "PyTorch + transformers", WHITE, PURPLE)

    node(625, 420, 200, 100, "File Storage", LIGHT_ORANGE, ORANGE)
    artifact(645, 450, 160, 35, "NFS  or  Object Store", LIGHT_ORANGE, ORANGE)

    # Connections University
    arrow(draw, 825, 140, 870, 140, MED_GREY, 2)
    arrow(draw, 1000, 190, 1000, 225, MED_GREY, 2)
    arrow(draw, 1000, 355, 1000, 390, MED_GREY, 2)
    arrow(draw, 1000, 490, 1000, 520, MED_GREY, 2)
    arrow(draw, 870, 310, 825, 470, MED_GREY, 2)
    dashed_line(draw, 825, 310, 870, 310, MED_GREY)
    draw.text((835, 148), "HTTPS", font=fsm, fill=MED_GREY)

    save(img, "deployment.png")


# ---------------------------------------------------------------------------
# 5. Sequence — MCQ Scan Flow
# ---------------------------------------------------------------------------
def generate_sequence_scan():
    W, H = 1200, 780
    img, draw = new_image(W, H, BG)
    fb = try_font_bold(14)
    fn = try_font(12)
    fsm = try_font(10)
    title_bar(draw, W, "SmartGrader — Sequence Diagram: MCQ Sheet Scanning", fb, fn)

    participants = [
        ("Teacher", ACTOR_FILL, ACTOR_BLUE),
        ("React UI", LIGHT_BLUE, BLUE),
        ("Flask API", LIGHT_ORANGE, ORANGE),
        ("ScannerService", LIGHT_GREEN, GREEN),
        ("MarkerFinder", LIGHT_GREEN, GREEN),
        ("BubbleDetector", LIGHT_GREEN, GREEN),
        ("GradingService", LIGHT_TEAL, TEAL),
        ("SQLite DB", LIGHT_YELLOW, YELLOW),
    ]

    xs = [70 + i * 155 for i in range(len(participants))]
    box_h = 50
    life_top = 80 + box_h
    life_bot = 750

    # Participant boxes
    for (name, fill, outline), x in zip(participants, xs):
        rounded_rect(draw, x - 60, 80, x + 60, 80 + box_h, fill=fill, outline=outline, radius=6, width=2)
        centered_text(draw, x, 80 + box_h // 2, name, fsm, outline)

    # Lifelines
    for x in xs:
        dashed_line(draw, x, life_top, x, life_bot, LIGHT_GREY, 1)

    # Messages
    messages = [
        # (from_idx, to_idx, y, label, is_return)
        (0, 1, 155, "Upload scanned sheet + exam_id", False),
        (1, 2, 195, "POST /api/scan/upload", False),
        (2, 3, 235, "scan_and_grade(file, exam_id)", False),
        (3, 7, 275, "SELECT questions for exam", False),
        (7, 3, 305, "questions[]", True),
        (3, 4, 340, "find_triangles(image)", False),
        (4, 3, 365, "triangles found", True),
        (3, 4, 395, "find_section_boundaries(triangles)", False),
        (4, 3, 420, "top_y, bottom_y", True),
        (3, 5, 450, "detect(image, top_y, bottom_y)", False),
        (5, 3, 480, "bubbles[]", True),
        (3, 3, 510, "map_bubbles → read_answers()", False),
        (3, 6, 540, "grade_mcq_answers(exam_id, answers)", False),
        (6, 7, 565, "SELECT correct choices", False),
        (7, 6, 590, "correct_choices[]", True),
        (6, 3, 615, "{score, percentage, details}", True),
        (3, 2, 645, "grading result JSON", True),
        (2, 1, 675, "{obtained_marks, percentage}", True),
        (1, 0, 705, "Display score + breakdown", True),
    ]

    for from_i, to_i, y, label, is_ret in messages:
        x1, x2 = xs[from_i], xs[to_i]
        clr = MED_GREY if is_ret else DARK_GREY
        style = "dashed" if is_ret else "solid"
        if from_i == to_i:
            # Self-call
            draw.line([(x1, y), (x1 + 30, y), (x1 + 30, y + 20), (x1, y + 20)], fill=DARK_GREY, width=1)
            draw.text((x1 + 33, y + 3), label, font=fsm, fill=DARK_GREY)
        else:
            if is_ret:
                dashed_line(draw, x1, y, x2, y, clr, 1)
                arrow(draw, x1, y, x2, y, clr, 1, 7)
            else:
                arrow(draw, x1, y, x2, y, clr, 2, 8)
            mx = (x1 + x2) // 2
            direction = 1 if x2 > x1 else -1
            draw.text((mx - 50, y - 15), label, font=fsm, fill=clr)

    save(img, "sequence-scan.png")


# ---------------------------------------------------------------------------
# 6. Sequence — AI Grading Flow
# ---------------------------------------------------------------------------
def generate_sequence_ai_grade():
    W, H = 1200, 820
    img, draw = new_image(W, H, BG)
    fb = try_font_bold(14)
    fn = try_font(12)
    fsm = try_font(10)
    title_bar(draw, W, "SmartGrader — Sequence Diagram: AI Grading Flow", fb, fn)

    participants = [
        ("Teacher", ACTOR_FILL, ACTOR_BLUE),
        ("React UI", LIGHT_BLUE, BLUE),
        ("Flask API", LIGHT_ORANGE, ORANGE),
        ("AIService", LIGHT_GREEN, GREEN),
        ("ModelLoader", LIGHT_PURPLE, PURPLE),
        ("OCRPipeline", LIGHT_TEAL, TEAL),
        ("AnswerEvaluator", LIGHT_PURPLE, PURPLE),
        ("SQLite DB", LIGHT_YELLOW, YELLOW),
    ]

    xs = [70 + i * 155 for i in range(len(participants))]
    box_h = 50
    life_top = 80 + box_h
    life_bot = 800

    for (name, fill, outline), x in zip(participants, xs):
        rounded_rect(draw, x - 60, 80, x + 60, 80 + box_h, fill=fill, outline=outline, radius=6, width=2)
        centered_text(draw, x, 80 + box_h // 2, name, fsm, outline)

    for x in xs:
        dashed_line(draw, x, life_top, x, life_bot, LIGHT_GREY, 1)

    # Stage labels
    stages = [
        (145, "Stage 1: OCR — Extract Handwritten Text"),
        (385, "Stage 2: Evaluate — AI Grading"),
        (640, "Stage 3: Correction — Teacher Review"),
    ]
    for y, label in stages:
        draw.rectangle([30, y - 3, 1170, y + 18], fill=LIGHT_YELLOW, outline=YELLOW, width=1)
        draw.text((35, y), label, font=fn, fill=YELLOW)

    messages = [
        (0, 1, 175, "Upload exam page + exam_id", False),
        (1, 2, 210, "POST /api/ai/ocr", False),
        (2, 3, 245, "run_ocr(file, question_ids)", False),
        (3, 4, 275, "get_model()", False),
        (4, 3, 300, "model + processor", True),
        (3, 5, 330, "extract_answers(image, q_ids)", False),
        (5, 4, 355, "generate(image, OCR_PROMPT)", False),
        (4, 5, 380, "raw JSON text", True),
        (5, 3, 405, "{q_id: text, ...}", True),
        (3, 2, 430, "answers[]", True),
        (2, 1, 455, "extracted text", True),
        (1, 0, 480, "Review/edit OCR results", True),
        # Stage 2
        (0, 1, 510, "Confirm + click Grade All", False),
        (1, 2, 545, "POST /api/ai/evaluate", False),
        (2, 3, 575, "run_evaluation(answers_data)", False),
        (3, 7, 600, "fetch RAG corrections (loop)", False),
        (3, 6, 625, "evaluate_answer(q_id, text, ref)", False),
        (6, 4, 650, "generate(None, EVAL_PROMPT)", False),
        (4, 6, 675, "raw JSON grade", True),
        (6, 3, 700, "{score, feedback, confidence}", True),
        (3, 2, 725, "grades[]", True),
        (2, 1, 750, "Display grades + confidence", True),
        # Stage 3
        (0, 1, 778, "Correct a grade → save", False),
        (1, 2, 800, "POST /api/ai/correct", False),
    ]

    for from_i, to_i, y, label, is_ret in messages:
        if y > life_bot - 5:
            continue
        x1, x2 = xs[from_i], xs[to_i]
        clr = MED_GREY if is_ret else DARK_GREY
        if from_i == to_i:
            draw.line([(x1, y), (x1 + 30, y), (x1 + 30, y + 18), (x1, y + 18)], fill=DARK_GREY, width=1)
            draw.text((x1 + 33, y + 2), label, font=fsm, fill=DARK_GREY)
        else:
            if is_ret:
                dashed_line(draw, x1, y, x2, y, clr, 1)
                arrow(draw, x1, y, x2, y, clr, 1, 7)
            else:
                arrow(draw, x1, y, x2, y, clr, 2, 8)
            draw.text(((x1 + x2) // 2 - 45, y - 14), label, font=fsm, fill=clr)

    save(img, "sequence-ai-grade.png")


# ---------------------------------------------------------------------------
# 7. Sequence — Authentication
# ---------------------------------------------------------------------------
def generate_sequence_auth():
    W, H = 1000, 680
    img, draw = new_image(W, H, BG)
    fb = try_font_bold(14)
    fn = try_font(12)
    fsm = try_font(10)
    title_bar(draw, W, "SmartGrader — Sequence Diagram: Authentication", fb, fn)

    participants = [
        ("Teacher/Student", ACTOR_FILL, ACTOR_BLUE),
        ("React UI", LIGHT_BLUE, BLUE),
        ("Flask API", LIGHT_ORANGE, ORANGE),
        ("AuthService", LIGHT_GREEN, GREEN),
        ("SQLite DB", LIGHT_YELLOW, YELLOW),
    ]

    xs = [90 + i * 190 for i in range(len(participants))]
    box_h = 50
    life_top = 80 + box_h
    life_bot = 660

    for (name, fill, outline), x in zip(participants, xs):
        rounded_rect(draw, x - 75, 80, x + 75, 80 + box_h, fill=fill, outline=outline, radius=6, width=2)
        centered_text(draw, x, 80 + box_h // 2, name, fsm, outline)

    for x in xs:
        dashed_line(draw, x, life_top, x, life_bot, LIGHT_GREY, 1)

    # Teacher login block
    draw.rectangle([30, 138, 970, 158], fill=LIGHT_BLUE, outline=BLUE, width=1)
    draw.text((35, 140), "Teacher Login (username + password)", font=fn, fill=BLUE)

    # Student barcode block
    draw.rectangle([30, 398, 970, 418], fill=LIGHT_GREEN, outline=GREEN, width=1)
    draw.text((35, 400), "Student Session Entry (barcode scan)", font=fn, fill=GREEN)

    messages = [
        (0, 1, 175, "Enter username + password", False),
        (1, 2, 210, "POST /api/auth/login", False),
        (2, 3, 245, "authenticate(username, password)", False),
        (3, 4, 275, "SELECT user WHERE username=?", False),
        (4, 3, 305, "user record", True),
        (3, 3, 330, "bcrypt.checkpw(password, hash)", False),
        (3, 2, 360, "JWT token", True),
        (2, 1, 385, "Set cookie + redirect to dashboard", True),

        (0, 1, 435, "Scan barcode (matricule)", False),
        (1, 2, 465, "POST /api/sessions/{id}/join", False),
        (2, 3, 495, "validate_student(matricule, session_id)", False),
        (3, 4, 525, "SELECT student + session assignment", False),
        (4, 3, 555, "student record + session", True),
        (3, 2, 585, "ExamAttempt created", True),
        (2, 1, 615, "Redirect to exam page", True),
        (1, 0, 645, "Exam interface displayed", True),
    ]

    for from_i, to_i, y, label, is_ret in messages:
        if y > life_bot - 5:
            continue
        x1, x2 = xs[from_i], xs[to_i]
        clr = MED_GREY if is_ret else DARK_GREY
        if from_i == to_i:
            draw.line([(x1, y), (x1 + 30, y), (x1 + 30, y + 18), (x1, y + 18)], fill=DARK_GREY, width=1)
            draw.text((x1 + 33, y + 2), label, font=fsm, fill=DARK_GREY)
        else:
            if is_ret:
                dashed_line(draw, x1, y, x2, y, clr, 1)
                arrow(draw, x1, y, x2, y, clr, 1, 7)
            else:
                arrow(draw, x1, y, x2, y, clr, 2, 8)
            draw.text(((x1 + x2) // 2 - 50, y - 14), label, font=fsm, fill=clr)

    save(img, "sequence-auth.png")


# ---------------------------------------------------------------------------
# 8. Sequence — Online Exam Flow
# ---------------------------------------------------------------------------
def generate_sequence_exam():
    W, H = 1000, 700
    img, draw = new_image(W, H, BG)
    fb = try_font_bold(14)
    fn = try_font(12)
    fsm = try_font(10)
    title_bar(draw, W, "SmartGrader — Sequence Diagram: Online Exam Flow", fb, fn)

    participants = [
        ("Student", ACTOR_FILL, ACTOR_BLUE),
        ("React UI", LIGHT_BLUE, BLUE),
        ("Flask API", LIGHT_ORANGE, ORANGE),
        ("ExamService", LIGHT_GREEN, GREEN),
        ("ProctorService", LIGHT_RED, RED),
        ("SQLite DB", LIGHT_YELLOW, YELLOW),
    ]

    xs = [85 + i * 180 for i in range(len(participants))]
    box_h = 50
    life_top = 80 + box_h
    life_bot = 680

    for (name, fill, outline), x in zip(participants, xs):
        rounded_rect(draw, x - 72, 80, x + 72, 80 + box_h, fill=fill, outline=outline, radius=6, width=2)
        centered_text(draw, x, 80 + box_h // 2, name, fsm, outline)

    for x in xs:
        dashed_line(draw, x, life_top, x, life_bot, LIGHT_GREY, 1)

    messages = [
        (0, 1, 155, "Enter exam (barcode auth)", False),
        (1, 2, 185, "POST /api/sessions/{id}/join", False),
        (2, 3, 215, "create_attempt(session_id, student_id)", False),
        (3, 5, 245, "INSERT exam_attempt", False),
        (5, 3, 270, "attempt_id", True),
        (3, 2, 295, "attempt created", True),
        (2, 4, 320, "start_proctoring(attempt_id)", False),
        (4, 5, 345, "log ProctorEvent: STARTED", False),
        (2, 1, 370, "Exam questions + timer", True),
        (0, 1, 400, "Answer question N", False),
        (1, 2, 425, "POST /api/attempts/{id}/answer", False),
        (2, 5, 450, "INSERT online_answer", False),
        (2, 1, 475, "Answer saved", True),
        (0, 1, 505, "Click Submit", False),
        (1, 2, 530, "POST /api/attempts/{id}/submit", False),
        (2, 3, 555, "grade_attempt(attempt_id)", False),
        (3, 5, 580, "UPDATE attempt: score + submitted_at", False),
        (3, 2, 605, "score + percentage", True),
        (2, 4, 630, "stop_proctoring(attempt_id)", False),
        (2, 1, 655, "Results screen", True),
        (1, 0, 675, "Score displayed", True),
    ]

    for from_i, to_i, y, label, is_ret in messages:
        if y > life_bot - 5:
            continue
        x1, x2 = xs[from_i], xs[to_i]
        clr = MED_GREY if is_ret else DARK_GREY
        if from_i == to_i:
            draw.line([(x1, y), (x1 + 30, y), (x1 + 30, y + 18), (x1, y + 18)], fill=DARK_GREY, width=1)
            draw.text((x1 + 33, y + 2), label, font=fsm, fill=DARK_GREY)
        else:
            if is_ret:
                dashed_line(draw, x1, y, x2, y, clr, 1)
                arrow(draw, x1, y, x2, y, clr, 1, 7)
            else:
                arrow(draw, x1, y, x2, y, clr, 2, 8)
            draw.text(((x1 + x2) // 2 - 45, y - 14), label, font=fsm, fill=clr)

    save(img, "sequence-exam.png")


# ---------------------------------------------------------------------------
# 9. Sequence — Proctoring
# ---------------------------------------------------------------------------
def generate_sequence_proctor():
    W, H = 1000, 680
    img, draw = new_image(W, H, BG)
    fb = try_font_bold(14)
    fn = try_font(12)
    fsm = try_font(10)
    title_bar(draw, W, "SmartGrader — Sequence Diagram: Proctoring System", fb, fn)

    participants = [
        ("Student\n(Browser)", ACTOR_FILL, ACTOR_BLUE),
        ("React UI\n(Webcam)", LIGHT_BLUE, BLUE),
        ("Flask API", LIGHT_ORANGE, ORANGE),
        ("ProctorService", LIGHT_RED, RED),
        ("Teacher\nDashboard", LIGHT_GREEN, GREEN),
        ("SQLite DB", LIGHT_YELLOW, YELLOW),
    ]

    xs = [85 + i * 180 for i in range(len(participants))]
    box_h = 55
    life_top = 80 + box_h
    life_bot = 660

    for (name, fill, outline), x in zip(participants, xs):
        rounded_rect(draw, x - 72, 80, x + 72, 80 + box_h, fill=fill, outline=outline, radius=6, width=2)
        wrapped_text(draw, x, 80 + box_h // 2, name, fsm, outline, max_width=135)

    for x in xs:
        dashed_line(draw, x, life_top, x, life_bot, LIGHT_GREY, 1)

    messages = [
        (0, 1, 160, "Webcam stream starts", False),
        (1, 2, 185, "POST /api/proctor/frame (base64)", False),
        (2, 3, 215, "analyze_frame(frame, attempt_id)", False),
        (3, 3, 240, "face_detection(frame)", False),
        (3, 5, 270, "SELECT attempt state", False),
        (5, 3, 295, "attempt active", True),
        (3, 3, 320, "Evaluate: faces_count, gaze, motion", False),
        (3, 2, 350, "events[] (if suspicious)", True),
        (2, 3, 380, "POST /api/proctor/event", False),
        (3, 5, 405, "INSERT proctor_event", False),
        (3, 2, 430, "event saved", True),
        (4, 2, 460, "GET /api/proctor/monitor/{session_id}", False),
        (2, 5, 485, "SELECT events + attempts", False),
        (5, 2, 510, "events + risk scores", True),
        (2, 4, 535, "Live dashboard: flags + streams", True),
        (4, 2, 560, "POST /api/proctor/flag/{attempt_id}", False),
        (2, 5, 585, "UPDATE attempt: flagged=True", False),
        (2, 1, 615, "WebSocket: alert sent to student", True),
        (1, 0, 645, "Warning displayed", True),
    ]

    for from_i, to_i, y, label, is_ret in messages:
        if y > life_bot - 5:
            continue
        x1, x2 = xs[from_i], xs[to_i]
        clr = MED_GREY if is_ret else DARK_GREY
        if from_i == to_i:
            draw.line([(x1, y), (x1 + 30, y), (x1 + 30, y + 18), (x1, y + 18)], fill=DARK_GREY, width=1)
            draw.text((x1 + 33, y + 2), label, font=fsm, fill=DARK_GREY)
        else:
            if is_ret:
                dashed_line(draw, x1, y, x2, y, clr, 1)
                arrow(draw, x1, y, x2, y, clr, 1, 7)
            else:
                arrow(draw, x1, y, x2, y, clr, 2, 8)
            draw.text(((x1 + x2) // 2 - 45, y - 14), label, font=fsm, fill=clr)

    save(img, "sequence-proctor.png")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  SmartGrader Diagram Generator")
    print("=" * 60)
    print(f"  Output directory: {OUT_DIR}")
    print()

    generators = [
        ("use-case.png",         generate_use_case),
        ("er-diagram.png",        generate_er_diagram),
        ("class-diagram.png",     generate_class_diagram),
        ("deployment.png",        generate_deployment),
        ("sequence-scan.png",     generate_sequence_scan),
        ("sequence-ai-grade.png", generate_sequence_ai_grade),
        ("sequence-auth.png",     generate_sequence_auth),
        ("sequence-exam.png",     generate_sequence_exam),
        ("sequence-proctor.png",  generate_sequence_proctor),
    ]

    success = 0
    for name, fn in generators:
        try:
            fn()
            success += 1
        except Exception as exc:
            print(f"  ERROR generating {name}: {exc}")
            import traceback; traceback.print_exc()

    print()
    print(f"  Done: {success}/{len(generators)} diagrams generated")
    print()

    # List generated files
    for name, _ in generators:
        p = OUT_DIR / name
        if p.exists():
            print(f"  OK  {p.name}  ({p.stat().st_size // 1024} KB)")
        else:
            print(f"  MISSING  {name}")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
