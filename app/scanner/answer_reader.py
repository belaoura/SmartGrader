"""Reads student answers from mapped bubbles."""

import logging
from app.scanner.detector import check_if_filled

logger = logging.getLogger("smartgrader.scanner.answer_reader")

CHOICE_LABELS = ["A", "B", "C", "D", "E", "F"]


def read_answers(image, mapped_bubbles, questions, fill_threshold=50):
    """Read detected answers from mapped bubbles.

    Args:
        image: BGR image.
        mapped_bubbles: Dict from grid_mapper.map_bubbles_to_questions().
        questions: List of question dicts with keys: id, choices_count.
        fill_threshold: Minimum fill percentage to consider a bubble selected.

    Returns:
        Dict mapping question_id -> detected choice label (or None if unanswered).
    """
    answers = {}

    for q in questions:
        q_id = q["id"]
        best_fill = 0.0
        best_choice = None

        for label in CHOICE_LABELS[: q["choices_count"]]:
            key = f"Q{q_id}{label}"
            if key not in mapped_bubbles:
                continue

            bubble = mapped_bubbles[key]
            _, fill_pct = check_if_filled(image, bubble, fill_threshold)

            if fill_pct > best_fill:
                best_fill = fill_pct
                best_choice = label

        if best_fill >= fill_threshold:
            answers[q_id] = best_choice
            logger.debug("Q%d: detected %s (%.1f%%)", q_id, best_choice, best_fill)
        else:
            answers[q_id] = None
            logger.debug("Q%d: unanswered (best fill %.1f%%)", q_id, best_fill)

    answered = sum(1 for v in answers.values() if v is not None)
    logger.info("Read answers: %d/%d answered", answered, len(questions))
    return answers
