"""Lazy singleton loader for Qwen2.5-VL-3B-Instruct.

Loads the model on first call to get_model(). Keeps it in GPU memory.
"""

import logging
from app.errors import AIModelError

try:
    import torch
except ImportError:  # pragma: no cover
    import unittest.mock as _mock
    torch = _mock.MagicMock()
    torch.cuda.is_available.return_value = False

logger = logging.getLogger("smartgrader.ai.model_loader")

_model = None
_processor = None

MODEL_ID = "Qwen/Qwen2.5-VL-3B-Instruct"


def get_model():
    """Load model and processor lazily. Returns (model, processor) tuple."""
    global _model, _processor

    if _model is not None:
        return _model, _processor

    if not torch.cuda.is_available():
        raise AIModelError("No GPU available. AI grading requires a CUDA-compatible GPU.")

    try:
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        from transformers import BitsAndBytesConfig

        logger.info("Loading AI model: %s (4-bit quantization)...", MODEL_ID)

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
        )

        _model = Qwen2VLForConditionalGeneration.from_pretrained(
            MODEL_ID,
            quantization_config=bnb_config,
            device_map="auto",
        )
        _processor = AutoProcessor.from_pretrained(MODEL_ID)

        logger.info("AI model loaded successfully on %s", _model.device)
        return _model, _processor

    except Exception as e:
        _model = None
        _processor = None
        logger.error("Failed to load AI model: %s", e)
        raise AIModelError(f"Failed to load AI model: {e}")


def generate(image, prompt, max_new_tokens=512):
    """Run inference with the vision model.

    Args:
        image: PIL Image for vision tasks, or None for text-only.
        prompt: The text prompt.
        max_new_tokens: Maximum tokens to generate.

    Returns:
        Generated text string.
    """
    model, processor = get_model()

    content = []
    if image is not None:
        content.append({"type": "image", "image": image})
    content.append({"type": "text", "text": prompt})

    messages = [{"role": "user", "content": content}]

    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text], images=[image] if image else None, return_tensors="pt")
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        output_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)

    # Decode only the generated tokens (skip input tokens)
    generated_ids = output_ids[:, inputs["input_ids"].shape[1]:]
    result = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    logger.debug("Generated %d chars from prompt (%d chars)", len(result), len(prompt))
    return result.strip()


def is_loaded():
    """Check if the model is currently loaded."""
    return _model is not None


def get_status():
    """Return model status info."""
    if not torch.cuda.is_available():
        return {"model_loaded": False, "device": "none", "error": "No GPU available"}

    status = {
        "model_loaded": _model is not None,
        "model_name": MODEL_ID,
        "device": "cuda" if _model is not None else "not loaded",
    }

    if _model is not None:
        mem = torch.cuda.memory_allocated() / 1024 / 1024 / 1024
        status["gpu_memory_used"] = f"{mem:.1f}GB"

    return status
