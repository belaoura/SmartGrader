"""Scanning orchestration service."""

import logging
import os
import cv2
import numpy as np

from app.scanner.preprocessor import ImagePreprocessor
from app.scanner.marker_finder import find_triangles, find_section_boundaries
from app.scanner.detector import BubbleDetector
from app.scanner.grid_mapper import map_bubbles_to_questions
from app.scanner.answer_reader import read_answers
from app.services.exam_service import get_exam_by_id, get_questions_for_exam
from app.services.grading_service import grade_mcq_answers
from app.errors import ScannerError, DetectionError

logger = logging.getLogger("smartgrader.services.scanner")


def load_image(file_path):
    """Load image from file (supports PDF and image formats)."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        try:
            import fitz
            doc = fitz.open(file_path)
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            doc.close()
            logger.info("Loaded PDF: %s (%dx%d)", file_path, img.shape[1], img.shape[0])
            return img
        except ImportError:
            raise ScannerError("PyMuPDF (fitz) is required for PDF scanning")
    else:
        img = cv2.imread(file_path)
        if img is None:
            raise ScannerError(f"Could not load image: {file_path}")
        logger.info("Loaded image: %s (%dx%d)", file_path, img.shape[1], img.shape[0])
        return img


def scan_and_grade(file_path, exam_id, fill_threshold=50, save_debug=None):
    """Full scanning and grading pipeline."""
    image = load_image(file_path)

    exam = get_exam_by_id(exam_id)
    questions_data = get_questions_for_exam(exam_id)
    questions = [
        {
            "id": q["id"],
            "choices_count": q["choices_number"],
            "marks": q["marks"],
        }
        for q in questions_data
    ]

    if not questions:
        raise ScannerError(f"Exam {exam_id} has no questions")

    triangles = find_triangles(image)
    boundaries = find_section_boundaries(image, triangles)

    if boundaries is None:
        raise DetectionError("Could not detect 4 triangle markers on the sheet")

    top_y, bottom_y = boundaries

    detector = BubbleDetector(area_min=60, area_max=600, circularity_min=0.65)
    bubbles = detector.detect(image, top_y, bottom_y)

    if not bubbles:
        raise DetectionError("No bubbles detected in the answer section")

    mapped_bubbles, mapped_ids = map_bubbles_to_questions(bubbles, questions)

    if not mapped_bubbles:
        raise DetectionError("Could not map bubbles to questions")

    detected_answers = read_answers(image, mapped_bubbles, questions, fill_threshold)
    result = grade_mcq_answers(exam_id, detected_answers)

    if save_debug:
        _save_debug_image(image, mapped_bubbles, top_y, bottom_y, save_debug)

    logger.info(
        "Scan complete for exam %d: %s/%s (%.1f%%)",
        exam_id, result["obtained_marks"], result["total_marks"], result["percentage"],
    )
    return result


def _save_debug_image(image, mapped_bubbles, top_y, bottom_y, output_dir):
    """Save annotated debug image."""
    os.makedirs(output_dir, exist_ok=True)
    result_img = image.copy()

    cv2.line(result_img, (0, top_y), (image.shape[1], top_y), (255, 0, 0), 4)
    cv2.line(result_img, (0, bottom_y), (image.shape[1], bottom_y), (255, 0, 0), 4)

    colors = [(0, 255, 0), (0, 255, 255), (255, 0, 255), (0, 128, 255), (128, 0, 255)]
    for label, bubble in mapped_bubbles.items():
        q_num = bubble.get("question", 0)
        color = colors[q_num % len(colors)]
        cv2.circle(result_img, (bubble["x"], bubble["y"]), bubble["r"], color, 3)
        cv2.putText(
            result_img, label,
            (bubble["x"] + 15, bubble["y"] + 4),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2,
        )

    filepath = os.path.join(output_dir, "scan_result.jpg")
    cv2.imwrite(filepath, result_img)
    logger.info("Saved debug image: %s", filepath)
