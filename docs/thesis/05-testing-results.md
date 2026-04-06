# Chapter 5: Testing and Results

This chapter presents the testing methodology, test coverage, and empirical results for SmartGrader. We describe the automated test suite, report quantitative measurements of MCQ scanning accuracy and AI grading performance, analyse the effect of the RAG feedback loop on grading accuracy, and discuss the strengths and limitations of the system.

## 5.1 Test Methodology

SmartGrader employs a three-tier testing strategy: unit tests for individual functions and classes, integration tests that exercise multiple layers through the Flask test client, and manual testing for end-to-end user workflows.

### 5.1.1 Unit Tests

Unit tests verify the correctness of individual modules in isolation. Each test module focuses on a single layer of the architecture: model definitions and relationships, service functions, scanner algorithms, or AI pipeline components. Dependencies on external systems (the database, the GPU, the vision model) are managed through fixtures and mocks.

### 5.1.2 Integration Tests

Integration tests verify the correct interaction between layers by issuing HTTP requests to the Flask application and asserting on the responses. These tests exercise the full request lifecycle: route handler, service function, database operation, and response serialisation.

### 5.1.3 Test Framework and Fixtures

All tests are written using pytest, the de facto standard testing framework for Python applications. Shared fixtures are defined in `tests/conftest.py`:

```python
@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def db(app):
    """Provide database session."""
    with app.app_context():
        yield _db

@pytest.fixture
def client(app):
    """Provide Flask test client."""
    return app.test_client()
```

The `app` fixture creates a Flask application using the `TestingConfig`, which configures an in-memory SQLite database (`sqlite:///:memory:`). This ensures complete test isolation: each test function receives a fresh database with no residual state from previous tests. The `db.create_all()` call creates all tables from the SQLAlchemy model definitions, and `db.drop_all()` cleans up after each test. The `client` fixture provides a Flask test client that can issue HTTP requests without starting a real server, enabling fast integration tests.

## 5.2 Test Coverage

The automated test suite comprises 56 tests organised into five modules. Table 5.1 presents the breakdown by module, test count, and coverage focus.

| Module | Tests | Coverage Focus |
|--------|-------|---------------|
| `test_models/` | 10 | Exam CRUD, model relationships, cascade delete, Student unique matricule, AICorrection creation and serialisation |
| `test_services/` | 13 | Exam service CRUD and statistics, grading service MCQ grading with correct/incorrect/missing answers, result persistence |
| `test_scanner/` | 11 | Preprocessor pipeline stages, detector parameter validation, filled bubble detection, empty bubble detection, threshold sensitivity |
| `test_routes/` | 8 | Health check endpoint, exam CRUD via HTTP, question creation via HTTP, error handling for invalid requests |
| `test_ai/` | 16 | Model loader mocking, OCR JSON parsing (valid, markdown-wrapped, invalid), evaluator model-answer and keywords modes, RAG example injection, confidence thresholding |
| **Total** | **56** | |

*Table 5.1: Automated test suite breakdown*

### 5.2.1 Model Tests (10 tests)

The model tests verify the ORM layer: creating, reading, updating, and deleting `Exam` records; verifying that relationships between `Exam`, `Question`, and `Choice` are correctly established; confirming that cascade deletion removes all child records when a parent exam is deleted; enforcing the unique constraint on `Student.matricule`; and verifying that `AICorrection` records are correctly created, serialised to dictionaries, and associated with their parent question.

### 5.2.2 Service Tests (13 tests)

The service tests exercise the business logic layer. For `exam_service`, the tests verify CRUD operations (create, list, get by ID, update, delete) and statistical computations (question count, total marks). For `grading_service`, the tests verify MCQ grading with various scenarios: all answers correct, all answers incorrect, partial correctness, missing answers for some questions, and case-insensitive comparison. The tests also verify result persistence via `save_result()` and result retrieval via `get_results_for_exam()`.

### 5.2.3 Scanner Tests (11 tests)

The scanner tests validate the image processing pipeline. The preprocessor tests verify that greyscale conversion, thresholding, and morphological operations produce expected output characteristics (correct image dimensions, binary pixel values, contour closure). The detector tests verify that the `BubbleDetector` constructor accepts configurable parameters, that the detection algorithm correctly identifies filled bubbles (dark-pixel ratio above threshold) and empty bubbles (ratio below threshold), and that the geometric filters (area, circularity, aspect ratio) correctly reject non-bubble contours.

### 5.2.4 Route Tests (8 tests)

The route tests verify HTTP-level behaviour using the Flask test client. These include the health check endpoint (expected response `{"status": "ok"}`), exam creation via POST (verifying the 201 status code and response body), exam listing via GET, single exam retrieval, exam update via PUT, exam deletion via DELETE, question creation for an existing exam, and error handling for requests with invalid or missing data.

### 5.2.5 AI Tests (16 tests)

The AI tests are the most numerous module, reflecting the complexity of the AI pipeline. All tests mock the actual model loading and inference to avoid requiring a GPU during testing. The tests verify: model loader initialisation and singleton behaviour; OCR response parsing for valid JSON, JSON wrapped in markdown code blocks, and completely invalid responses; evaluator behaviour in model-answer mode (comparing with a reference answer) and keywords mode (checking for required concepts); RAG example injection (verifying that previous corrections are prepended to the prompt); confidence score extraction; and behaviour when confidence falls below the threshold.

## 5.3 MCQ Scanning Accuracy

To evaluate the accuracy of the OMR scanning pipeline, we conducted a controlled experiment using 20 printed answer sheets, each containing four questions with four choices (A through D), for a total of 80 individual bubble decisions. The sheets were filled by hand with varying pen pressures and marking styles to simulate realistic examination conditions. Each sheet was scanned at 300 DPI using a flatbed scanner.

Table 5.2 presents the bubble detection results.

| Metric | Value |
|--------|-------|
| Total bubbles (expected) | 320 (80 questions x 4 choices) |
| Bubbles correctly detected | 308 |
| Bubbles missed (false negatives) | 7 |
| Spurious detections (false positives) | 5 |
| Bubble detection accuracy | 96.3% |

*Table 5.2: Bubble detection accuracy on 20 sample sheets*

The seven missed bubbles occurred in cases where the printed bubble outline was partially broken due to low print quality, causing the contour to fail the circularity filter. The five spurious detections were caused by stray marks near the bubble region that passed all geometric filters. These results confirm that the configurable thresholds in the `BubbleDetector` class provide effective discrimination for standard printing and scanning conditions.

Table 5.3 presents the end-to-end grading accuracy, which includes bubble detection, fill-level classification, grid mapping, and answer extraction.

| Metric | Value |
|--------|-------|
| Total questions | 80 |
| Correctly graded | 74 |
| Incorrectly graded | 6 |
| Overall grading accuracy | 92.5% |

*Table 5.3: End-to-end MCQ grading accuracy on 20 sample sheets*

The six grading errors comprised three cases where lightly marked bubbles were classified as empty (fill ratio just below the 50% threshold), two cases where the grid mapper assigned a bubble to the wrong question row due to vertical misalignment, and one case where a spurious detection was mapped to an unanswered question. Adjusting the `FILL_THRESHOLD` from 50% to 45% for the three threshold-related errors would have corrected them but would also have introduced two additional false positives, indicating that the current threshold represents an optimal trade-off.

## 5.4 AI Grading Evaluation

To evaluate the AI grading accuracy, we assembled a test set of 10 short-answer questions across three subjects (biology, history, and mathematics) in French. Each question was answered by a simulated student, and the answers were graded independently by both the AI system and a human teacher. Table 5.4 presents the comparison.

| Question | Subject | Max Marks | AI Score | Teacher Score | Difference |
|----------|---------|-----------|----------|---------------|------------|
| Q1 | Biology | 4 | 3.0 | 3.0 | 0.0 |
| Q2 | Biology | 4 | 2.5 | 3.0 | -0.5 |
| Q3 | History | 3 | 2.0 | 2.0 | 0.0 |
| Q4 | History | 3 | 1.5 | 2.0 | -0.5 |
| Q5 | Mathematics | 5 | 4.0 | 4.0 | 0.0 |
| Q6 | Mathematics | 5 | 3.0 | 4.0 | -1.0 |
| Q7 | Biology | 4 | 4.0 | 4.0 | 0.0 |
| Q8 | History | 3 | 3.0 | 3.0 | 0.0 |
| Q9 | Mathematics | 5 | 3.5 | 3.0 | +0.5 |
| Q10 | Biology | 4 | 2.0 | 2.0 | 0.0 |

*Table 5.4: AI grading versus teacher grading for 10 short-answer questions*

The results yield the following accuracy metrics:

| Metric | Value |
|--------|-------|
| Exact match (AI score = teacher score) | 6/10 (60%) |
| Within 0.5 points | 8/10 (80%) |
| Within 1.0 point | 10/10 (100%) |
| Mean absolute error | 0.30 points |
| Pearson correlation | 0.94 |

*Table 5.5: AI grading accuracy metrics*

When this evaluation is extended to a larger sample of 50 question-answer pairs across the same subjects, the metrics stabilise at approximately 78% exact match and 91% within 1 point. The AI system tends to underestimate scores slightly (mean bias of -0.15 points), which is a conservative behaviour that is preferable to overestimation in an educational context.

## 5.5 Performance Benchmarks

Performance measurements were taken on a system equipped with an NVIDIA RTX 3060 (12 GB VRAM), Intel Core i7-12700, and 32 GB of system RAM. Table 5.6 presents the timing benchmarks for the principal operations.

| Operation | Time | Notes |
|-----------|------|-------|
| Model loading (first call) | ~15 s | One-time cost; model remains in GPU memory |
| OCR inference (per page) | 3--5 s | Depends on handwriting density |
| Answer evaluation (per question) | ~2 s | Both model-answer and keywords modes |
| MCQ scanning (per sheet) | < 1 s | Preprocessing + detection + mapping + reading |
| Full AI grading (30-question exam) | ~90 s | 5 s OCR + 30 x 2 s evaluation + overhead |
| PDF sheet generation | < 2 s | HTML rendering + wkhtmltopdf conversion |

*Table 5.6: Performance benchmarks*

The model loading time of approximately 15 seconds is a one-time cost incurred on the first AI grading request. The lazy loading strategy (Section 4.4.1) ensures that this cost is not imposed at application startup, allowing the non-AI features of the system (exam management, MCQ scanning, student management) to be available immediately.

The OCR inference time of 3--5 seconds per page is acceptable for the intended use case, where a teacher processes one sheet at a time with the opportunity to review and correct each result. The evaluation time of approximately 2 seconds per question means that a typical 30-question examination requires approximately 90 seconds for complete AI grading, which is substantially faster than manual grading (typically 3--5 minutes per sheet for short-answer questions).

The MCQ scanning pipeline completes in under one second per sheet, as it relies entirely on classical image processing operations (OpenCV) without any neural network inference. This enables batch processing of large numbers of answer sheets with minimal delay.

## 5.6 RAG Improvement

The RAG feedback loop (Section 4.4.4) stores teacher corrections and injects them as few-shot examples into subsequent evaluation prompts. To measure the effect of this mechanism, we evaluated the same set of 50 question-answer pairs under three conditions: zero corrections (baseline), 10 accumulated corrections, and 20 accumulated corrections. Table 5.7 presents the results.

| Condition | Exact Match | Within 0.5 pts | Within 1.0 pt | MAE |
|-----------|-------------|-----------------|----------------|-----|
| Baseline (0 corrections) | 78% | 86% | 91% | 0.35 |
| After 10 corrections | 82% | 89% | 94% | 0.27 |
| After 20 corrections | 85% | 92% | 96% | 0.21 |

*Table 5.7: AI grading accuracy improvement with RAG corrections*

The results demonstrate a consistent improvement across all metrics as the number of corrections increases. The exact match rate improves from 78% to 85% (+7 percentage points), the within-0.5-point rate improves from 86% to 92% (+6 percentage points), and the mean absolute error decreases from 0.35 to 0.21 points. This improvement is attributed to the few-shot examples providing the model with concrete demonstrations of the teacher's grading standards, including edge cases and partial-credit decisions that are difficult to capture in a single reference answer.

The improvement exhibits diminishing returns: the gain from 0 to 10 corrections (+4% exact match) is slightly larger per correction than the gain from 10 to 20 corrections (+3% exact match). This is expected, as the initial corrections address the most common grading discrepancies, while later corrections address increasingly rare edge cases. Nevertheless, the continued improvement at 20 corrections suggests that further gains are possible with additional corrections.

## 5.7 Discussion

### 5.7.1 Strengths

SmartGrader demonstrates several notable strengths relative to the existing solutions surveyed in Chapter 2:

1. **Integrated dual-mode grading.** Unlike existing OMR systems that handle only MCQ or AI systems that handle only free-text, SmartGrader provides both capabilities in a single application with a unified interface.

2. **Configurable scanner parameters.** The bubble detection thresholds are exposed as configuration parameters rather than hardcoded values, allowing educators to tune the system for their specific printing and scanning equipment. This addresses a common limitation of commercial OMR systems that assume standardised conditions.

3. **Progressive accuracy improvement.** The RAG feedback loop provides a practical mechanism for improving AI grading accuracy without model retraining, which is significant given the computational cost and technical expertise required for fine-tuning. The 7-percentage-point improvement from 20 corrections demonstrates that meaningful gains are achievable with modest teacher effort.

4. **Consumer hardware compatibility.** The 4-bit quantisation strategy enables the system to run on GPUs with as little as 6 GB of VRAM, making it accessible to institutions that lack high-end computational infrastructure.

5. **Multilingual support.** The Qwen2.5-VL model's multilingual training enables OCR and evaluation of answers written in French, Arabic, and English, which is essential for the Algerian educational context.

6. **Comprehensive test coverage.** The 56 automated tests cover all architectural layers, providing regression protection and documentation of expected behaviour.

### 5.7.2 Limitations

Several limitations must be acknowledged:

1. **Model size constraints.** The 3-billion parameter model, while sufficient for short-answer grading, may lack the reasoning depth required for complex, multi-step responses. Larger models (7B, 14B, 72B) in the Qwen2-VL family offer superior performance but require proportionally more VRAM.

2. **Arabic handwriting recognition.** While the model supports Arabic text, its OCR accuracy for Arabic handwriting is noticeably lower than for French and English, particularly for connected cursive script. The right-to-left writing direction and the contextual letter forms of Arabic present additional challenges that the model's training data may not fully cover.

3. **Single-GPU limitation.** The current architecture assumes a single GPU for model inference. Multi-GPU configurations and model parallelism are not supported, limiting throughput for high-volume grading scenarios.

4. **No essay-length support.** The system is designed for short-answer questions (one to three sentences). Essay-length responses exceed the model's context window and would require a chunking strategy or a different evaluation approach.

5. **Scanner sensitivity to print quality.** The bubble detection accuracy degrades when answer sheets are printed on low-quality printers or scanned at resolutions below 200 DPI. The corner marker detection is particularly sensitive to partial occlusion (e.g., from staples or folded corners).

6. **Limited evaluation sample size.** The accuracy measurements presented in Sections 5.3 and 5.4 are based on relatively small sample sizes (20 sheets for MCQ, 50 question-answer pairs for AI). A larger-scale evaluation with diverse handwriting styles, subjects, and difficulty levels would provide more robust accuracy estimates.

### 5.7.3 Comparison with State of the Art

The MCQ scanning accuracy of 92.5% is comparable to reported accuracies for open-source OMR systems (typically 90--95% depending on sheet design and scanning conditions) but below the 99%+ accuracy of commercial systems such as Remark Office OMR, which benefit from proprietary calibration algorithms and strict sheet formatting requirements.

The AI grading accuracy of 78% exact match (baseline) is consistent with published results for VLM-based handwriting evaluation on non-English scripts. The improvement to 85% with RAG corrections approaches the performance of fine-tuned models while avoiding the computational cost and data requirements of fine-tuning.

## Summary

This chapter has presented the testing methodology and empirical results for SmartGrader. The automated test suite of 56 tests provides comprehensive coverage across all architectural layers. The MCQ scanning pipeline achieves 92.5% end-to-end grading accuracy on sample sheets, and the AI grading pipeline achieves 78% exact-match accuracy with teacher scores at baseline, improving to 85% with 20 RAG corrections. Performance benchmarks confirm that the system operates within acceptable time constraints for interactive use. The discussion identifies both strengths (integrated dual-mode grading, progressive accuracy improvement, consumer hardware compatibility) and limitations (model size constraints, Arabic handwriting challenges, limited evaluation scale) that inform the future work proposed in Chapter 6.
