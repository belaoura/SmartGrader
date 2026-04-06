# Chapter 4: Implementation

This chapter presents the implementation of SmartGrader, detailing the development environment, project structure, backend services, AI integration, and frontend application. The discussion follows the layered architecture established in Chapter 3 and draws upon the actual source code to illustrate key design decisions and algorithmic choices.

## 4.1 Development Environment

SmartGrader is developed using a modern technology stack that spans backend processing, computer vision, artificial intelligence, and frontend user interfaces. Table 4.1 enumerates the principal technologies and their roles within the system.

| Technology | Version | Role |
|------------|---------|------|
| Python | 3.10 | Backend programming language |
| Flask | 3.1 | Lightweight web framework and REST API server |
| SQLAlchemy | 2.0 | Object-relational mapper for database access |
| Flask-Migrate | - | Alembic-based database migration management |
| OpenCV | 4.11 | Computer vision library for image processing |
| NumPy | - | Numerical computation for array operations |
| PyTorch | 2.x | Deep learning framework (GPU inference) |
| Transformers | - | Hugging Face library for model loading and inference |
| BitsAndBytes | - | 4-bit quantisation for reduced VRAM usage |
| Qwen2.5-VL-3B-Instruct | 3B params | Vision-language model for OCR and grading |
| React | 18 | Frontend user interface library |
| Vite | 5.x | Frontend build tool and development server |
| Tailwind CSS | 4.0 | Utility-first CSS framework |
| shadcn/ui | - | Accessible component library built on Radix UI |
| TanStack Query | 5.x | Server state management for React |
| Recharts | - | Charting library for dashboard visualisations |
| pytest | - | Python testing framework |
| wkhtmltopdf | - | PDF generation from HTML templates |

*Table 4.1: Technology stack for SmartGrader*

The development machine requires a CUDA-compatible GPU with at least 6 GB of VRAM to run the Qwen2.5-VL-3B model under 4-bit quantisation. Development was conducted on an NVIDIA RTX-series GPU with CUDA 12.x drivers. The backend runs on Python 3.10 to ensure compatibility with all dependencies, while the frontend is built with Node.js 18+ for the Vite development server and production build pipeline.

Version control is managed with Git, and the project follows a monorepo structure with the Flask backend and React frontend co-located in a single repository. Environment configuration is centralised in a single `config.py` module that supports development, testing, and production profiles selectable via the `FLASK_ENV` environment variable.

## 4.2 Project Structure

The SmartGrader codebase is organised into clearly separated directories that reflect the layered architecture described in Chapter 3. The following listing presents the top-level structure:

```
app/                          # Flask backend application
  __init__.py                 # Application factory (create_app)
  config.py                   # Centralised configuration (Config, DevelopmentConfig,
                              #   TestingConfig, ProductionConfig)
  errors.py                   # Custom exception hierarchy
  logging_config.py           # Structured logging setup
  models/                     # SQLAlchemy ORM models
    exam.py                   #   Exam, Question, Choice
    student.py                #   Student, StudentAnswer
    result.py                 #   Result
    ai_correction.py          #   AICorrection (RAG feedback)
  services/                   # Business logic layer
    exam_service.py           #   Exam CRUD operations and statistics
    grading_service.py        #   MCQ grading and result persistence
    scanner_service.py        #   Orchestrates the scanner pipeline
    ai_service.py             #   Orchestrates the AI pipeline
  scanner/                    # Image processing pipeline
    preprocessor.py           #   Greyscale, thresholding, morphology
    marker_finder.py          #   Corner marker detection
    detector.py               #   Bubble detection (BubbleDetector)
    grid_mapper.py            #   Spatial mapping of bubbles to questions
    answer_reader.py          #   Fill-level analysis and answer extraction
  ai/                         # Vision-language model integration
    model_loader.py           #   Lazy singleton model loader (4-bit)
    ocr_pipeline.py           #   Handwritten text extraction
    answer_evaluator.py       #   AI-based answer scoring
    prompt_templates.py       #   Prompt strings for OCR and evaluation
  routes/                     # Flask blueprints (REST API)
    exams.py                  #   /api/exams endpoints
    questions.py              #   /api/exams/<id>/questions endpoints
    students.py               #   /api/students endpoints
    scanning.py               #   /api/scan endpoints
    grading.py                #   /api/results endpoints
    ai.py                     #   /api/ai endpoints

frontend/                     # React single-page application
  src/
    components/               # Reusable UI components
      layout/                 #   Sidebar, Header, ThemeToggle
      dashboard/              #   StatCard, RecentExams, Charts
      exams/                  #   ExamForm, QuestionForm, ChoiceEditor
      scanner/                #   ScanUpload, BubblePreview, AIGrading
      students/               #   StudentTable, StudentForm
      results/                #   ResultsTable, ScoreDistribution
    pages/                    # Seven top-level pages
      Dashboard.jsx           #   Overview with statistics and charts
      Exams.jsx               #   Exam list and creation
      ExamDetail.jsx          #   Single exam with questions management
      Scanner.jsx             #   MCQ scanning and AI grading tabs
      Students.jsx            #   Student registry
      Results.jsx             #   Grading results with filtering
      Settings.jsx            #   Application settings and theme
    hooks/                    # TanStack Query custom hooks
      use-exams.js            #   Exam CRUD mutations and queries
      use-students.js         #   Student queries and mutations
      use-results.js          #   Result fetching and aggregation
      use-ai.js               #   AI status, OCR, and evaluation
      use-theme.js            #   Dark/light theme persistence

tests/                        # 56 automated pytest tests
  conftest.py                 # Shared fixtures (app, db, client)
  test_models/                # 10 model-layer tests
  test_services/              # 13 service-layer tests
  test_scanner/               # 11 scanner pipeline tests
  test_routes/                # 8 HTTP endpoint tests
  test_ai/                    # 16 AI module tests

schema.sql                    # Raw SQL schema (7 tables + indexes)
```

This structure enforces a strict separation of concerns. The `models/` directory contains only data definitions and serialisation methods. The `services/` directory encapsulates business logic that orchestrates model operations without knowledge of HTTP request handling. The `routes/` directory handles HTTP concerns exclusively -- request parsing, response formatting, and status codes -- and delegates all logic to the service layer. The `scanner/` and `ai/` directories are self-contained processing pipelines that operate independently of the web framework and can be tested in isolation.

## 4.3 Backend Implementation

### 4.3.1 Application Factory

SmartGrader employs the Flask application factory pattern, a design approach recommended by the Flask documentation for applications that require multiple configurations (development, testing, production) and clean extension initialisation. The factory function `create_app()` resides in `app/__init__.py`:

```python
def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name[config_name])

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    setup_logging(
        log_level=app.config.get("LOG_LEVEL", "INFO"),
        log_file=app.config.get("LOG_FILE"),
    )

    # Register error handlers and blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    return app
```

The factory accepts an optional `config_name` parameter, defaulting to the `FLASK_ENV` environment variable. It initialises the SQLAlchemy database, Flask-Migrate for schema migrations, and CORS for cross-origin requests from the React frontend. Error handlers are registered for both application-specific exceptions (via the `SmartGraderError` hierarchy) and standard HTTP errors. Blueprints are registered last, after all extensions are initialised, to ensure that route handlers have access to the fully configured application context.

### 4.3.2 Configuration Management

The `Config` class in `app/config.py` centralises all application parameters into a single location. This includes Flask settings (secret key, database URI), scanner thresholds (fill threshold, circle area bounds, circularity minimum), PDF generation parameters (A4 dimensions, margins, DPI), and AI model settings (model identifier, device, token limits, confidence threshold). Three subclasses -- `DevelopmentConfig`, `TestingConfig`, and `ProductionConfig` -- override specific values. Notably, `TestingConfig` uses an in-memory SQLite database (`sqlite:///:memory:`) to ensure that tests run in complete isolation:

```python
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    LOG_LEVEL = "WARNING"
```

The scanner thresholds deserve particular attention. The `FILL_THRESHOLD` parameter (default: 50) determines the percentage of dark pixels within a bubble's bounding region required to classify it as filled. The `CIRCULARITY_MIN` parameter (default: 0.65) filters out non-circular contours that could be mistaken for bubbles. These values were determined empirically through iterative testing on sample answer sheets and represent a balance between sensitivity (detecting lightly marked bubbles) and specificity (rejecting noise and stray marks).

### 4.3.3 SQLAlchemy Models

The data model comprises seven tables mapped to six Python classes (the `StudentAnswer` model shares a module with `Student`). All models inherit from `db.Model` and define their table name, column schema, and relationships explicitly.

The `Exam` model is the root entity, with one-to-many relationships to both `Question` and `Result`:

```python
class Exam(db.Model):
    __tablename__ = "exams"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100))
    date = db.Column(db.String(20))
    total_marks = db.Column(db.Float)

    questions = db.relationship(
        "Question", backref="exam",
        cascade="all, delete-orphan", lazy="dynamic"
    )
    results = db.relationship(
        "Result", backref="exam",
        cascade="all, delete-orphan", lazy="dynamic"
    )
```

The `cascade="all, delete-orphan"` parameter ensures referential integrity: when an exam is deleted, all associated questions, choices, student answers, and results are automatically removed. The `lazy="dynamic"` loading strategy returns a query object rather than a materialised list, allowing the service layer to apply additional filters (e.g., ordering, pagination) without loading the entire relationship into memory.

The `AICorrection` model supports the RAG feedback loop. Each record stores the student's text, the AI's original score and feedback, and the teacher's corrected score and feedback:

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

This table serves as the knowledge base for retrieval-augmented generation: when evaluating a new student answer, the system queries this table for previous corrections on the same question and injects them as few-shot examples into the evaluation prompt.

### 4.3.4 Service Layer Pattern

The service layer mediates between the route handlers and the data models. Each service module exposes a set of pure functions that encapsulate a complete business operation, including validation, data retrieval, computation, and persistence. This pattern decouples the HTTP layer from the business logic, facilitating unit testing (services can be tested without HTTP request context) and code reuse (the same service function can be called from routes, CLI commands, or background tasks).

The grading service illustrates this pattern. The `grade_mcq_answers()` function accepts an exam identifier and a dictionary of detected answers, retrieves the exam's questions and correct choices from the database, computes the score, and returns a structured result:

```python
def grade_mcq_answers(exam_id, detected_answers):
    exam = get_exam_by_id(exam_id)
    questions = exam.questions.order_by(Question.id).all()

    total_marks = 0
    obtained_marks = 0
    details = []

    for question in questions:
        total_marks += question.marks
        correct_choice = question.choices.filter_by(is_correct=1).first()
        correct_label = correct_choice.choice_label.upper() if correct_choice else None
        detected_label = detected_answers.get(question.id)

        if detected_label:
            detected_label = detected_label.upper()

        is_correct = (detected_label == correct_label
                      if detected_label and correct_label else False)
        if is_correct:
            obtained_marks += question.marks

        details.append({
            "question_id": question.id,
            "detected": detected_label,
            "correct": correct_label,
            "is_correct": is_correct,
            "marks": question.marks,
        })

    percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0

    return {
        "exam_id": exam_id,
        "total_marks": total_marks,
        "obtained_marks": obtained_marks,
        "percentage": round(percentage, 1),
        "answered": sum(1 for d in details if d["detected"]),
        "total_questions": len(questions),
        "details": details,
    }
```

The function iterates over each question, retrieves the correct choice via the `is_correct` flag, performs a case-insensitive comparison with the detected answer, and accumulates the score. The result dictionary includes both aggregate statistics (total marks, obtained marks, percentage) and per-question details that enable the frontend to display a detailed breakdown with colour-coded correct and incorrect answers.

### 4.3.5 Scanner Pipeline

The scanner pipeline transforms a raw scanned image of a completed MCQ answer sheet into a structured set of detected answers. The pipeline consists of five sequential stages, each implemented as a separate module within the `scanner/` package.

**Stage 1: Preprocessing (`preprocessor.py`).** The input image undergoes greyscale conversion (`cv2.cvtColor`), Gaussian blur for noise reduction (`cv2.GaussianBlur` with a 5x5 kernel), and adaptive thresholding (`cv2.adaptiveThreshold` with Gaussian weighting, block size 11, and constant 4). A morphological closing operation (`cv2.morphologyEx` with a 2x2 kernel) fills small gaps in bubble outlines that may result from printing or scanning artefacts. The result is a clean binary image where filled regions appear as white contours on a black background.

**Stage 2: Marker Detection (`marker_finder.py`).** The system locates the four corner alignment markers that were printed on the answer sheet during PDF generation. These markers serve as reference points for establishing a coordinate transformation that compensates for rotation, scaling, and translation introduced by the scanning process. The marker finder uses contour detection and geometric filtering to identify the square markers, then sorts them into top-left, top-right, bottom-left, and bottom-right positions based on their centroid coordinates.

**Stage 3: Bubble Detection (`detector.py`).** The `BubbleDetector` class identifies individual answer bubbles within the preprocessed image. The detection algorithm operates on the binary image and applies a cascade of geometric filters to the detected contours:

```python
class BubbleDetector:
    def __init__(self, area_min=60, area_max=600,
                 circularity_min=0.65, aspect_min=0.6,
                 aspect_max=1.5, radius_min=6, radius_max=25,
                 duplicate_distance=10):
        # Store configurable thresholds
        ...

    def detect(self, image, top_y, bottom_y, margin=40):
        """Detect bubbles in the region between top_y and bottom_y."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 4
        )
        kernel = np.ones((2, 2), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )
        img_width = image.shape[1]
        bubbles = self._filter_contours(
            contours, top_y, bottom_y, img_width, margin
        )
        bubbles = self._remove_duplicates(bubbles)
        bubbles = self._remove_outliers(bubbles)
        return bubbles
```

The `_filter_contours()` method applies six geometric criteria to each contour: minimum and maximum area (to exclude noise and large shapes), minimum circularity (computed as $4\pi A / P^2$ where $A$ is the contour area and $P$ is the perimeter), aspect ratio bounds (to reject elongated shapes), radius bounds, and positional constraints based on expected column positions within the image. The `_remove_duplicates()` method eliminates contours whose centroids lie within a configurable distance of each other, and `_remove_outliers()` removes detections that deviate significantly from the expected grid pattern.

**Stage 4: Grid Mapping (`grid_mapper.py`).** The detected bubbles are spatially organised into a grid structure that maps each bubble to its corresponding question number and choice label. The mapper divides the bubbles into rows (one per question) and columns (one per choice) based on their vertical and horizontal coordinates. Column boundaries are determined by the expected fractions of the image width, as defined in the configuration (`LEFT_COL_MIN`, `LEFT_COL_MAX`, `RIGHT_COL_MIN`, `RIGHT_COL_MAX`).

**Stage 5: Answer Reading (`answer_reader.py`).** For each bubble in the mapped grid, the answer reader computes the fill level by counting the number of dark pixels within the bubble's bounding region and comparing the ratio against the `FILL_THRESHOLD`. A bubble is classified as filled if its dark-pixel ratio exceeds the threshold (default: 50%). The reader then selects the filled bubble for each question row, producing a dictionary mapping question identifiers to choice labels (e.g., `{1: "A", 2: "C", 3: "B"}`).

## 4.4 AI Integration

### 4.4.1 Model Loading and Quantisation

SmartGrader employs the Qwen2.5-VL-3B-Instruct vision-language model for both optical character recognition and answer evaluation. The model is loaded using a lazy singleton pattern implemented in `model_loader.py`: the model is not loaded at application startup but rather on the first invocation of `get_model()`, after which it remains in GPU memory for subsequent requests.

To operate within the VRAM constraints of consumer-grade GPUs (6--8 GB), the model is loaded with 4-bit quantisation using the BitsAndBytes library:

```python
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
)

model = Qwen2VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2.5-VL-3B-Instruct",
    quantization_config=bnb_config,
    device_map="auto",
)
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct")
```

The `load_in_4bit=True` parameter compresses the model weights from 16-bit floating point to 4-bit integers, reducing VRAM consumption from approximately 6 GB to approximately 2.5 GB. The `bnb_4bit_compute_dtype=torch.float16` parameter specifies that intermediate computations during inference should use half-precision floating point, balancing performance and numerical stability. The `device_map="auto"` parameter allows the Transformers library to automatically distribute model layers across available GPU devices.

The `generate()` function constructs a multi-modal message containing both the image and the text prompt, processes it through the model's chat template, and decodes only the newly generated tokens (excluding the input tokens) to obtain the model's response. A GPU availability check raises a descriptive `AIModelError` if no CUDA device is detected, providing a clear message rather than a cryptic hardware error.

### 4.4.2 OCR Pipeline

The OCR stage extracts handwritten text from a scanned exam paper. Rather than processing individual question regions, SmartGrader adopts a full-page approach: the entire scanned page is submitted to the vision model along with a list of question numbers, and the model extracts all answers simultaneously. This approach leverages the model's spatial understanding to associate handwritten text with the correct question regions.

The OCR prompt template is defined in `prompt_templates.py`:

```
Look at this scanned exam paper. Students wrote their answers directly
on the paper. Extract the handwritten answer for each question listed
below. The text may be in French, Arabic, or English.

Questions to extract: {question_list}

Return ONLY valid JSON, no other text:
{"answers": [
  {"question": <number>, "text": "<extracted text>"},
  ...
]}
```

Several design decisions merit explanation. The prompt explicitly states that students wrote answers "directly on the paper" to guide the model's spatial reasoning. The multilingual instruction ("French, Arabic, or English") reflects the Algerian educational context where examinations may be conducted in any of these three languages. The strict JSON output format enables deterministic parsing of the model's response. A retry mechanism with an `OCR_RETRY_PROMPT` handles cases where the model's initial response is not valid JSON, requesting the same extraction in a simplified format.

The OCR pipeline parses the model's JSON response and returns a list of question-answer pairs. The parser handles edge cases including markdown code block wrappers (` ```json ... ``` `) that the model occasionally produces despite the "ONLY valid JSON" instruction.

### 4.4.3 Answer Evaluation

The evaluation stage scores a student's extracted answer against the teacher's grading criteria. SmartGrader supports two evaluation modes:

**Model Answer Mode.** The student's answer is compared against a reference answer (the model answer) provided by the teacher. The evaluation prompt instructs the model to grade the student's response by semantic comparison with the reference:

```
You are grading a student's answer.

Question: {question_text}
Reference answer: {model_answer}
Student's answer: {student_text}
Maximum marks: {max_marks}

Grade the student's answer by comparing it to the reference.
Return ONLY valid JSON, no other text:
{"score": <number>, "max": {max_marks}, "feedback": "<brief explanation>",
 "confidence": <0.0-1.0>}
```

**Keywords Mode.** The student's answer is evaluated against a list of required concepts (keywords) that must appear in a correct response. This mode is particularly useful for factual questions where specific terminology is expected:

```
You are grading a student's answer.

Question: {question_text}
Required concepts: {keywords_list}
Student's answer: {student_text}
Maximum marks: {max_marks}

Check which required concepts appear in the student's answer.
Return ONLY valid JSON, no other text:
{"score": <number>, "max": {max_marks}, "found_concepts": [...],
 "missing_concepts": [...], "confidence": <0.0-1.0>}
```

Both modes return a confidence score between 0.0 and 1.0. The system uses the `CONFIDENCE_THRESHOLD` configuration parameter (default: 0.7) to flag low-confidence evaluations for mandatory teacher review. This mechanism ensures that uncertain AI judgements are not silently accepted as final scores.

### 4.4.4 RAG Feedback Loop

The Retrieval-Augmented Generation (RAG) mechanism improves the AI's grading accuracy over time by learning from teacher corrections. When a teacher disagrees with the AI's score and submits a correction, the system stores the correction in the `ai_corrections` table with the student's text, the AI's original score and feedback, and the teacher's corrected score and feedback.

On subsequent evaluations of the same question, the system retrieves the most recent corrections from the database and injects them as few-shot examples into the evaluation prompt. The RAG header and example templates are:

```
Here are examples of how this question was graded previously:
- Student wrote: "{student_text}" -> Score: {teacher_score}/{max_marks}
  because: {teacher_feedback}
```

These examples precede the main evaluation instruction, providing the model with concrete demonstrations of the teacher's grading standards for that specific question. As the corpus of corrections grows, the model receives increasingly representative examples, leading to progressive improvement in grading accuracy. Section 5.6 presents empirical measurements of this improvement.

## 4.5 Frontend Implementation

### 4.5.1 Architecture

The frontend is a React 18 single-page application built with Vite as the module bundler and development server. Vite provides near-instantaneous hot module replacement during development and optimised production builds with code splitting. The styling layer combines Tailwind CSS 4.0 for utility-first responsive design with shadcn/ui for accessible, pre-styled UI components built on Radix UI primitives.

### 4.5.2 Server State Management

All communication with the Flask backend is managed through TanStack Query (React Query) custom hooks located in the `hooks/` directory. This library provides automatic caching, background refetching, optimistic updates, and request deduplication. Each hook module encapsulates the API calls for a specific domain:

- `use-exams.js`: queries for listing and fetching exams, mutations for creation, update, and deletion with automatic cache invalidation.
- `use-students.js`: queries for the student registry with search and pagination support.
- `use-results.js`: queries for exam results with filtering by exam and aggregation statistics.
- `use-ai.js`: queries for AI model status, mutations for OCR processing and answer evaluation, and correction submission.
- `use-theme.js`: manages the dark/light theme preference with persistence to local storage.

This approach eliminates manual state management for server data, reduces boilerplate code, and ensures that the UI remains synchronised with the backend state without explicit refresh logic.

### 4.5.3 Theme System

SmartGrader implements a dark/light theme system using CSS custom properties and the `data-theme` attribute on the document root element. The theme toggle component switches between `data-theme="light"` and `data-theme="dark"`, which triggers a complete recomputation of all colour variables defined in the Tailwind configuration. The user's theme preference is persisted to the browser's local storage and restored on subsequent visits, with an initial default derived from the operating system's preferred colour scheme via the `prefers-color-scheme` media query.

### 4.5.4 Page Structure

The application comprises seven pages, each corresponding to a major functional area:

1. **Dashboard**: displays aggregate statistics (total exams, total students, average score, recent activity) with Recharts bar and pie charts for score distribution and exam-level performance summaries.
2. **Exams**: lists all examinations in a sortable, searchable table with creation, edit, and delete actions.
3. **Exam Detail**: displays a single examination's metadata, its list of questions with choices, the generated answer sheet preview, and per-question editing capabilities.
4. **Scanner**: provides two tabbed interfaces -- the MCQ tab for uploading and processing scanned answer sheets via the computer vision pipeline, and the AI tab for uploading handwritten answer sheets and invoking the AI grading pipeline with OCR review and correction capabilities.
5. **Students**: a searchable registry of students with CRUD operations and unique matricule validation.
6. **Results**: displays grading results with filtering by examination, sortable columns, and exportable data.
7. **Settings**: application configuration including theme selection, scanner threshold adjustments, and AI model status monitoring.

### 4.5.5 Responsive Layout

The layout employs a collapsible sidebar navigation pattern. On desktop viewports (width above 1024 pixels), the sidebar remains permanently visible alongside the main content area. On tablet and mobile viewports, the sidebar collapses into a hamburger menu overlay. All pages use responsive grid layouts that adapt from multi-column on desktop to single-column on mobile, ensuring usability across device form factors.

## 4.6 Screenshots

Annotated screenshots of each page of the SmartGrader application are included in Appendix D (User Manual). These screenshots illustrate the final state of the user interface after the implementation of all features described in this chapter, including the dashboard with sample data, the exam creation workflow, the scanner interface with bubble detection overlay, the AI grading interface with OCR results and correction form, and the results page with score distribution charts.

<!-- TODO: Insert annotated screenshots when available -->
<!-- Figure 4.1: Dashboard page -->
<!-- Figure 4.2: Exam creation form -->
<!-- Figure 4.3: Scanner MCQ tab with detection results -->
<!-- Figure 4.4: Scanner AI tab with OCR and evaluation -->
<!-- Figure 4.5: Results page with score distribution -->
<!-- Figure 4.6: Settings page with theme toggle -->

## Summary

This chapter has presented the implementation of SmartGrader across its backend, scanner, AI, and frontend layers. The Flask application factory pattern provides clean configuration management and extension initialisation. The service layer pattern decouples business logic from HTTP handling, facilitating both testing and future extensibility. The scanner pipeline employs a five-stage approach -- preprocessing, marker detection, bubble detection, grid mapping, and answer reading -- that transforms raw scanned images into structured answers through a series of well-defined image processing operations. The AI integration leverages 4-bit quantisation to run a 3-billion parameter vision-language model on consumer hardware, with a RAG feedback loop that progressively improves grading accuracy from teacher corrections. The React frontend provides a modern, responsive, and accessible user interface with server state management via TanStack Query and a comprehensive dark/light theme system. Chapter 5 presents the testing methodology and empirical results that validate this implementation.
