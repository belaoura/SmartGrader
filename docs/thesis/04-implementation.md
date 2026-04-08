# Chapter 4: Implementation

This chapter presents the implementation of SmartGrader across all four development phases. It covers the development environment and tools, the backend implementation (Flask application factory, SQLAlchemy models, service layer, scanner pipeline), the authentication system, the online examination engine, the anti-cheat proctoring layer, the AI integration, the frontend application, and the deployment configurations. The discussion follows the layered architecture established in Chapter 3.

## 4.1 Development Environment

SmartGrader is developed using a technology stack that spans backend processing, computer vision, machine learning, browser-native AI inference, and frontend user interfaces. Table 4.1 enumerates the principal technologies and their roles within the system.

| Technology | Version | Role |
|------------|---------|------|
| Python | 3.10 | Backend programming language |
| Flask | 3.1 | Lightweight web framework and REST API server |
| SQLAlchemy | 2.0 | Object-relational mapper for database access |
| Flask-Migrate | - | Alembic-based database migration management |
| Flask-JWT-Extended | - | JWT token generation and validation decorators |
| bcrypt | - | Password hashing for user authentication |
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
| TensorFlow.js | 4.x | Browser-native machine learning inference |
| @tensorflow-models/blazeface | - | BlazeFace model for browser face detection |
| Recharts | - | Charting library for dashboard visualisations |
| pytest | - | Python testing framework |
| Gunicorn | - | Production WSGI server |
| Nginx | - | Reverse proxy and static file server |
| Docker / Docker Compose | - | Containerised deployment |
| wkhtmltopdf | - | PDF generation from HTML templates |

*Table 4.1: Technology stack for SmartGrader*

## 4.2 Project Structure

The SmartGrader codebase is organised into clearly separated directories that reflect the layered architecture described in Chapter 3. The following listing presents the full structure:

```
app/                          # Flask backend application
  __init__.py                 # Application factory (create_app)
  config.py                   # Centralised configuration
  errors.py                   # Custom exception hierarchy
  logging_config.py           # Structured logging setup
  models/                     # SQLAlchemy ORM models
    exam.py                   #   Exam, Question, Choice
    student.py                #   Student, StudentAnswer
    result.py                 #   Result
    ai_correction.py          #   AICorrection (RAG feedback)
    user.py                   #   User (authentication)
    group.py                  #   StudentGroup, GroupMember
    session.py                #   ExamSession, ExamAttempt, OnlineAnswer
    proctor.py                #   ProctorEvent, ProctorSnapshot
  services/                   # Business logic layer
    exam_service.py           #   Exam CRUD and statistics
    grading_service.py        #   MCQ grading and result persistence
    scanner_service.py        #   Scanner pipeline orchestration
    ai_service.py             #   AI pipeline orchestration
    auth_service.py           #   JWT, bcrypt, user management
    group_service.py          #   Student group CRUD
    session_service.py        #   Exam session lifecycle
    exam_take_service.py      #   Attempt creation, answer persistence, grading
    proctor_service.py        #   Event/snapshot ingestion, dashboard queries
  scanner/                    # Image processing pipeline
    preprocessor.py
    marker_finder.py
    detector.py
    grid_mapper.py
    answer_reader.py
  ai/                         # Vision-language model integration
    model_loader.py
    ocr_pipeline.py
    answer_evaluator.py
    prompt_templates.py
  auth/                       # Authentication utilities
    decorators.py             #   @require_auth, @require_role
    token_utils.py            #   JWT generation and validation
  routes/                     # Flask blueprints (REST API)
    exams.py
    questions.py
    students.py
    scanning.py
    grading.py
    ai.py
    auth.py                   #   /api/auth endpoints
    groups.py                 #   /api/groups endpoints
    sessions.py               #   /api/sessions endpoints
    exam_take.py              #   /api/exam endpoints
    proctor.py                #   /api/proctor endpoints

frontend/                     # React single-page application
  src/
    components/               # Reusable UI components
      layout/
      dashboard/
      exams/
      scanner/
      students/
      results/
      auth/                   #   LoginForm, RegisterForm
      exam/                   #   ExamTake, QuestionCard, Timer
      proctor/                #   ProctorEngine, EventLog, SnapshotGrid
      groups/                 #   GroupForm, MemberList
      sessions/               #   SessionCard, MonitorDashboard
    pages/
      Dashboard.jsx
      Exams.jsx
      ExamDetail.jsx
      Scanner.jsx
      Students.jsx
      Results.jsx
      Settings.jsx
      Login.jsx               #   Authentication page
      ExamTake.jsx            #   Student examination page
      ProctorDashboard.jsx    #   Teacher proctoring view
      Groups.jsx              #   Student group management
      Sessions.jsx            #   Session management
    hooks/
      use-exams.js
      use-students.js
      use-results.js
      use-ai.js
      use-theme.js
      use-auth.js             #   Login, logout, JWT storage
      use-exam-take.js        #   Attempt lifecycle, answer saving
      use-proctor.js          #   ProctorEngine integration
      use-sessions.js         #   Session CRUD and activation
      use-groups.js           #   Group management

tests/                        # 191 automated pytest tests
  conftest.py
  test_models/                # 22 model-layer tests
  test_services/              # 35 service-layer tests
  test_scanner/               # 11 scanner pipeline tests
  test_routes/                # 45 HTTP endpoint tests
  test_ai/                    # 16 AI module tests
  test_auth/                  # 28 authentication tests
  test_session/               # 20 online exam tests
  test_proctor/               # 14 proctoring tests

nginx/                        # Nginx configuration
  nginx.conf                  #   Reverse proxy and SSL config
docker-compose.yml            # Docker Compose deployment
Dockerfile                    # Application container image
schema.sql                    # Raw SQL schema (15 tables + indexes)
```

## 4.3 Backend Implementation

### 4.3.1 Application Factory

SmartGrader employs the Flask application factory pattern. The factory function `create_app()` in `app/__init__.py` initialises all extensions (SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, CORS) and registers all blueprints including the new auth, groups, sessions, exam_take, and proctor blueprints:

```python
def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name[config_name])

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=app.config.get("CORS_ORIGINS", "*"))

    setup_logging(
        log_level=app.config.get("LOG_LEVEL", "INFO"),
        log_file=app.config.get("LOG_FILE"),
    )

    from app.routes import register_blueprints
    register_blueprints(app)

    return app
```

The `CORS_ORIGINS` configuration parameter is set to `"*"` in development and to the specific frontend URL in production, enforcing the CORS hardening required for the university server deployment mode.

### 4.3.2 Configuration Management

The `Config` class in `app/config.py` centralises all application parameters. New configuration keys added for Phases 1–4 include:

- `JWT_SECRET_KEY`, `JWT_ACCESS_TOKEN_EXPIRES`: JWT signing key and token lifetime.
- `PROCTOR_WARNING_THRESHOLD`: Number of integrity violations before automatic attempt termination (default: 3).
- `PROCTOR_SNAPSHOT_INTERVAL`: Snapshot capture interval in seconds.
- `CORS_ORIGINS`: Allowed origins for CORS policy enforcement.
- `GUNICORN_WORKERS`, `GUNICORN_BIND`: Gunicorn process count and bind address for production.

### 4.3.3 SQLAlchemy Models

The data model has expanded from 7 to 15 tables across Phases 1–4. The new models follow the same design conventions as the original: each inherits from `db.Model`, defines columns as class attributes, and implements a `to_dict()` method.

The `User` model supports both teacher and student accounts:

```python
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'teacher' or 'student'
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=True)
    created_at = db.Column(db.String(30), nullable=False)
```

The `ExamAttempt` model tracks the lifecycle of each student's examination sitting:

```python
class ExamAttempt(db.Model):
    __tablename__ = "exam_attempts"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("exam_sessions.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    started_at = db.Column(db.String(30), nullable=False)
    submitted_at = db.Column(db.String(30), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="in_progress")
    score = db.Column(db.Float, nullable=True)
    percentage = db.Column(db.Float, nullable=True)
```

### 4.3.4 Service Layer Pattern

The service layer has been extended with five new modules: `AuthService`, `GroupService`, `SessionService`, `ExamTakeService`, and `ProctorService`. Each follows the same stateless function pattern as the original services.

The `ExamTakeService.submit_attempt()` function illustrates the auto-grading logic executed on submission:

```python
def submit_attempt(attempt_id):
    attempt = get_attempt_by_id(attempt_id)
    if attempt.status != "in_progress":
        raise ValidationError("Attempt already finalised.")

    answers = OnlineAnswer.query.filter_by(attempt_id=attempt_id).all()
    questions = (Question.query
                 .filter_by(exam_id=attempt.session.exam_id)
                 .all())

    total_marks = 0
    obtained_marks = 0
    for question in questions:
        total_marks += question.marks
        correct = question.choices.filter_by(is_correct=1).first()
        student_answer = next(
            (a for a in answers if a.question_id == question.id), None
        )
        if student_answer and correct:
            if student_answer.selected_choice_id == correct.id:
                obtained_marks += question.marks

    percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
    attempt.score = obtained_marks
    attempt.percentage = round(percentage, 1)
    attempt.status = "submitted"
    attempt.submitted_at = datetime.utcnow().isoformat()
    db.session.commit()

    return attempt.to_dict()
```

### 4.3.5 Scanner Pipeline

The scanner pipeline is unchanged from the original design: preprocessing, marker detection, bubble detection, grid mapping, and answer reading. The five-stage pipeline is documented in detail in Section 4.3.5 of the original implementation chapter.

## 4.4 Authentication Implementation

### 4.4.1 Password Hashing

User passwords are hashed using bcrypt via the `bcrypt` library. The `AuthService.register_user()` function generates a salted hash:

```python
import bcrypt

def register_user(username, password, role, student_id=None):
    if User.query.filter_by(username=username).first():
        raise ConflictError(f"Username '{username}' already exists.")
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = User(
        username=username,
        password_hash=hashed.decode("utf-8"),
        role=role,
        student_id=student_id,
        created_at=datetime.utcnow().isoformat(),
    )
    db.session.add(user)
    db.session.commit()
    return user
```

### 4.4.2 JWT Token Generation

On successful login, `AuthService.login()` verifies the password hash and delegates to Flask-JWT-Extended to generate a signed access token:

```python
from flask_jwt_extended import create_access_token

def login(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(
        password.encode("utf-8"), user.password_hash.encode("utf-8")
    ):
        raise AuthenticationError("Invalid username or password.")

    token = create_access_token(
        identity=user.id,
        additional_claims={"role": user.role, "username": user.username}
    )
    return {"access_token": token, "role": user.role, "user_id": user.id}
```

### 4.4.3 Route Decorators

The `app/auth/decorators.py` module provides two decorators that wrap Flask-JWT-Extended's `@jwt_required()`:

```python
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from app.errors import AuthenticationError, AuthorizationError

def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return fn(*args, **kwargs)
    return wrapper

def require_role(role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != role:
                raise AuthorizationError(
                    f"This action requires the '{role}' role."
                )
            return fn(*args, **kwargs)
        return wrapper
    return decorator
```

These decorators are applied directly to route handler functions:

```python
@sessions_bp.route("/api/sessions", methods=["POST"])
@require_role("teacher")
def create_session():
    ...
```

### 4.4.4 Barcode Login

Student barcode login accepts a `matricule` value encoded in the barcode and issues a student-role JWT without requiring a password:

```python
@auth_bp.route("/api/auth/barcode-login", methods=["POST"])
def barcode_login():
    matricule = request.json.get("matricule")
    student = Student.query.filter_by(matricule=matricule).first()
    if not student:
        raise NotFoundError("No student found with this matricule.")
    user = User.query.filter_by(student_id=student.id).first()
    if not user:
        raise NotFoundError("No user account linked to this student.")
    token = create_access_token(
        identity=user.id,
        additional_claims={"role": "student"}
    )
    return jsonify({"access_token": token}), 200
```

## 4.5 Online Examination Engine

### 4.5.1 Session Service

The `SessionService` manages the lifecycle of exam sessions. Sessions transition through three states: `scheduled` → `active` → `closed`. The `activate_session()` function validates that the scheduled start time has not passed and sets the status to `active`, making the session visible to enrolled students.

### 4.5.2 Exam Take Service

The `ExamTakeService` handles all student-facing examination interactions:

- `create_attempt(session_id, student_id)`: Creates an ExamAttempt record, verifying that the student is enrolled in the session's group and does not already have an active attempt.
- `save_answer(attempt_id, question_id, choice_id)`: Creates or updates an OnlineAnswer record within the attempt.
- `submit_attempt(attempt_id)`: Finalises the attempt, computes the MCQ score, and sets the submission timestamp.

### 4.5.3 Answer Persistence

Each answer selection by the student triggers an immediate API call to persist the OnlineAnswer record. This ensures that if the student's browser closes unexpectedly, their answers are preserved and the attempt can be resumed or auto-submitted at the deadline. The persistence call is debounced with a 500 ms delay to avoid excessive API requests during rapid question navigation.

### 4.5.4 Auto-Submission

Two mechanisms enforce the examination deadline:

**Client-side:** A JavaScript countdown timer component tracks the remaining time (computed from `start_time + duration_minutes - current_time`). On reaching zero, the timer component calls `submitAttempt()`, which issues `POST /api/exam/attempt/<id>/submit`. A confirmation dialog is skipped for timer-triggered submission to prevent the student from delaying.

**Server-side:** A lightweight background check (invoked on each student request) compares the attempt's `started_at` timestamp plus the session's `duration_minutes` against the current time. If the deadline has passed and the attempt status is still `in_progress`, the server calls `submit_attempt()` automatically before returning the response.

## 4.6 Anti-Cheat Implementation

### 4.6.1 ProctorEngine Architecture

The `ProctorEngine` is a JavaScript module (`frontend/src/components/proctor/ProctorEngine.jsx`) that runs within the student examination page. It initialises on attempt start and cleans up on submission. Its architecture consists of three concurrent loops:

1. **Face Detection Loop:** Runs at `PROCTOR_FACE_CHECK_INTERVAL` (default: 1000 ms). Captures a video frame from the webcam MediaStream, passes it to the BlazeFace model via TensorFlow.js, and reports a `face_missing` or `multiple_faces` event if the detection result is abnormal.

2. **Snapshot Loop:** Runs at `PROCTOR_SNAPSHOT_INTERVAL` (default: 30 seconds). Captures a JPEG snapshot from the webcam, encodes it as a Base64 data URL, and transmits it via `POST /api/proctor/snapshot`.

3. **Event Listeners:** Attached to `document.addEventListener` for `visibilitychange`, `fullscreenchange`, `blur`, `copy`, and `paste` events. Each triggered event is reported via `POST /api/proctor/event`.

### 4.6.2 BlazeFace Integration

TensorFlow.js and the BlazeFace model are loaded dynamically on examination start to avoid adding to the main bundle:

```javascript
import * as tf from "@tensorflow/tfjs";
import * as blazeface from "@tensorflow-models/blazeface";

async function loadModel() {
  await tf.ready();
  const model = await blazeface.load();
  return model;
}

async function detectFaces(model, videoElement) {
  const predictions = await model.estimateFaces(videoElement, false);
  return predictions; // array of detected faces
}
```

The ProctorEngine calls `detectFaces()` at each tick of the face detection loop. If `predictions.length === 0`, a `face_missing` event is generated. If `predictions.length > 1`, a `multiple_faces` event is generated. Both events increment the local warning counter, and a warning overlay is displayed to the student.

### 4.6.3 Warning Escalation

The warning escalation system operates as follows:

1. Each `face_missing` and `multiple_faces` event increments both a local counter (React state) and a server-side counter (maintained in the ExamAttempt record or derived from ProctorEvent count).
2. At `WARNING_THRESHOLD / 2`, the student sees a yellow warning banner: "Your face is not visible. Please ensure your face is in view of the camera."
3. At `WARNING_THRESHOLD - 1`, the student sees a red warning dialog that must be acknowledged to continue.
4. At `WARNING_THRESHOLD`, the attempt is automatically submitted and the student is shown a session-terminated message.

### 4.6.4 Proctoring Dashboard

The teacher-facing `ProctorDashboard` page polls `GET /api/sessions/<id>/attempts` every 5 seconds to display the live status of all students. For each student, it shows:

- Attempt status (in progress / submitted / terminated)
- Warning count and severity distribution
- Most recent snapshot thumbnail
- Time elapsed since last activity

Clicking a student row opens a detailed panel showing the complete event timeline (sorted by `occurred_at`) and a scrollable grid of snapshots. Each snapshot is annotated with the `face_detected` flag, making it easy for the teacher to review intervals where no face was visible.

## 4.7 AI Integration

The AI grading pipeline is unchanged from the original implementation. The Qwen2.5-VL-3B-Instruct model is loaded with 4-bit quantisation via BitsAndBytes, using a lazy singleton pattern. The two-stage OCR + Evaluation pipeline and the RAG feedback loop are as described in the original design and are fully operational in the production system.

## 4.8 Frontend Implementation

### 4.8.1 Architecture

The frontend is a React 18 single-page application built with Vite. The styling layer combines Tailwind CSS 4.0 with shadcn/ui. TanStack Query manages all server state. The routing layer uses React Router v6, with protected routes that redirect unauthenticated users to the login page.

### 4.8.2 Authentication State

The `use-auth.js` hook manages the authentication lifecycle:

```javascript
export function useAuth() {
  const queryClient = useQueryClient();

  const loginMutation = useMutation({
    mutationFn: ({ username, password }) =>
      api.post("/auth/login", { username, password }),
    onSuccess: (data) => {
      localStorage.setItem("token", data.access_token);
      queryClient.setQueryData(["me"], data);
    },
  });

  const logout = () => {
    localStorage.removeItem("token");
    queryClient.clear();
  };

  return { loginMutation, logout };
}
```

The stored JWT is automatically attached to all API requests by an Axios request interceptor that reads `localStorage.getItem("token")` and injects it into the `Authorization` header.

### 4.8.3 Student Examination Page

The `ExamTake.jsx` page provides the student-facing examination interface:

1. **Header:** Displays the examination title, remaining time (countdown), and warning count.
2. **Question Panel:** Renders each question with radio buttons for MCQ choices. Selecting a choice immediately triggers `use-exam-take.js`'s `saveAnswer` mutation.
3. **Navigation:** Previous/next buttons for question-by-question navigation. A question grid overview allows jumping to any question.
4. **Proctor Overlay:** The `ProctorEngine` component is mounted as an invisible child; it manages the webcam stream and detection loops without rendering visible UI elements beyond the warning banners.
5. **Submit Button:** Available at all times; triggers a confirmation dialog (unless timer-triggered).

### 4.8.4 Page Structure

The application has been extended from the original seven pages to thirteen pages:

| Page | Route | Role |
|------|-------|------|
| Login | `/login` | Public |
| Dashboard | `/` | Teacher |
| Exams | `/exams` | Teacher |
| Exam Detail | `/exams/:id` | Teacher |
| Scanner | `/scanner` | Teacher |
| Students | `/students` | Teacher |
| Groups | `/groups` | Teacher |
| Sessions | `/sessions` | Teacher |
| Proctor Dashboard | `/sessions/:id/proctor` | Teacher |
| Results | `/results` | Teacher |
| Settings | `/settings` | Teacher |
| Exam Take | `/exam` | Student |

### 4.8.5 Responsive Layout and Theme

The layout, theme system, and server state management architecture are unchanged from the original implementation, using the collapsible sidebar pattern, CSS custom properties for dark/light themes, and TanStack Query for caching.

## 4.9 Deployment Configurations

### 4.9.1 LAN Mode (Gunicorn)

For classroom or departmental deployments on a local area network, SmartGrader is served by Gunicorn with multiple worker processes:

```bash
gunicorn "app:create_app('production')" \
  --workers 4 \
  --bind 0.0.0.0:5000 \
  --timeout 120 \
  --access-logfile logs/access.log
```

The number of workers is set to `2 * CPU_CORES + 1` as recommended by the Gunicorn documentation, providing concurrency for simultaneous student examination sessions.

### 4.9.2 University Server Mode (Nginx + Gunicorn)

For university server deployment, Nginx acts as a reverse proxy, handling SSL/TLS termination and static file serving:

```nginx
server {
    listen 443 ssl;
    server_name smartgrader.university.dz;

    ssl_certificate     /etc/ssl/certs/smartgrader.crt;
    ssl_certificate_key /etc/ssl/private/smartgrader.key;

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        add_header Access-Control-Allow-Origin "https://smartgrader.university.dz";
    }

    location / {
        root /var/www/smartgrader/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

The `add_header Access-Control-Allow-Origin` directive restricts cross-origin requests to the university's domain, enforcing the CORS hardening requirement.

### 4.9.3 Docker Mode

The Docker Compose configuration defines two services:

```yaml
services:
  api:
    build: .
    environment:
      - FLASK_ENV=production
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - CORS_ORIGINS=http://localhost
    volumes:
      - ./instance:/app/instance
      - ./uploads:/app/uploads
    ports:
      - "5000:5000"

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - ./frontend/dist:/usr/share/nginx/html
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api
```

The `instance/` volume persists the SQLite database across container restarts, and the `uploads/` volume preserves uploaded scan images and proctoring snapshots.

## 4.10 Screenshots

Annotated screenshots of each page of the SmartGrader application are included in Appendix D (User Manual). These screenshots illustrate the final state of the user interface after the implementation of all four phases, including the login page, the teacher dashboard with monitoring statistics, the student examination interface with the timer and warning overlays, the proctoring dashboard with event timelines and snapshots, the group management page, and the session scheduling interface.

<!-- TODO: Insert annotated screenshots when available -->

## Summary

This chapter has presented the implementation of SmartGrader across its four development phases. Phase 1 established JWT authentication with bcrypt password hashing, role-based route decorators, and barcode login for students. Phase 2 delivered the online examination engine with session management, answer persistence, and auto-submission on timer expiry. Phase 3 implemented the browser-native ProctorEngine using TensorFlow.js BlazeFace for face detection, browser event tracking, periodic snapshot capture, and teacher-facing proctoring dashboard. Phase 4 provided three production deployment configurations: LAN mode with Gunicorn, university server mode with Nginx and SSL, and Docker Compose for containerised deployment. The original scanner pipeline and AI integration from earlier phases remain fully operational, and the test suite has grown to 191 tests covering all architectural layers. Chapter 5 presents the testing methodology and empirical results that validate this implementation.
