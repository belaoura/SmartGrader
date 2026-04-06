"""Tests for bubble detector."""

import numpy as np
import cv2
from app.scanner.detector import BubbleDetector, check_if_filled


def _make_bubble_image(width=800, height=1000, bubble_positions=None):
    """Create a white image with black circles at specified positions."""
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    if bubble_positions:
        for (cx, cy, r) in bubble_positions:
            cv2.circle(img, (cx, cy), r, (0, 0, 0), -1)
    return img


def test_detector_init():
    detector = BubbleDetector()
    assert detector.area_min == 60
    assert detector.circularity_min == 0.65


def test_detector_custom_params():
    detector = BubbleDetector(area_min=100, area_max=500)
    assert detector.area_min == 100
    assert detector.area_max == 500


def test_detect_no_bubbles():
    img = _make_bubble_image()
    detector = BubbleDetector()
    bubbles = detector.detect(img, top_y=100, bottom_y=900)
    assert len(bubbles) == 0


def test_check_filled_bubble():
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    cv2.circle(img, (50, 50), 15, (0, 0, 0), -1)
    bubble = {"x": 50, "y": 50, "r": 15}
    is_filled, pct = check_if_filled(img, bubble, fill_threshold=50)
    assert is_filled is True
    assert pct > 80


def test_check_empty_bubble():
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    cv2.circle(img, (50, 50), 15, (0, 0, 0), 2)
    bubble = {"x": 50, "y": 50, "r": 15}
    is_filled, pct = check_if_filled(img, bubble, fill_threshold=50)
    assert is_filled is False
    assert pct < 50
