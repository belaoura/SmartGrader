"""Maps detected bubbles to question/choice grid."""

import logging

logger = logging.getLogger("smartgrader.scanner.grid_mapper")

CHOICE_LABELS = ["A", "B", "C", "D", "E", "F"]


def map_bubbles_to_questions(bubbles, questions):
    """Map detected bubbles to questions using choice counts from database.

    Args:
        bubbles: List of bubble dicts with keys: x, y, r, area, col.
        questions: List of question dicts with keys: id, choices_count, marks.

    Returns:
        Tuple of (mapped_bubbles dict, list of mapped question ids).
    """
    left_col = sorted([b for b in bubbles if b["col"] == "L"], key=lambda b: b["y"])
    right_col = sorted([b for b in bubbles if b["col"] == "R"], key=lambda b: b["y"])

    questions_sorted = sorted(questions, key=lambda q: q["id"])

    left_count = len(left_col)
    left_questions = []
    bubble_used = 0
    for q in questions_sorted:
        if bubble_used + q["choices_count"] <= left_count:
            left_questions.append(q)
            bubble_used += q["choices_count"]
        else:
            break

    right_questions = [q for q in questions_sorted if q not in left_questions]

    result = {}
    mapped_ids = []

    _assign_column(left_col, left_questions, result, mapped_ids)
    _assign_column(right_col, right_questions, result, mapped_ids)

    logger.info("Mapped %d bubbles to %d questions", len(result), len(mapped_ids))
    return result, mapped_ids


def _assign_column(col_bubbles, questions, result, mapped_ids):
    """Assign bubbles in a column to questions sequentially."""
    idx = 0
    for q in questions:
        count = q["choices_count"]
        q_id = q["id"]

        q_bubbles = []
        while idx < len(col_bubbles) and len(q_bubbles) < count:
            q_bubbles.append(col_bubbles[idx])
            idx += 1

        if len(q_bubbles) < count:
            logger.warning("Q%d: expected %d bubbles, got %d", q_id, count, len(q_bubbles))
            break

        mapped_ids.append(q_id)
        for j, bubble in enumerate(q_bubbles):
            if j < len(CHOICE_LABELS):
                label = CHOICE_LABELS[j]
                bubble["question"] = q_id
                bubble["choice"] = label
                bubble["label"] = f"Q{q_id}{label}"
                result[f"Q{q_id}{label}"] = bubble
