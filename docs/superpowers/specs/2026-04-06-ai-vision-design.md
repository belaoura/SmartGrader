# SmartGrader AI Vision Model -- Design Specification

**Date:** 2026-04-06
**Status:** Approved
**Depends on:** Sub-Project 1 (Code Restructuring) + Sub-Project 2 (Web UI) -- both complete

---

## 1. Overview

Integrate Qwen2.5-VL-3B-Instruct (4-bit quantized) into SmartGrader for automatic grading of handwritten short-answer exams. Students write answers directly on the question paper, which is scanned and processed through a two-stage pipeline: OCR (extract handwritten text) then evaluation (grade against reference). A RAG feedback loop improves accuracy over time via teacher corrections.

### Goals
- OCR handwritten answers in French, Arabic, and English
- Grade short answers against model answers or keyword rubrics
- Flag low-confidence grades for teacher review (confidence < 0.7)
- Improve accuracy over time via RAG feedback loop (no fine-tuning)

### Constraints
- GPU: 6-8 GB VRAM -- model must fit with 4-bit quantization (~2.5GB)
- Single inference at a time (no batching across requests)
- Must not block Flask server -- model loads lazily on first request

---

## 2. Model

**Model:** `Qwen/Qwen2.5-VL-3B-Instruct`
**Quantization:** 4-bit via `bitsandbytes` (`BitsAndBytesConfig` with `load_in_4bit=True`, `bnb_4bit_compute_dtype=float16`)
**Memory:** ~2.5GB VRAM, leaving 4-5GB for inference context
**Loading:** Lazy singleton -- loads on first `/api/ai/*` request, stays in GPU memory

**Dependencies:**
```
transformers>=4.45.0
bitsandbytes>=0.44.0
accelerate>=1.0.0
torch>=2.4.0
qwen-vl-utils>=0.0.8
```

---

## 3. Architecture

### New Files

```
app/ai/
├── __init__.py              # (exists)
├── model_loader.py          # Lazy singleton: load model + processor, generate()
├── ocr_pipeline.py          # Stage 1: full-page OCR, extract text per question
├── answer_evaluator.py      # Stage 2: grade text vs reference/keywords
└── prompt_templates.py      # All prompt strings

app/models/ai_correction.py  # AICorrection SQLAlchemy model
app/services/ai_service.py   # Orchestrates OCR → evaluate → store
app/routes/ai.py             # /api/ai/* endpoints
app/errors.py                # Add AIModelError exception

frontend/src/hooks/use-ai.js                    # TanStack hooks
frontend/src/components/scanner/OCRResults.jsx   # Editable OCR output
frontend/src/components/scanner/AIGradeResults.jsx # AI grades + correction
```

### Data Flow

```
Teacher uploads scanned exam page
    ↓
POST /api/ai/ocr  →  Qwen2.5-VL processes full page  →  returns extracted text per question
    ↓
Teacher reviews/corrects OCR text in editable fields
    ↓
POST /api/ai/evaluate  →  Qwen2.5-VL grades each answer (text-only)  →  returns scores + feedback
    ↓
Teacher reviews grades, corrects low-confidence ones
    ↓
POST /api/ai/correct  →  stores correction in ai_corrections table for RAG
```

---

## 4. Model Loader (`model_loader.py`)

Singleton pattern -- module-level variable holds model + processor after first load.

```python
_model = None
_processor = None

def get_model():
    """Load model lazily. Returns (model, processor) tuple."""
    global _model, _processor
    if _model is None:
        # Load with 4-bit quantization
        ...
    return _model, _processor

def generate(image, prompt, max_new_tokens=512):
    """Run inference. image is PIL Image or None (text-only)."""
    model, processor = get_model()
    # Build messages, process, generate, decode
    ...
    return output_text
```

If no GPU available or model fails to load, raises `AIModelError` (status 503).

---

## 5. Two-Stage Pipeline

### Stage 1: OCR (`ocr_pipeline.py`)

**Input:** Scanned page image (PIL Image) + list of question numbers
**Output:** Dict mapping question number → extracted text

Sends the full page to the model with a single prompt:

```
Look at this scanned exam paper. Students wrote their answers directly on the paper.
Extract the handwritten answer for each question listed below.
The text may be in French, Arabic, or English.

Questions to extract: Q1, Q2, Q3

Return JSON:
{"answers": [
  {"question": 1, "text": "<extracted text>"},
  {"question": 2, "text": "<extracted text>"},
  {"question": 3, "text": "<extracted text>"}
]}
```

**Why full-page (not cropped zones):**
- No zone detection needed on the question paper
- Model sees question + answer context together
- Single inference for all questions (faster)

**JSON parsing:** Parse with `json.loads()`. On failure, retry once with stricter prompt. If still fails, return empty text and confidence 0.0.

### Stage 2: Evaluation (`answer_evaluator.py`)

**Input:** Extracted text + reference answer or keywords + question context
**Output:** Score, feedback, confidence per question

**Text-only** -- no image needed. Uses same model via `generate(image=None, prompt=...)`.

**Model answer mode prompt:**
```
You are grading a student's answer.

Question: {question_text}
Reference answer: {model_answer}
Student's answer: {extracted_text}
Maximum marks: {max_marks}

Grade the student's answer. Return JSON:
{"score": <number>, "max": <number>, "feedback": "<brief explanation>", "confidence": <0.0-1.0>}
```

**Keywords mode prompt:**
```
You are grading a student's answer.

Question: {question_text}
Required concepts: {keywords_list}
Student's answer: {extracted_text}
Maximum marks: {max_marks}

Check which required concepts appear in the answer. Return JSON:
{"score": <number>, "max": <number>, "found_concepts": [...], "missing_concepts": [...], "confidence": <0.0-1.0>}
```

---

## 6. RAG Feedback Loop

### Database Model (`app/models/ai_correction.py`)

```python
class AICorrection(db.Model):
    __tablename__ = "ai_corrections"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    student_text = db.Column(db.Text, nullable=False)
    ai_score = db.Column(db.Float, nullable=False)
    ai_feedback = db.Column(db.Text)
    teacher_score = db.Column(db.Float, nullable=False)
    teacher_feedback = db.Column(db.Text)
    created_at = db.Column(db.String(30), nullable=False)
```

### How RAG Enhances Grading

Before evaluating a new answer:

1. Query `ai_corrections` for corrections on the same `question_id`
2. Take up to 3 most recent corrections
3. Inject as few-shot examples in the evaluation prompt:

```
Here are examples of how this question was graded previously:
- Student wrote: "{past_text}" -> Score: {teacher_score}/{max} because: {teacher_feedback}
- Student wrote: "{past_text2}" -> Score: {teacher_score2}/{max} because: {teacher_feedback2}

Now grade this new answer:
...
```

### Confidence Threshold

If `confidence < 0.7` in the model output, the API response includes `"needs_review": true`. The frontend highlights these grades in amber.

---

## 7. API Endpoints

```
POST /api/ai/ocr
  Body: multipart (file: image, exam_id: int, question_ids: JSON array)
  Returns: {"answers": [{"question_id": 1, "text": "..."}, ...]}

POST /api/ai/evaluate
  Body: JSON {"exam_id": int, "answers": [{"question_id": 1, "text": "...", "reference": "...", "mode": "model_answer|keywords", "keywords": [...]}]}
  Returns: {"grades": [{"question_id": 1, "score": 4, "max": 5, "feedback": "...", "confidence": 0.85, "needs_review": false}, ...]}

POST /api/ai/correct
  Body: JSON {"question_id": int, "student_text": "...", "ai_score": float, "ai_feedback": "...", "teacher_score": float, "teacher_feedback": "..."}
  Returns: {"message": "Correction saved", "id": int}

GET /api/ai/corrections/<question_id>
  Returns: [{"id": 1, "student_text": "...", "ai_score": 3, "teacher_score": 4, ...}, ...]

GET /api/ai/status
  Returns: {"model_loaded": true, "model_name": "Qwen2.5-VL-3B", "device": "cuda", "gpu_memory_used": "2.5GB"}
```

---

## 8. Frontend Integration

**Scanner page extended** with a mode toggle: "MCQ Scanning" | "Short Answer Grading"

**Short Answer Grading flow:**

1. Select exam + upload scanned page
2. Click "Extract Answers" → `POST /api/ai/ocr`
3. `OCRResults.jsx` shows extracted text in editable text fields per question
4. Teacher corrects OCR errors, provides reference answers if not set
5. Click "Grade All" → `POST /api/ai/evaluate`
6. `AIGradeResults.jsx` shows per-question: score, feedback, confidence badge
7. Low-confidence grades (< 0.7) highlighted amber with "Review" prompt
8. Teacher clicks "Correct" → dialog to set correct score/feedback → `POST /api/ai/correct`

**New hook:** `frontend/src/hooks/use-ai.js`
- `useOCR()` -- mutation for OCR extraction
- `useEvaluate()` -- mutation for grading
- `useCorrect()` -- mutation for saving corrections
- `useAIStatus()` -- query for model status

**New components:**
- `OCRResults.jsx` -- editable text fields showing extracted answers
- `AIGradeResults.jsx` -- grade display with confidence indicators and correction buttons

---

## 9. Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Full-page OCR | Single prompt for all questions | Faster than per-zone cropping, model sees context |
| Lazy model loading | Load on first request | Avoids slow Flask startup |
| Text-only Stage 2 | No image for evaluation | Faster inference, teacher can correct OCR first |
| RAG not fine-tuning | Few-shot examples from corrections | Fits 6-8GB VRAM, no training needed |
| Confidence 0.7 threshold | Flag below for review | Balances automation with safety |
| Same model both stages | Qwen2.5-VL for OCR and eval | Simplicity, single model to manage |
| Scanner page extension | Mode toggle, not new page | Reuses existing upload flow |
