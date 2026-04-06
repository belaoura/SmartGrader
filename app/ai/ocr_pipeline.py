"""Stage 1: Extract handwritten text from scanned exam pages."""

import json
import logging
import re
from app.ai.model_loader import generate
from app.ai.prompt_templates import OCR_PROMPT, OCR_RETRY_PROMPT

logger = logging.getLogger("smartgrader.ai.ocr_pipeline")


def extract_answers(image, question_ids):
    """Extract handwritten answers from a scanned exam page.

    Args:
        image: PIL Image of the scanned page.
        question_ids: List of question ID integers to extract.

    Returns:
        Dict mapping question_id -> extracted text string.
    """
    question_list = ", ".join(f"Q{qid}" for qid in question_ids)
    prompt = OCR_PROMPT.format(question_list=question_list)

    logger.info("Running OCR for questions: %s", question_list)
    raw_output = generate(image=image, prompt=prompt)
    result = parse_ocr_response(raw_output)

    if not result:
        logger.warning("OCR parse failed, retrying with stricter prompt")
        raw_output = generate(image=image, prompt=OCR_RETRY_PROMPT)
        result = parse_ocr_response(raw_output)

    if not result:
        logger.error("OCR failed after retry. Raw output: %s", raw_output[:200])
        return {qid: "" for qid in question_ids}

    # Ensure all requested question_ids have entries
    for qid in question_ids:
        if qid not in result:
            result[qid] = ""

    logger.info("OCR extracted %d/%d answers", sum(1 for v in result.values() if v), len(question_ids))
    return result


def parse_ocr_response(raw_text):
    """Parse model output into {question_id: text} dict.

    Handles raw JSON or JSON wrapped in markdown code blocks.
    """
    text = raw_text.strip()

    # Strip markdown code block wrapper if present
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)

    # Try to find JSON object in the text
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        text = text[start:end]

    try:
        data = json.loads(text)
        answers = data.get("answers", [])
        return {item["question"]: item["text"] for item in answers}
    except (json.JSONDecodeError, KeyError, TypeError):
        return {}
