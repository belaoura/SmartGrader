"""Tests for OCR pipeline."""

import json
from unittest.mock import patch
from app.ai.ocr_pipeline import extract_answers, parse_ocr_response


def test_parse_valid_json():
    raw = '{"answers": [{"question": 1, "text": "hello"}, {"question": 2, "text": "world"}]}'
    result = parse_ocr_response(raw)
    assert len(result) == 2
    assert result[1] == "hello"
    assert result[2] == "world"


def test_parse_json_with_markdown_wrapper():
    raw = '```json\n{"answers": [{"question": 1, "text": "test"}]}\n```'
    result = parse_ocr_response(raw)
    assert result[1] == "test"


def test_parse_invalid_json():
    raw = "This is not JSON at all"
    result = parse_ocr_response(raw)
    assert result == {}


def test_extract_answers_calls_generate(app):
    from PIL import Image
    import numpy as np

    img = Image.fromarray(np.ones((100, 100, 3), dtype=np.uint8) * 255)
    mock_response = '{"answers": [{"question": 1, "text": "photosynthesis"}]}'

    with app.app_context():
        with patch("app.ai.ocr_pipeline.generate", return_value=mock_response):
            result = extract_answers(img, [1])

    assert result[1] == "photosynthesis"
