"""Tests for image preprocessor."""

import numpy as np
import pytest
from app.scanner.preprocessor import ImagePreprocessor


def _make_test_image(width=800, height=1000):
    """Create a synthetic test image (white with black rectangles)."""
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    img[100:150, 100:700] = 0
    img[200:250, 100:700] = 0
    return img


def test_preprocessor_init():
    preprocessor = ImagePreprocessor()
    assert preprocessor.original is None


def test_load_from_array():
    img = _make_test_image()
    preprocessor = ImagePreprocessor()
    preprocessor.load_from_array(img)
    assert preprocessor.original is not None
    assert preprocessor.original.shape == (1000, 800, 3)


def test_to_grayscale():
    img = _make_test_image()
    preprocessor = ImagePreprocessor()
    preprocessor.load_from_array(img)
    gray = preprocessor.to_grayscale()
    assert len(gray.shape) == 2


def test_reduce_noise():
    img = _make_test_image()
    preprocessor = ImagePreprocessor()
    preprocessor.load_from_array(img)
    preprocessor.to_grayscale()
    blurred = preprocessor.reduce_noise(kernel_size=5)
    assert blurred.shape == preprocessor.gray.shape


def test_threshold_otsu():
    img = _make_test_image()
    preprocessor = ImagePreprocessor()
    preprocessor.load_from_array(img)
    preprocessor.to_grayscale()
    thresh = preprocessor.threshold(method="otsu")
    assert thresh is not None
    unique_values = np.unique(thresh)
    assert len(unique_values) <= 2


def test_full_preprocess():
    img = _make_test_image()
    preprocessor = ImagePreprocessor()
    preprocessor.load_from_array(img)
    result = preprocessor.full_preprocess(deskew=False, auto_crop=False)
    assert result is not None
    assert len(result.shape) == 2
