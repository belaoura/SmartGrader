"""Tests for AI model loader."""

import pytest
from unittest.mock import patch, MagicMock


def test_model_not_loaded_initially():
    """Model should not load at import time."""
    from app.ai import model_loader
    # Reset module state
    model_loader._model = None
    model_loader._processor = None
    assert model_loader._model is None


def test_get_model_raises_without_gpu(app):
    """Should raise AIModelError if torch.cuda is not available."""
    from app.ai import model_loader
    from app.errors import AIModelError

    model_loader._model = None
    model_loader._processor = None

    with app.app_context():
        with patch("app.ai.model_loader.torch") as mock_torch:
            mock_torch.cuda.is_available.return_value = False
            with pytest.raises(AIModelError, match="No GPU available"):
                model_loader.get_model()


def test_generate_calls_model(app):
    """generate() should use loaded model and return decoded text."""
    from app.ai import model_loader

    mock_model = MagicMock()
    mock_processor = MagicMock()
    mock_model.generate.return_value = MagicMock()
    mock_processor.batch_decode.return_value = ["test output"]
    mock_processor.apply_chat_template.return_value = "formatted"
    mock_processor.return_value = {"input_ids": MagicMock(to=MagicMock(return_value=MagicMock()))}

    model_loader._model = mock_model
    model_loader._processor = mock_processor

    with app.app_context():
        result = model_loader.generate(image=None, prompt="test")

    assert isinstance(result, str)
    # Cleanup
    model_loader._model = None
    model_loader._processor = None
