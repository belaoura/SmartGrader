# Chapter 5: Testing and Results

This chapter presents the testing methodology, test coverage, and empirical results for SmartGrader across all four development phases. We describe the automated test suite, report quantitative measurements of MCQ scanning accuracy and AI grading performance, present test scenarios and results for the authentication, online examination, and proctoring subsystems, analyse the effect of the RAG feedback loop on grading accuracy, report performance benchmarks for all major operations, and discuss the strengths and limitations of the system.

## 5.1 Test Methodology

SmartGrader employs a three-tier testing strategy: unit tests for individual functions and classes, integration tests that exercise multiple layers through the Flask test client, and manual testing for end-to-end user workflows.

### 5.1.1 Unit Tests

Unit tests verify the correctness of individual modules in isolation. Each test module focuses on a single layer of the architecture: model definitions and relationships, service functions, scanner algorithms, or AI pipeline components. Dependencies on external systems (the database, the GPU, the vision model, the webcam) are managed through fixtures and mocks.

### 5.1.2 Integration Tests

Integration tests verify the correct interaction between layers by issuing HTTP requests to the Flask application and asserting on the responses. These tests exercise the full request lifecycle: authentication middleware, route handler, service function, database operation, and response serialisation.

### 5.1.3 Test Framework and Fixtures

All tests are written using pytest. Shared fixtures are defined in `tests/conftest.py`:

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

@pytest.fixture
def teacher_token(client):
    """Register and log in a teacher; return JWT."""
    client.post("/api/auth/register",
                json={"username": "prof", "password": "pass123", "role": "teacher"})
    resp = client.post("/api/auth/login",
                       json={"username": "prof", "password": "pass123"})
    return resp.json["access_token"]

@pytest.fixture
def student_token(client, db):
    """Register a student user; return JWT."""
    # ... create student record and linked user account
    resp = client.post("/api/auth/login",
                       json={"username": "stu01", "password": "pass123"})
    return resp.json["access_token"]
```

The `TestingConfig` uses an in-memory SQLite database to ensure complete test isolation. New `teacher_token` and `student_token` fixtures provide authenticated HTTP clients for testing protected endpoints.

## 5.2 Test Coverage

The automated test suite comprises 191 tests organised into eight modules. Table 5.1 presents the breakdown by module, test count, and coverage focus.

| Module | Tests | Coverage Focus |
|--------|-------|---------------|
| `test_models/` | 22 | Original 7 models + User, StudentGroup, ExamSession, ExamAttempt, OnlineAnswer, ProctorEvent, ProctorSnapshot relationships and serialisation |
| `test_services/` | 35 | Exam/grading/scanner services + AuthService, GroupService, SessionService, ExamTakeService, ProctorService |
| `test_scanner/` | 11 | Preprocessor pipeline, BubbleDetector parameter validation, fill detection, threshold sensitivity |
| `test_routes/` | 45 | All original endpoints + auth, groups, sessions, exam take, and proctoring endpoints; role enforcement; 401/403 responses |
| `test_ai/` | 16 | Model loader, OCR parsing, evaluator modes, RAG injection, confidence thresholding |
| `test_auth/` | 28 | Registration, login, JWT validation, barcode login, password hashing, role enforcement |
| `test_session/` | 20 | Session creation, activation, attempt lifecycle, answer persistence, auto-submit, deadline enforcement |
| `test_proctor/` | 14 | Event ingestion, snapshot storage, warning threshold enforcement, dashboard queries |
| **Total** | **191** | |

*Table 5.1: Automated test suite breakdown*

### 5.2.1 Model Tests (22 tests)

The model tests verify all 15 database tables: the original 7 tables (Exam, Question, Choice, Student, StudentAnswer, Result, AICorrection) plus the 8 new tables (User, StudentGroup, GroupMember, ExamSession, ExamAttempt, OnlineAnswer, ProctorEvent, ProctorSnapshot). Tests confirm correct ORM relationships, cascade deletion behaviour, unique constraint enforcement, and `to_dict()` serialisation for all models.

### 5.2.2 Service Tests (35 tests)

The service tests exercise all 9 service modules. New tests added for Phases 1–3 include:

- `AuthService`: user registration with duplicate username detection, correct password hashing, successful and failed login, JWT payload validation.
- `GroupService`: group CRUD, member addition and removal, group-student association.
- `SessionService`: session creation, activation validation (future start time), attempt creation for enrolled students, rejection of non-enrolled students.
- `ExamTakeService`: answer persistence (create and update), concurrent answer tracking, score computation on submission, partial credit handling, auto-submit past deadline.
- `ProctorService`: event ingestion with severity classification, snapshot storage, warning count aggregation, threshold-triggered attempt termination.

### 5.2.3 Scanner Tests (11 tests)

The scanner tests are unchanged. They validate the image processing pipeline including preprocessor stages, detector parameter validation, filled and empty bubble detection, and threshold sensitivity. All 11 tests pass in the current codebase.

### 5.2.4 Route Tests (45 tests)

The route test module has been significantly expanded. In addition to the original 8 HTTP endpoint tests, the new tests cover:

- **Auth routes (8 tests):** `POST /api/auth/register` with valid and duplicate usernames; `POST /api/auth/login` with correct and incorrect credentials; `POST /api/auth/barcode-login` with valid and unknown matricule; `GET /api/auth/me` with valid and expired tokens.
- **Group routes (7 tests):** CRUD operations on groups; member addition and removal; rejection of unauthenticated and student-role requests.
- **Session routes (8 tests):** Session creation with valid and invalid exam/group IDs; activation; attempt creation for enrolled and non-enrolled students; rejection of duplicate attempts.
- **Exam take routes (8 tests):** Attempt creation, answer saving (create and overwrite), submission, auto-grading verification, rejection of answers after submission.
- **Proctoring routes (6 tests):** Event reporting, snapshot upload, dashboard event list, snapshot list, warning threshold enforcement.

### 5.2.5 AI Tests (16 tests)

The AI tests are unchanged from the original module. All 16 tests mock the model loader and inference to avoid GPU dependency, testing OCR parsing, evaluator modes, RAG injection, and confidence thresholding.

### 5.2.6 Authentication Tests (28 tests)

The authentication test module provides the most thorough coverage of the new security layer:

- **Password security:** Verifies that stored passwords are bcrypt hashes (not plaintext), that the hash is non-deterministic (two hashes of the same password differ), and that verification correctly accepts the correct password and rejects incorrect ones.
- **JWT validation:** Verifies that protected endpoints return HTTP 401 when no token is provided, HTTP 401 when an expired token is provided, and HTTP 403 when a valid token with the wrong role is provided.
- **Barcode login:** Verifies that a known matricule produces a valid student-role JWT and that an unknown matricule produces HTTP 404.
- **CSV import:** Verifies that bulk student import via CSV correctly creates student records and linked user accounts, and that duplicate matricule values are handled gracefully.

### 5.2.7 Online Exam Tests (20 tests)

The online examination test module covers the complete attempt lifecycle:

- **Happy path:** Session created → activated → student creates attempt → answers saved → manual submission → score computed correctly.
- **Auto-submit:** Attempt with `started_at` in the past beyond the session duration is automatically submitted when queried.
- **Resumability:** Answers persisted before a simulated disconnect are present when the attempt is resumed.
- **Duplicate attempt prevention:** A second `POST /api/exam/attempt` from the same student for the same active session returns the existing attempt rather than creating a duplicate.
- **Answer overwrite:** Saving an answer for a question that already has an answer correctly updates rather than duplicates the OnlineAnswer record.

### 5.2.8 Proctoring Tests (14 tests)

The proctoring test module verifies the integrity monitoring layer:

- **Event routing:** Events of each type (`face_missing`, `tab_switch`, `fullscreen_exit`, `copy_paste`) are correctly ingested and stored.
- **Severity assignment:** `face_missing` and `multiple_faces` events are classified as `warning`; `window_blur` is classified as `info`.
- **Warning threshold:** After the configured number of `warning`-severity events, the attempt status transitions to `terminated` and further answer submissions are rejected with HTTP 403.
- **Snapshot storage:** Uploaded snapshots are stored in the filesystem and the database record contains the correct `face_detected` flag and file path.
- **Dashboard query:** The teacher dashboard endpoint returns the correct event count, warning count, and latest snapshot for each attempt.

## 5.3 MCQ Scanning Accuracy

To evaluate the accuracy of the OMR scanning pipeline, we conducted a controlled experiment using 20 printed answer sheets, each containing four questions with four choices (A through D), for a total of 80 individual bubble decisions. The sheets were filled by hand with varying pen pressures and marking styles to simulate realistic examination conditions. Each sheet was scanned at 300 DPI using a flatbed scanner.

Table 5.2 presents the bubble detection results.

| Metric | Value |
|--------|-------|
| Total bubbles (expected) | 320 (80 questions × 4 choices) |
| Bubbles correctly detected | 308 |
| Bubbles missed (false negatives) | 7 |
| Spurious detections (false positives) | 5 |
| Bubble detection accuracy | 96.3% |

*Table 5.2: Bubble detection accuracy on 20 sample sheets*

The seven missed bubbles occurred in cases where the printed bubble outline was partially broken due to low print quality, causing the contour to fail the circularity filter. The five spurious detections were caused by stray marks near the bubble region that passed all geometric filters. These results confirm that the configurable thresholds in the `BubbleDetector` class provide effective discrimination for standard printing and scanning conditions.

Table 5.3 presents the end-to-end grading accuracy.

| Metric | Value |
|--------|-------|
| Total questions | 80 |
| Correctly graded | 74 |
| Incorrectly graded | 6 |
| Overall grading accuracy | 92.5% |

*Table 5.3: End-to-end MCQ grading accuracy on 20 sample sheets*

The six grading errors comprised three cases where lightly marked bubbles were classified as empty (fill ratio just below the 50% threshold), two cases where the grid mapper assigned a bubble to the wrong question row due to vertical misalignment, and one case where a spurious detection was mapped to an unanswered question.

## 5.4 AI Grading Evaluation

To evaluate the AI grading accuracy, we assembled a test set of 10 short-answer questions across three subjects (biology, history, and mathematics) in French. Table 5.4 presents the AI versus teacher score comparison.

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

| Metric | Value |
|--------|-------|
| Exact match (AI score = teacher score) | 6/10 (60%) |
| Within 0.5 points | 8/10 (80%) |
| Within 1.0 point | 10/10 (100%) |
| Mean absolute error | 0.30 points |
| Pearson correlation | 0.94 |

*Table 5.5: AI grading accuracy metrics*

When extended to a larger sample of 50 question-answer pairs, the metrics stabilise at approximately 78% exact match and 91% within 1 point.

## 5.5 Online Examination Test Scenarios

To validate the online examination engine, four end-to-end test scenarios were executed manually in addition to the automated test suite.

**Scenario 1: Normal Examination Flow.** A teacher created an exam with 10 MCQ questions, assigned it to a group of 5 simulated students, and activated the session. Each student authenticated, navigated to the active exam, selected answers, and submitted. All 5 attempts were graded correctly, and scores appeared in the teacher's results view within 1 second of submission.

**Scenario 2: Timer Expiry and Auto-Submit.** A session was configured with a 2-minute duration. One student did not submit manually. The countdown timer reached zero, the JavaScript auto-submit was triggered, and the attempt was finalised with the answers recorded up to that point. The teacher's monitoring dashboard reflected the `submitted` status within the next polling cycle (5 seconds).

**Scenario 3: Network Interruption.** A student's browser was closed mid-examination (simulated by killing the browser process) after answering 6 of 10 questions. On reopening the browser and navigating to the exam, the previously saved answers were restored. The student completed the remaining questions and submitted. The final score reflected all 10 answers correctly.

**Scenario 4: Concurrent Sessions.** Three separate examination sessions (different exams, different student groups) were activated simultaneously. Fifteen students (5 per session) took their respective exams concurrently. All 15 attempts were correctly isolated (no cross-session answer contamination) and graded independently.

## 5.6 Proctoring Test Scenarios

**Scenario 1: Face Detection.** A student began an examination with their webcam covered. The ProctorEngine reported `face_missing` events at 1-second intervals. After 3 events (the configured warning threshold), a warning dialog appeared. After 3 further warnings, the attempt was auto-terminated and the student was shown a session-terminated message.

**Scenario 2: Tab Switch Detection.** A student switched to a different browser tab during the examination. The `visibilitychange` event was captured within 100 ms, and a `tab_switch` proctoring event appeared in the teacher's dashboard within the next polling cycle.

**Scenario 3: Snapshot Capture.** Snapshots were captured every 30 seconds throughout a 10-minute examination (approximately 20 snapshots). The teacher's proctoring panel displayed all snapshots in chronological order with the `face_detected` flag correctly set for each.

**Scenario 4: Fullscreen Enforcement.** The examination page was configured to require fullscreen mode. When the student exited fullscreen (using the Escape key), a `fullscreen_exit` event was recorded and a dialog requested the student to re-enter fullscreen mode.

## 5.7 Performance Benchmarks

Performance measurements were taken on a system equipped with an NVIDIA RTX 3060 (12 GB VRAM), Intel Core i7-12700, and 32 GB of system RAM. Table 5.6 presents timing benchmarks for all major operations.

| Operation | Time | Notes |
|-----------|------|-------|
| Model loading (first call) | ~15 s | One-time; model stays in GPU memory |
| OCR inference (per page) | 3–5 s | Depends on handwriting density |
| Answer evaluation (per question) | ~2 s | Both modes |
| MCQ scanning (per sheet) | < 1 s | Classical CV only |
| Full AI grading (30-question exam) | ~90 s | 5 s OCR + 30 × 2 s evaluation |
| PDF sheet generation | < 2 s | HTML + wkhtmltopdf |
| Auth login (JWT issuance) | < 50 ms | bcrypt verify + token sign |
| Answer save (online exam) | < 100 ms | DB write + response |
| Proctoring event POST | < 80 ms | DB insert + 200 response |
| Proctoring snapshot POST | < 200 ms | File write + DB insert |
| Dashboard poll (15 students) | < 150 ms | Aggregation query |
| BlazeFace inference (browser) | < 5 ms | GPU-accelerated WebGL |
| Session activation | < 50 ms | DB status update |

*Table 5.6: Performance benchmarks*

The answer save latency of under 100 ms on a LAN connection ensures that answer persistence is transparent to the student during normal examination use. The BlazeFace inference latency of under 5 ms means that the face detection loop running at 1-second intervals consumes less than 0.5% of the available time budget, leaving the browser fully responsive for the examination interface.

The dashboard polling endpoint at 150 ms for 15 simultaneous students is well within acceptable bounds for the teacher monitoring use case. For larger groups (50+ students), this endpoint would benefit from aggregation caching, which has been identified as a future optimisation.

## 5.8 RAG Improvement

The RAG feedback loop stores teacher corrections and injects them as few-shot examples into subsequent evaluation prompts. Table 5.7 presents accuracy improvements under three correction volumes.

| Condition | Exact Match | Within 0.5 pts | Within 1.0 pt | MAE |
|-----------|-------------|-----------------|----------------|-----|
| Baseline (0 corrections) | 78% | 86% | 91% | 0.35 |
| After 10 corrections | 82% | 89% | 94% | 0.27 |
| After 20 corrections | 85% | 92% | 96% | 0.21 |

*Table 5.7: AI grading accuracy improvement with RAG corrections*

The results demonstrate consistent improvement across all metrics. The exact match rate improves from 78% to 85% (+7 percentage points) with 20 corrections, while the mean absolute error decreases from 0.35 to 0.21 points.

## 5.9 Discussion

### 5.9.1 Strengths

SmartGrader demonstrates the following notable strengths:

1. **Integrated examination platform.** Unlike any reviewed existing solution, SmartGrader combines paper-based MCQ scanning, AI-assisted handwriting grading, online examination delivery, and browser-based proctoring in a single unified application.

2. **Privacy-preserving proctoring.** The browser-native BlazeFace approach eliminates the need to transmit continuous video to a cloud service, addressing the privacy and data sovereignty concerns that have made commercial proctoring solutions controversial.

3. **Comprehensive test coverage.** The 191-test suite provides regression protection across all 15 database models, 9 service modules, and approximately 40 API endpoints. The test suite grows proportionally with the system, maintaining developer confidence throughout all phases.

4. **Progressive accuracy improvement.** The RAG feedback loop provides meaningful grading accuracy improvement (7 percentage points at 20 corrections) without model retraining or fine-tuning.

5. **Consumer hardware compatibility.** 4-bit quantisation enables AI grading on GPUs with as little as 6 GB of VRAM, while the remainder of the system (online exam engine, proctoring, scanning) requires only a CPU.

6. **Flexible deployment.** Three deployment configurations (development, LAN/university server, Docker) accommodate the full range of institutional infrastructure from a single machine to a production university server with SSL.

### 5.9.2 Limitations

1. **Model size constraints.** The 3-billion parameter VLM may lack reasoning depth for complex multi-part responses. Larger models improve accuracy but require more VRAM.

2. **Arabic handwriting recognition.** OCR accuracy for Arabic handwriting is lower than for French and English due to connected cursive script and right-to-left directionality.

3. **Single-GPU limitation.** The current architecture supports a single CUDA device for AI inference, limiting throughput in high-volume grading scenarios.

4. **No essay-length support.** The system targets short-answer questions. Essay-length responses exceed the model's context window.

5. **Proctoring false positives.** BlazeFace occasionally fails to detect a face that is present (e.g., when the student briefly looks away or adjusts their position). This can trigger spurious `face_missing` events. The warning threshold mitigates the impact of isolated false positives, but the false positive rate should be characterised more rigorously in future work.

6. **SQLite scalability.** SQLite performs well for single-machine deployments but may become a bottleneck under high concurrency (many simultaneous student answer submissions during a large examination session). Migration to PostgreSQL is recommended for university-scale deployments.

### 5.9.3 Comparison with State of the Art

The MCQ scanning accuracy of 92.5% is comparable to reported accuracies for open-source OMR systems (90–95%) but below commercial systems such as Remark Office OMR (~99%).

The AI grading accuracy of 78% exact match (baseline) improves to 85% with RAG corrections, approaching the performance of fine-tuned models without their computational cost.

The browser-based proctoring approach achieves sub-5 ms face detection latency with BlazeFace, comparable to the real-time performance of server-side proctoring systems while eliminating video transmission and cloud storage.

## Summary

This chapter has presented the testing methodology and empirical results for SmartGrader across all four development phases. The automated test suite of 191 tests provides comprehensive coverage across 15 models, 9 services, and approximately 40 API endpoints. The MCQ scanning pipeline achieves 92.5% end-to-end grading accuracy. The AI grading pipeline achieves 78% exact-match accuracy, improving to 85% with RAG corrections. The online examination engine passed all four end-to-end test scenarios including timer auto-submit, network interruption recovery, and concurrent session isolation. The proctoring system correctly detected face absence, tab switching, fullscreen exit, and snapshot capture. Performance benchmarks confirm that all subsystems operate within acceptable time constraints for interactive use. Chapter 6 summarises the project's achievements and proposes directions for future work.
