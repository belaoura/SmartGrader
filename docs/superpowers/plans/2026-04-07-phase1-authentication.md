# Phase 1: Authentication & Student Login — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add JWT-based authentication with teacher email/password login and student barcode-scan login, role-based route protection, CSV student import, and admin management — with zero breaking changes to existing models.

**Architecture:** New `User` model links to existing `Student` via FK. JWT access/refresh tokens in httpOnly cookies. Auth decorators protect existing routes. React `AuthProvider` context + `ProtectedRoute` guards the frontend. `html5-qrcode` handles browser-side barcode scanning.

**Tech Stack:** Flask + PyJWT + bcrypt + Flask-Limiter (backend), React 19 + React Router 7 + html5-qrcode (frontend)

---

## File Structure

```
NEW FILES:
  app/models/user.py              — User model (auth identity)
  app/auth.py                     — JWT helpers + @require_auth, @require_role, @require_admin decorators
  app/services/auth_service.py    — login, logout, refresh, create_teacher
  app/services/import_service.py  — CSV student import
  app/routes/auth.py              — /api/auth/* blueprint
  app/routes/admin.py             — /api/admin/* blueprint
  scripts/create_admin.py         — CLI bootstrap command
  tests/test_models/test_user.py
  tests/test_services/test_auth_service.py
  tests/test_services/test_import_service.py
  tests/test_routes/test_auth.py
  tests/test_routes/test_admin.py
  frontend/src/contexts/AuthContext.jsx
  frontend/src/components/ProtectedRoute.jsx
  frontend/src/components/BarcodeScanner.jsx
  frontend/src/pages/LoginPage.jsx
  frontend/src/pages/TeacherManagement.jsx
  frontend/src/pages/StudentImport.jsx
  frontend/src/hooks/use-auth.js

MODIFIED FILES:
  requirements.txt                — add PyJWT, bcrypt, Flask-Limiter
  app/models/__init__.py          — export User
  app/config.py                   — add JWT/auth config
  app/errors.py                   — add AuthenticationError, AuthorizationError
  app/__init__.py                 — register auth/admin blueprints, init Flask-Limiter
  app/routes/__init__.py          — register auth_bp, admin_bp
  app/routes/exams.py             — add @require_auth @require_role("teacher")
  app/routes/students.py          — add @require_auth @require_role("teacher")
  app/routes/questions.py         — add @require_auth @require_role("teacher")
  app/routes/scanning.py          — add @require_auth @require_role("teacher")
  app/routes/grading.py           — add @require_auth @require_role("teacher")
  app/routes/ai.py                — add @require_auth @require_role("teacher")
  tests/conftest.py               — add auth helper fixtures
  frontend/package.json           — add html5-qrcode
  frontend/src/main.jsx           — wrap with AuthProvider
  frontend/src/App.jsx            — add ProtectedRoute, login route, admin routes
  frontend/src/lib/api.js         — add credentials + 401 refresh interceptor
```

---

## Task 1: Install Dependencies & Update Config

**Files:**
- Modify: `requirements.txt`
- Modify: `app/config.py:89-113`
- Modify: `app/errors.py`

- [ ] **Step 1: Add Python dependencies to requirements.txt**

Add these three lines at the end of `requirements.txt`:

```
# Authentication
PyJWT>=2.8.0
bcrypt>=4.1.0
Flask-Limiter>=3.5.0
```

- [ ] **Step 2: Install the new dependencies**

Run: `pip install PyJWT bcrypt Flask-Limiter`

- [ ] **Step 3: Add auth config to app/config.py**

Add these lines inside the `Config` class, after the `LOG_FILE` line (line 86):

```python
    # Authentication
    JWT_ACCESS_TOKEN_EXPIRES = 900        # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRES = 604800    # 7 days
    BCRYPT_LOG_ROUNDS = 12
    RATELIMIT_LOGIN = "5 per minute"
```

- [ ] **Step 4: Add auth exceptions to app/errors.py**

Add at the end of `app/errors.py`:

```python
class AuthenticationError(SmartGraderError):
    """Raised when authentication fails."""

    def __init__(self, message="Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationError(SmartGraderError):
    """Raised when user lacks required permissions."""

    def __init__(self, message="Permission denied"):
        super().__init__(message, status_code=403)
```

- [ ] **Step 5: Verify config loads**

Run: `python -c "from app.config import Config; print(Config.JWT_ACCESS_TOKEN_EXPIRES)"`
Expected: `900`

- [ ] **Step 6: Commit**

```bash
git add requirements.txt app/config.py app/errors.py
git commit -m "feat(auth): add dependencies and config for JWT authentication"
```

---

## Task 2: User Model

**Files:**
- Create: `app/models/user.py`
- Modify: `app/models/__init__.py`
- Create: `tests/test_models/test_user.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_models/test_user.py`:

```python
"""Tests for User model."""

import pytest
import sqlalchemy
from app.models.user import User
from app.models.student import Student
from app.models import db as _db


def test_create_teacher_user(db):
    user = User(
        name="Prof Ahmed",
        email="ahmed@univ.dz",
        password_hash="fakehash",
        role="teacher",
    )
    db.session.add(user)
    db.session.commit()

    assert user.id is not None
    assert user.role == "teacher"
    assert user.is_admin is False
    assert user.is_active is True
    assert user.token_version == 0
    assert user.student_id is None


def test_create_student_user(db):
    student = Student(name="Fatima", matricule="2026001", email="fatima@univ.dz")
    db.session.add(student)
    db.session.commit()

    user = User(role="student", student_id=student.id)
    db.session.add(user)
    db.session.commit()

    assert user.id is not None
    assert user.role == "student"
    assert user.student_id == student.id
    assert user.student.name == "Fatima"
    assert user.email is None
    assert user.password_hash is None


def test_teacher_unique_email(db):
    u1 = User(name="A", email="same@univ.dz", password_hash="h", role="teacher")
    u2 = User(name="B", email="same@univ.dz", password_hash="h", role="teacher")
    db.session.add(u1)
    db.session.commit()

    db.session.add(u2)
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_student_users_allow_null_email(db):
    s1 = Student(name="A", matricule="001")
    s2 = Student(name="B", matricule="002")
    db.session.add_all([s1, s2])
    db.session.commit()

    u1 = User(role="student", student_id=s1.id)
    u2 = User(role="student", student_id=s2.id)
    db.session.add_all([u1, u2])
    db.session.commit()

    assert u1.email is None
    assert u2.email is None


def test_user_to_dict_teacher(db):
    user = User(name="Prof", email="prof@univ.dz", password_hash="h", role="teacher", is_admin=True)
    db.session.add(user)
    db.session.commit()

    d = user.to_dict()
    assert d["name"] == "Prof"
    assert d["email"] == "prof@univ.dz"
    assert d["role"] == "teacher"
    assert d["is_admin"] is True
    assert "password_hash" not in d


def test_user_to_dict_student(db):
    student = Student(name="Ali", matricule="003")
    db.session.add(student)
    db.session.commit()

    user = User(role="student", student_id=student.id)
    db.session.add(user)
    db.session.commit()

    d = user.to_dict()
    assert d["name"] == "Ali"
    assert d["role"] == "student"
    assert d["student_id"] == student.id


def test_token_version_bump(db):
    user = User(name="T", email="t@t.dz", password_hash="h", role="teacher")
    db.session.add(user)
    db.session.commit()

    assert user.token_version == 0
    user.token_version += 1
    db.session.commit()
    assert user.token_version == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models/test_user.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.models.user'`

- [ ] **Step 3: Create User model**

Create `app/models/user.py`:

```python
"""User model for authentication."""

from datetime import datetime, timezone
from app.models import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=True)
    role = db.Column(db.String(20), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=True)
    token_version = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.String(30), default=lambda: datetime.now(timezone.utc).isoformat())

    student = db.relationship("Student", backref="user", uselist=False)

    def to_dict(self):
        name = self.name
        if self.role == "student" and self.student:
            name = self.student.name
        return {
            "id": self.id,
            "name": name,
            "email": self.email,
            "role": self.role,
            "is_admin": self.is_admin,
            "student_id": self.student_id,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }
```

- [ ] **Step 4: Export User in models/__init__.py**

Add this line at the end of `app/models/__init__.py`:

```python
from app.models.user import User  # noqa: E402, F401
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_models/test_user.py -v`
Expected: all 7 tests PASS

- [ ] **Step 6: Run full test suite to verify no regressions**

Run: `pytest tests/ -v --tb=short`
Expected: all existing tests still pass

- [ ] **Step 7: Commit**

```bash
git add app/models/user.py app/models/__init__.py tests/test_models/test_user.py
git commit -m "feat(auth): add User model with role, token_version, student FK"
```

---

## Task 3: JWT Helpers & Auth Decorators

**Files:**
- Create: `app/auth.py`

- [ ] **Step 1: Create app/auth.py**

```python
"""JWT helpers and authentication decorators."""

import logging
from datetime import datetime, timezone, timedelta
from functools import wraps

import jwt
from flask import request, g, current_app, jsonify

from app.models.user import User

logger = logging.getLogger("smartgrader.auth")


def encode_access_token(user):
    """Create a short-lived access JWT for the given user."""
    payload = {
        "sub": user.id,
        "role": user.role,
        "ver": user.token_version,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(
            seconds=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        ),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def encode_refresh_token(user):
    """Create a long-lived refresh JWT for the given user."""
    payload = {
        "sub": user.id,
        "ver": user.token_version,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(
            seconds=current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
        ),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_token(token):
    """Decode and verify a JWT. Returns the payload dict or None."""
    try:
        return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        logger.debug("Token expired")
        return None
    except jwt.InvalidTokenError:
        logger.debug("Invalid token")
        return None


def set_auth_cookies(response, user):
    """Set access and refresh token cookies on a response."""
    access_token = encode_access_token(user)
    refresh_token = encode_refresh_token(user)

    is_prod = not current_app.config.get("DEBUG", False)

    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=is_prod,
        samesite="Lax",
        max_age=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
        path="/",
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=is_prod,
        samesite="Lax",
        max_age=current_app.config["JWT_REFRESH_TOKEN_EXPIRES"],
        path="/api/auth/refresh",
    )
    return response


def clear_auth_cookies(response):
    """Remove auth cookies from a response."""
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/auth/refresh")
    return response


def require_auth(f):
    """Decorator: require a valid access token. Sets g.current_user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("access_token")
        if not token:
            return jsonify({"error": "Authentication required"}), 401

        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            return jsonify({"error": "Invalid or expired token"}), 401

        user = User.query.get(payload["sub"])
        if not user:
            return jsonify({"error": "User not found"}), 401
        if not user.is_active:
            return jsonify({"error": "Account is disabled"}), 401
        if user.token_version != payload.get("ver"):
            return jsonify({"error": "Session expired"}), 401

        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def require_role(role_name):
    """Decorator factory: require a specific role. Must be used after @require_auth."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if g.current_user.role != role_name:
                return jsonify({"error": "Permission denied"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


def require_admin(f):
    """Decorator: require admin flag. Must be used after @require_auth."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated
```

- [ ] **Step 2: Verify import works**

Run: `python -c "from app.auth import require_auth, require_role, require_admin; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add app/auth.py
git commit -m "feat(auth): add JWT helpers and auth decorators"
```

---

## Task 4: Auth Service

**Files:**
- Create: `app/services/auth_service.py`
- Create: `tests/test_services/test_auth_service.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_services/test_auth_service.py`:

```python
"""Tests for auth service."""

import pytest
from app.models.user import User
from app.models.student import Student
from app.models import db as _db
from app.services.auth_service import (
    create_teacher,
    login_teacher,
    login_student,
    logout_user,
)
from app.errors import AuthenticationError, NotFoundError


def test_create_teacher(db):
    user = create_teacher(
        email="prof@univ.dz",
        password="securepass",
        name="Prof Ahmed",
        is_admin=False,
    )
    assert user.id is not None
    assert user.email == "prof@univ.dz"
    assert user.role == "teacher"
    assert user.password_hash is not None
    assert user.password_hash != "securepass"


def test_create_admin_teacher(db):
    user = create_teacher(
        email="admin@univ.dz",
        password="adminpass",
        name="Admin",
        is_admin=True,
    )
    assert user.is_admin is True


def test_create_teacher_duplicate_email(db):
    create_teacher(email="dup@univ.dz", password="pass", name="A")
    with pytest.raises(AuthenticationError, match="already exists"):
        create_teacher(email="dup@univ.dz", password="pass", name="B")


def test_login_teacher_success(app, db):
    create_teacher(email="login@univ.dz", password="mypassword", name="T")

    with app.test_request_context():
        user = login_teacher("login@univ.dz", "mypassword")
        assert user.email == "login@univ.dz"


def test_login_teacher_wrong_password(app, db):
    create_teacher(email="wrong@univ.dz", password="correct", name="T")

    with app.test_request_context():
        with pytest.raises(AuthenticationError, match="Invalid email or password"):
            login_teacher("wrong@univ.dz", "incorrect")


def test_login_teacher_unknown_email(app, db):
    with app.test_request_context():
        with pytest.raises(AuthenticationError, match="Invalid email or password"):
            login_teacher("nobody@univ.dz", "pass")


def test_login_teacher_inactive(app, db):
    user = create_teacher(email="inactive@univ.dz", password="pass", name="T")
    user.is_active = False
    db.session.commit()

    with app.test_request_context():
        with pytest.raises(AuthenticationError, match="Account is disabled"):
            login_teacher("inactive@univ.dz", "pass")


def test_login_teacher_bumps_token_version(app, db):
    create_teacher(email="bump@univ.dz", password="pass", name="T")

    with app.test_request_context():
        user = login_teacher("bump@univ.dz", "pass")
        assert user.token_version == 1
        user = login_teacher("bump@univ.dz", "pass")
        assert user.token_version == 2


def test_login_student_success(app, db):
    student = Student(name="Ali", matricule="2026001", email="ali@univ.dz")
    db.session.add(student)
    db.session.commit()

    user = User(role="student", student_id=student.id)
    db.session.add(user)
    db.session.commit()

    with app.test_request_context():
        result = login_student("2026001")
        assert result.role == "student"
        assert result.student_id == student.id


def test_login_student_unknown_matricule(app, db):
    with app.test_request_context():
        with pytest.raises(NotFoundError):
            login_student("UNKNOWN")


def test_login_student_no_user_account(app, db):
    student = Student(name="NoUser", matricule="999")
    db.session.add(student)
    db.session.commit()

    with app.test_request_context():
        with pytest.raises(AuthenticationError, match="No account"):
            login_student("999")


def test_logout_bumps_token_version(db):
    user = create_teacher(email="out@univ.dz", password="pass", name="T")
    old_ver = user.token_version
    logout_user(user.id)
    assert user.token_version == old_ver + 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_services/test_auth_service.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.auth_service'`

- [ ] **Step 3: Create auth service**

Create `app/services/auth_service.py`:

```python
"""Authentication service — login, logout, token management."""

import logging
import re

import bcrypt

from app.models import db
from app.models.user import User
from app.models.student import Student
from app.errors import AuthenticationError, NotFoundError

logger = logging.getLogger("smartgrader.services.auth")


def hash_password(password):
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password, password_hash):
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_teacher(email, password, name, is_admin=False):
    """Create a new teacher user account.

    Args:
        email: Teacher email address.
        password: Plaintext password (min 8 chars).
        name: Display name.
        is_admin: Whether this teacher has admin privileges.

    Returns:
        The created User object.

    Raises:
        AuthenticationError: If email already exists or validation fails.
    """
    if not email or not password or not name:
        raise AuthenticationError("Email, password, and name are required")
    if len(password) < 8:
        raise AuthenticationError("Password must be at least 8 characters")

    existing = User.query.filter_by(email=email).first()
    if existing:
        raise AuthenticationError(f"User with email {email} already exists")

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role="teacher",
        is_admin=is_admin,
    )
    db.session.add(user)
    db.session.commit()

    logger.info("Created teacher account: %s (admin=%s)", email, is_admin)
    return user


def login_teacher(email, password):
    """Authenticate a teacher by email and password.

    Args:
        email: Teacher email address.
        password: Plaintext password.

    Returns:
        The authenticated User object (token_version bumped).

    Raises:
        AuthenticationError: If credentials are invalid or account is disabled.
    """
    user = User.query.filter_by(email=email, role="teacher").first()
    if not user or not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid email or password")

    if not user.is_active:
        raise AuthenticationError("Account is disabled")

    user.token_version += 1
    db.session.commit()

    logger.info("Teacher logged in: %s", email)
    return user


def login_student(matricule):
    """Authenticate a student by matricule (from barcode scan).

    Args:
        matricule: Student matricule number.

    Returns:
        The authenticated User object (token_version bumped).

    Raises:
        NotFoundError: If no student with this matricule.
        AuthenticationError: If student has no user account or is disabled.
    """
    sanitized = re.sub(r"[^a-zA-Z0-9]", "", matricule)
    student = Student.query.filter_by(matricule=sanitized).first()
    if not student:
        raise NotFoundError("Student", sanitized)

    user = User.query.filter_by(student_id=student.id, role="student").first()
    if not user:
        raise AuthenticationError("No account linked to this student")

    if not user.is_active:
        raise AuthenticationError("Account is disabled")

    user.token_version += 1
    db.session.commit()

    logger.info("Student logged in: %s", sanitized)
    return user


def logout_user(user_id):
    """Invalidate all tokens for a user by bumping token_version.

    Args:
        user_id: The user ID to log out.
    """
    user = User.query.get(user_id)
    if user:
        user.token_version += 1
        db.session.commit()
        logger.info("User logged out: %s", user_id)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_services/test_auth_service.py -v`
Expected: all 12 tests PASS

- [ ] **Step 5: Run full test suite**

Run: `pytest tests/ -v --tb=short`
Expected: all tests pass, no regressions

- [ ] **Step 6: Commit**

```bash
git add app/services/auth_service.py tests/test_services/test_auth_service.py
git commit -m "feat(auth): add auth service with teacher/student login, logout"
```

---

## Task 5: Auth Routes (Blueprint)

**Files:**
- Create: `app/routes/auth.py`
- Modify: `app/routes/__init__.py`
- Modify: `app/__init__.py`
- Create: `tests/test_routes/test_auth.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_routes/test_auth.py`:

```python
"""Tests for auth API routes."""

import json
from app.models.user import User
from app.models.student import Student
from app.models import db as _db
from app.services.auth_service import create_teacher


def _create_teacher(db, email="prof@univ.dz", password="password123", name="Prof", is_admin=False):
    """Helper to create a teacher in the DB."""
    return create_teacher(email=email, password=password, name=name, is_admin=is_admin)


def _create_student_with_user(db):
    """Helper to create a student + linked user."""
    student = Student(name="Ali", matricule="2026001", email="ali@univ.dz")
    db.session.add(student)
    db.session.commit()
    user = User(role="student", student_id=student.id)
    db.session.add(user)
    db.session.commit()
    return student, user


def test_teacher_login_success(client, db):
    _create_teacher(db)
    response = client.post(
        "/api/auth/login",
        data=json.dumps({"email": "prof@univ.dz", "password": "password123"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["user"]["email"] == "prof@univ.dz"
    assert data["user"]["role"] == "teacher"
    assert "access_token" in response.headers.get("Set-Cookie", "")


def test_teacher_login_wrong_password(client, db):
    _create_teacher(db)
    response = client.post(
        "/api/auth/login",
        data=json.dumps({"email": "prof@univ.dz", "password": "wrong"}),
        content_type="application/json",
    )
    assert response.status_code == 401


def test_student_scan_login(client, db):
    _create_student_with_user(db)
    response = client.post(
        "/api/auth/scan",
        data=json.dumps({"matricule": "2026001"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["user"]["role"] == "student"
    assert data["user"]["name"] == "Ali"


def test_student_scan_unknown_matricule(client, db):
    response = client.post(
        "/api/auth/scan",
        data=json.dumps({"matricule": "UNKNOWN"}),
        content_type="application/json",
    )
    assert response.status_code == 404


def test_get_me_authenticated(client, db):
    _create_teacher(db)
    client.post(
        "/api/auth/login",
        data=json.dumps({"email": "prof@univ.dz", "password": "password123"}),
        content_type="application/json",
    )
    response = client.get("/api/auth/me")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["user"]["email"] == "prof@univ.dz"


def test_get_me_unauthenticated(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_logout(client, db):
    _create_teacher(db)
    client.post(
        "/api/auth/login",
        data=json.dumps({"email": "prof@univ.dz", "password": "password123"}),
        content_type="application/json",
    )
    response = client.post("/api/auth/logout")
    assert response.status_code == 200

    # After logout, /me should fail
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_refresh_token(client, db):
    _create_teacher(db)
    client.post(
        "/api/auth/login",
        data=json.dumps({"email": "prof@univ.dz", "password": "password123"}),
        content_type="application/json",
    )
    response = client.post("/api/auth/refresh")
    assert response.status_code == 200
    assert "access_token" in response.headers.get("Set-Cookie", "")


def test_single_session_enforcement(client, db):
    _create_teacher(db)

    # First login
    client.post(
        "/api/auth/login",
        data=json.dumps({"email": "prof@univ.dz", "password": "password123"}),
        content_type="application/json",
    )
    response = client.get("/api/auth/me")
    assert response.status_code == 200

    # Second login (simulated from another device — bumps token_version)
    # We manually bump token_version to simulate
    user = User.query.filter_by(email="prof@univ.dz").first()
    user.token_version += 1
    _db.session.commit()

    # Old session should now be invalid
    response = client.get("/api/auth/me")
    assert response.status_code == 401
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_routes/test_auth.py -v`
Expected: FAIL — `404` on `/api/auth/login` (route doesn't exist yet)

- [ ] **Step 3: Create auth routes blueprint**

Create `app/routes/auth.py`:

```python
"""Authentication API endpoints."""

import logging
from flask import Blueprint, request, jsonify, make_response

from app.auth import require_auth, set_auth_cookies, clear_auth_cookies, decode_token, encode_access_token
from app.services.auth_service import login_teacher, login_student, logout_user
from app.models.user import User

logger = logging.getLogger("smartgrader.routes.auth")
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    """Teacher login with email and password."""
    data = request.get_json()
    email = data.get("email", "")
    password = data.get("password", "")

    user = login_teacher(email, password)

    response = make_response(jsonify({"user": user.to_dict()}))
    set_auth_cookies(response, user)
    return response


@auth_bp.route("/auth/scan", methods=["POST"])
def scan_login():
    """Student login via barcode scan (matricule)."""
    data = request.get_json()
    matricule = data.get("matricule", "")

    user = login_student(matricule)

    response = make_response(jsonify({"user": user.to_dict()}))
    set_auth_cookies(response, user)
    return response


@auth_bp.route("/auth/refresh", methods=["POST"])
def refresh():
    """Refresh access token using refresh cookie."""
    token = request.cookies.get("refresh_token")
    if not token:
        return jsonify({"error": "Refresh token required"}), 401

    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        return jsonify({"error": "Invalid refresh token"}), 401

    user = User.query.get(payload["sub"])
    if not user or not user.is_active:
        return jsonify({"error": "User not found or disabled"}), 401
    if user.token_version != payload.get("ver"):
        return jsonify({"error": "Session expired"}), 401

    access_token = encode_access_token(user)

    from flask import current_app
    is_prod = not current_app.config.get("DEBUG", False)

    response = make_response(jsonify({"message": "Token refreshed"}))
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=is_prod,
        samesite="Lax",
        max_age=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
        path="/",
    )
    return response


@auth_bp.route("/auth/logout", methods=["POST"])
@require_auth
def logout():
    """Log out the current user (invalidate tokens)."""
    from flask import g
    logout_user(g.current_user.id)

    response = make_response(jsonify({"message": "Logged out"}))
    clear_auth_cookies(response)
    return response


@auth_bp.route("/auth/me", methods=["GET"])
@require_auth
def me():
    """Get current authenticated user info."""
    from flask import g
    return jsonify({"user": g.current_user.to_dict()})
```

- [ ] **Step 4: Register the auth blueprint**

Add to `app/routes/__init__.py`, inside `register_blueprints(app)`:

```python
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api")
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_routes/test_auth.py -v`
Expected: all 10 tests PASS

- [ ] **Step 6: Run full test suite**

Run: `pytest tests/ -v --tb=short`
Expected: all tests pass

- [ ] **Step 7: Commit**

```bash
git add app/routes/auth.py app/routes/__init__.py tests/test_routes/test_auth.py
git commit -m "feat(auth): add auth routes — login, scan, refresh, logout, me"
```

---

## Task 6: Admin Routes & CSV Import

**Files:**
- Create: `app/services/import_service.py`
- Create: `app/routes/admin.py`
- Modify: `app/routes/__init__.py`
- Create: `tests/test_services/test_import_service.py`
- Create: `tests/test_routes/test_admin.py`

- [ ] **Step 1: Write import service tests**

Create `tests/test_services/test_import_service.py`:

```python
"""Tests for CSV student import service."""

import io
from app.models.student import Student
from app.models.user import User
from app.services.import_service import import_students_csv


def test_import_valid_csv(db):
    csv_content = "name,matricule,email\nAli,001,ali@univ.dz\nFatima,002,fatima@univ.dz\n"
    file = io.BytesIO(csv_content.encode("utf-8"))

    result = import_students_csv(file)

    assert result["created"] == 2
    assert result["skipped"] == 0
    assert result["errors"] == []

    assert Student.query.count() == 2
    assert User.query.filter_by(role="student").count() == 2


def test_import_skip_duplicate_matricule(db):
    student = Student(name="Existing", matricule="001")
    db.session.add(student)
    db.session.commit()

    csv_content = "name,matricule,email\nAli,001,ali@univ.dz\nFatima,002,fatima@univ.dz\n"
    file = io.BytesIO(csv_content.encode("utf-8"))

    result = import_students_csv(file)

    assert result["created"] == 1
    assert result["skipped"] == 1


def test_import_missing_required_fields(db):
    csv_content = "name,matricule,email\n,001,ali@univ.dz\nFatima,,fatima@univ.dz\n"
    file = io.BytesIO(csv_content.encode("utf-8"))

    result = import_students_csv(file)

    assert result["created"] == 0
    assert len(result["errors"]) == 2


def test_import_empty_csv(db):
    csv_content = "name,matricule,email\n"
    file = io.BytesIO(csv_content.encode("utf-8"))

    result = import_students_csv(file)

    assert result["created"] == 0
    assert result["skipped"] == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_services/test_import_service.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Create import service**

Create `app/services/import_service.py`:

```python
"""CSV student import service."""

import csv
import io
import logging

from app.models import db
from app.models.student import Student
from app.models.user import User

logger = logging.getLogger("smartgrader.services.import")


def import_students_csv(file):
    """Import students from a CSV file, creating Student + User records.

    Args:
        file: File-like object containing CSV data with columns: name, matricule, email.

    Returns:
        Dict with keys: created (int), skipped (int), errors (list of dicts).
    """
    content = file.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8")

    reader = csv.DictReader(io.StringIO(content))

    created = 0
    skipped = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):
        name = (row.get("name") or "").strip()
        matricule = (row.get("matricule") or "").strip()
        email = (row.get("email") or "").strip()

        if not name or not matricule:
            errors.append({"row": row_num, "message": "Name and matricule are required"})
            continue

        existing = Student.query.filter_by(matricule=matricule).first()
        if existing:
            skipped += 1
            continue

        student = Student(name=name, matricule=matricule, email=email or None)
        db.session.add(student)
        db.session.flush()

        user = User(role="student", student_id=student.id)
        db.session.add(user)

        created += 1

    db.session.commit()

    logger.info("CSV import complete: created=%d, skipped=%d, errors=%d", created, skipped, len(errors))
    return {"created": created, "skipped": skipped, "errors": errors}
```

- [ ] **Step 4: Run import service tests**

Run: `pytest tests/test_services/test_import_service.py -v`
Expected: all 4 tests PASS

- [ ] **Step 5: Write admin route tests**

Create `tests/test_routes/test_admin.py`:

```python
"""Tests for admin API routes."""

import io
import json
from app.services.auth_service import create_teacher


def _login_admin(client, db):
    """Create an admin and log in, returning the client with auth cookies."""
    create_teacher(email="admin@univ.dz", password="adminpass1", name="Admin", is_admin=True)
    client.post(
        "/api/auth/login",
        data=json.dumps({"email": "admin@univ.dz", "password": "adminpass1"}),
        content_type="application/json",
    )
    return client


def _login_teacher(client, db):
    """Create a non-admin teacher and log in."""
    create_teacher(email="teacher@univ.dz", password="teachpass1", name="Teacher")
    client.post(
        "/api/auth/login",
        data=json.dumps({"email": "teacher@univ.dz", "password": "teachpass1"}),
        content_type="application/json",
    )
    return client


def test_create_teacher_as_admin(client, db):
    _login_admin(client, db)
    response = client.post(
        "/api/admin/teachers",
        data=json.dumps({"email": "new@univ.dz", "password": "newpass12", "name": "New Prof"}),
        content_type="application/json",
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["email"] == "new@univ.dz"


def test_create_teacher_as_non_admin(client, db):
    _login_teacher(client, db)
    response = client.post(
        "/api/admin/teachers",
        data=json.dumps({"email": "x@x.dz", "password": "password1", "name": "X"}),
        content_type="application/json",
    )
    assert response.status_code == 403


def test_create_teacher_unauthenticated(client):
    response = client.post(
        "/api/admin/teachers",
        data=json.dumps({"email": "x@x.dz", "password": "password1", "name": "X"}),
        content_type="application/json",
    )
    assert response.status_code == 401


def test_list_teachers(client, db):
    _login_admin(client, db)
    client.post(
        "/api/admin/teachers",
        data=json.dumps({"email": "t2@univ.dz", "password": "password12", "name": "T2"}),
        content_type="application/json",
    )
    response = client.get("/api/admin/teachers")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) >= 2  # admin + new teacher


def test_deactivate_teacher(client, db):
    _login_admin(client, db)
    resp = client.post(
        "/api/admin/teachers",
        data=json.dumps({"email": "del@univ.dz", "password": "password12", "name": "Del"}),
        content_type="application/json",
    )
    teacher_id = json.loads(resp.data)["id"]

    response = client.delete(f"/api/admin/teachers/{teacher_id}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["is_active"] is False


def test_csv_import_as_admin(client, db):
    _login_admin(client, db)

    csv_content = "name,matricule,email\nAli,001,ali@univ.dz\nFatima,002,fatima@univ.dz\n"
    data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "students.csv")}

    response = client.post(
        "/api/admin/students/import",
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result["created"] == 2


def test_csv_import_as_non_admin(client, db):
    _login_teacher(client, db)

    csv_content = "name,matricule,email\nAli,001,ali@univ.dz\n"
    data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "students.csv")}

    response = client.post(
        "/api/admin/students/import",
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 403
```

- [ ] **Step 6: Create admin routes blueprint**

Create `app/routes/admin.py`:

```python
"""Admin API endpoints."""

import logging
from flask import Blueprint, request, jsonify

from app.auth import require_auth, require_admin
from app.services.auth_service import create_teacher
from app.services.import_service import import_students_csv
from app.models.user import User

logger = logging.getLogger("smartgrader.routes.admin")
admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/teachers", methods=["POST"])
@require_auth
@require_admin
def create_teacher_account():
    """Create a new teacher account (admin only)."""
    data = request.get_json()
    user = create_teacher(
        email=data.get("email"),
        password=data.get("password"),
        name=data.get("name"),
        is_admin=data.get("is_admin", False),
    )
    return jsonify(user.to_dict()), 201


@admin_bp.route("/admin/teachers", methods=["GET"])
@require_auth
@require_admin
def list_teachers():
    """List all teacher accounts (admin only)."""
    teachers = User.query.filter_by(role="teacher").all()
    return jsonify([t.to_dict() for t in teachers])


@admin_bp.route("/admin/teachers/<int:user_id>", methods=["DELETE"])
@require_auth
@require_admin
def deactivate_teacher(user_id):
    """Deactivate a teacher account (admin only)."""
    from app.models import db

    user = User.query.get(user_id)
    if not user or user.role != "teacher":
        return jsonify({"error": "Teacher not found"}), 404

    user.is_active = False
    user.token_version += 1  # force logout
    db.session.commit()

    logger.info("Deactivated teacher: %s", user.email)
    return jsonify(user.to_dict())


@admin_bp.route("/admin/students/import", methods=["POST"])
@require_auth
@require_admin
def import_students():
    """Import students from CSV file (admin only)."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename.endswith(".csv"):
        return jsonify({"error": "File must be a CSV"}), 400

    result = import_students_csv(file)
    return jsonify(result)
```

- [ ] **Step 7: Register admin blueprint**

Add to `app/routes/__init__.py`, inside `register_blueprints(app)`:

```python
    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/api")
```

- [ ] **Step 8: Run all admin and import tests**

Run: `pytest tests/test_services/test_import_service.py tests/test_routes/test_admin.py -v`
Expected: all 12 tests PASS

- [ ] **Step 9: Run full test suite**

Run: `pytest tests/ -v --tb=short`
Expected: all tests pass

- [ ] **Step 10: Commit**

```bash
git add app/services/import_service.py app/routes/admin.py app/routes/__init__.py tests/test_services/test_import_service.py tests/test_routes/test_admin.py
git commit -m "feat(auth): add admin routes — teacher CRUD, CSV student import"
```

---

## Task 7: Protect Existing Routes

**Files:**
- Modify: `app/routes/exams.py`
- Modify: `app/routes/students.py`
- Modify: `app/routes/questions.py`
- Modify: `app/routes/scanning.py`
- Modify: `app/routes/grading.py`
- Modify: `app/routes/ai.py`
- Modify: `tests/conftest.py`
- Modify: `tests/test_routes/test_exams.py`

- [ ] **Step 1: Add auth helper fixture to conftest.py**

Add to `tests/conftest.py`:

```python
import json
from app.services.auth_service import create_teacher


@pytest.fixture
def auth_client(client, db):
    """Provide an authenticated test client (teacher role)."""
    create_teacher(email="test@univ.dz", password="testpass1", name="Test Teacher")
    client.post(
        "/api/auth/login",
        data=json.dumps({"email": "test@univ.dz", "password": "testpass1"}),
        content_type="application/json",
    )
    return client
```

Also add `import json` and the `from app.services.auth_service import create_teacher` at the top of conftest.py.

- [ ] **Step 2: Add decorators to exams.py**

Add imports at the top of `app/routes/exams.py`:

```python
from app.auth import require_auth, require_role
```

Add `@require_auth` and `@require_role("teacher")` decorators to each route function, like this:

```python
@exams_bp.route("/exams", methods=["GET"])
@require_auth
@require_role("teacher")
def list_exams():
    ...
```

Apply the same two decorators to: `list_exams`, `create`, `get_exam`, `update`, `delete`.

- [ ] **Step 3: Add decorators to students.py, questions.py, scanning.py, grading.py, ai.py**

For each file, add the same imports and decorators:

```python
from app.auth import require_auth, require_role
```

Add `@require_auth` and `@require_role("teacher")` to every route function in each file.

- [ ] **Step 4: Update existing route tests to use auth_client**

In `tests/test_routes/test_exams.py`, change every `client` parameter to `auth_client`. For example:

```python
def test_create_exam(auth_client):
    response = auth_client.post(
        "/api/exams",
        data=json.dumps({"title": "Math", "subject": "Science", "total_marks": 100}),
        content_type="application/json",
    )
    assert response.status_code == 201
```

Do this for all test functions that use `client` in `test_exams.py`. Keep `test_health_check` using `client` (health check stays public).

- [ ] **Step 5: Add tests for unauthenticated access**

Add to `tests/test_routes/test_exams.py`:

```python
def test_list_exams_unauthenticated(client):
    response = client.get("/api/exams")
    assert response.status_code == 401


def test_create_exam_unauthenticated(client):
    response = client.post(
        "/api/exams",
        data=json.dumps({"title": "X"}),
        content_type="application/json",
    )
    assert response.status_code == 401
```

- [ ] **Step 6: Run full test suite**

Run: `pytest tests/ -v --tb=short`
Expected: all tests pass (existing tests now use auth_client, new tests verify 401)

- [ ] **Step 7: Commit**

```bash
git add app/routes/exams.py app/routes/students.py app/routes/questions.py app/routes/scanning.py app/routes/grading.py app/routes/ai.py tests/conftest.py tests/test_routes/test_exams.py
git commit -m "feat(auth): protect existing routes with @require_auth @require_role"
```

---

## Task 8: Initialize Flask-Limiter in App Factory

**Files:**
- Modify: `app/__init__.py`

- [ ] **Step 1: Add Flask-Limiter initialization**

In `app/__init__.py`, add the import at the top:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
```

After `migrate = Migrate()` (line 14), add:

```python
limiter = Limiter(key_func=get_remote_address)
```

Inside `create_app()`, after `CORS(app)` (line 37), add:

```python
    limiter.init_app(app)
```

- [ ] **Step 2: Apply rate limiting to login routes**

In `app/routes/auth.py`, add at the top:

```python
from app import limiter
```

Add the rate limit decorator to the login and scan routes:

```python
@auth_bp.route("/auth/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    ...

@auth_bp.route("/auth/scan", methods=["POST"])
@limiter.limit("5 per minute")
def scan_login():
    ...
```

- [ ] **Step 3: Verify the app starts**

Run: `python -c "from app import create_app; app = create_app('testing'); print('OK')"`
Expected: `OK`

- [ ] **Step 4: Run full test suite**

Run: `pytest tests/ -v --tb=short`
Expected: all tests pass

- [ ] **Step 5: Commit**

```bash
git add app/__init__.py app/routes/auth.py
git commit -m "feat(auth): add Flask-Limiter rate limiting on login endpoints"
```

---

## Task 9: Create Admin CLI Script

**Files:**
- Create: `scripts/create_admin.py`

- [ ] **Step 1: Create the script**

Create `scripts/create_admin.py`:

```python
"""CLI script to create the initial admin account.

Usage:
    python -m scripts.create_admin --email admin@school.dz --password yourpassword
"""

import argparse
import sys

from app import create_app
from app.models.user import User
from app.services.auth_service import create_teacher


def main():
    parser = argparse.ArgumentParser(description="Create the initial admin account")
    parser.add_argument("--email", required=True, help="Admin email address")
    parser.add_argument("--password", required=True, help="Admin password (min 8 chars)")
    parser.add_argument("--name", default="Admin", help="Admin display name")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        existing = User.query.filter_by(is_admin=True).first()
        if existing:
            print(f"Error: Admin already exists ({existing.email}). Aborting.")
            sys.exit(1)

        user = create_teacher(
            email=args.email,
            password=args.password,
            name=args.name,
            is_admin=True,
        )
        print(f"Admin account created: {user.email} (id={user.id})")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify script runs with --help**

Run: `python -m scripts.create_admin --help`
Expected: shows usage with `--email` and `--password` args

- [ ] **Step 3: Commit**

```bash
git add scripts/create_admin.py
git commit -m "feat(auth): add CLI script to create initial admin account"
```

---

## Task 10: Database Migration

- [ ] **Step 1: Generate migration**

Run: `flask db migrate -m "add users table for authentication"`

Expected: a new migration file in `migrations/versions/`

- [ ] **Step 2: Apply migration**

Run: `flask db upgrade`

Expected: `users` table created in `instance/smart_grader.db`

- [ ] **Step 3: Verify table exists**

Run: `python -c "from app import create_app; from app.models.user import User; app = create_app(); ctx = app.app_context(); ctx.push(); print(User.query.count())"`
Expected: `0`

- [ ] **Step 4: Commit migration**

```bash
git add migrations/
git commit -m "feat(auth): add database migration for users table"
```

---

## Task 11: Frontend — Install html5-qrcode & Update API Layer

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/src/lib/api.js`

- [ ] **Step 1: Install html5-qrcode**

Run: `cd frontend && npm install html5-qrcode`

- [ ] **Step 2: Update api.js for credentials and 401 handling**

Replace the content of `frontend/src/lib/api.js` with:

```javascript
const API_BASE = "/api";

let isRefreshing = false;
let refreshPromise = null;

async function refreshToken() {
  if (isRefreshing) return refreshPromise;
  isRefreshing = true;
  refreshPromise = fetch(`${API_BASE}/auth/refresh`, {
    method: "POST",
    credentials: "same-origin",
  }).then((res) => {
    isRefreshing = false;
    return res.ok;
  }).catch(() => {
    isRefreshing = false;
    return false;
  });
  return refreshPromise;
}

export async function fetchAPI(path, options = {}) {
  const { body, headers: customHeaders, ...rest } = options;

  const headers = { ...customHeaders };
  if (body && typeof body === "string") {
    headers["Content-Type"] = "application/json";
  }

  let response = await fetch(`${API_BASE}${path}`, {
    headers,
    body,
    credentials: "same-origin",
    ...rest,
  });

  // Auto-refresh on 401 (except for auth endpoints)
  if (response.status === 401 && !path.startsWith("/auth/")) {
    const refreshed = await refreshToken();
    if (refreshed) {
      response = await fetch(`${API_BASE}${path}`, {
        headers,
        body,
        credentials: "same-origin",
        ...rest,
      });
    }
  }

  if (!response.ok) {
    let errorMessage = "Request failed";
    try {
      const error = await response.json();
      errorMessage = error.error || errorMessage;
    } catch {}
    const err = new Error(errorMessage);
    err.status = response.status;
    throw err;
  }

  return response.json();
}

export function uploadFile(path, formData) {
  return fetch(`${API_BASE}${path}`, {
    method: "POST",
    body: formData,
    credentials: "same-origin",
  }).then(async (res) => {
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.error || "Upload failed");
    }
    return res.json();
  });
}
```

- [ ] **Step 3: Commit**

```bash
cd frontend && git add package.json package-lock.json src/lib/api.js
git commit -m "feat(auth): add html5-qrcode dependency, update API layer with auth support"
```

---

## Task 12: Frontend — AuthContext & ProtectedRoute

**Files:**
- Create: `frontend/src/contexts/AuthContext.jsx`
- Create: `frontend/src/components/ProtectedRoute.jsx`
- Create: `frontend/src/hooks/use-auth.js`
- Modify: `frontend/src/main.jsx`

- [ ] **Step 1: Create AuthContext**

Create `frontend/src/contexts/AuthContext.jsx`:

```jsx
import { createContext, useState, useEffect, useCallback } from "react";
import { fetchAPI } from "@/lib/api";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAPI("/auth/me")
      .then((data) => setUser(data.user))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  const loginTeacher = useCallback(async (email, password) => {
    const data = await fetchAPI("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setUser(data.user);
    return data.user;
  }, []);

  const loginStudent = useCallback(async (matricule) => {
    const data = await fetchAPI("/auth/scan", {
      method: "POST",
      body: JSON.stringify({ matricule }),
    });
    setUser(data.user);
    return data.user;
  }, []);

  const logout = useCallback(async () => {
    try {
      await fetchAPI("/auth/logout", { method: "POST" });
    } catch {}
    setUser(null);
  }, []);

  const value = {
    user,
    loading,
    loginTeacher,
    loginStudent,
    logout,
    isAuthenticated: !!user,
    isTeacher: user?.role === "teacher",
    isAdmin: !!user?.is_admin,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
```

- [ ] **Step 2: Create use-auth hook**

Create `frontend/src/hooks/use-auth.js`:

```javascript
import { useContext } from "react";
import { AuthContext } from "@/contexts/AuthContext";

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
```

- [ ] **Step 3: Create ProtectedRoute**

Create `frontend/src/components/ProtectedRoute.jsx`:

```jsx
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/hooks/use-auth";

export default function ProtectedRoute({ role, requireAdmin }) {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (role && user.role !== role) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-destructive text-lg">403 — Access Denied</div>
      </div>
    );
  }

  if (requireAdmin && !user.is_admin) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-destructive text-lg">403 — Admin Access Required</div>
      </div>
    );
  }

  return <Outlet />;
}
```

- [ ] **Step 4: Wrap app with AuthProvider**

Modify `frontend/src/main.jsx` — add the AuthProvider import and wrap:

```jsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./lib/query-client";
import { AuthProvider } from "./contexts/AuthContext";
import App from "./App";
import "./index.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>
);
```

- [ ] **Step 5: Commit**

```bash
cd frontend && git add src/contexts/AuthContext.jsx src/components/ProtectedRoute.jsx src/hooks/use-auth.js src/main.jsx
git commit -m "feat(auth): add AuthContext, ProtectedRoute, useAuth hook"
```

---

## Task 13: Frontend — Login Page with Barcode Scanner

**Files:**
- Create: `frontend/src/components/BarcodeScanner.jsx`
- Create: `frontend/src/pages/LoginPage.jsx`

- [ ] **Step 1: Create BarcodeScanner component**

Create `frontend/src/components/BarcodeScanner.jsx`:

```jsx
import { useEffect, useRef, useState } from "react";
import { Html5Qrcode } from "html5-qrcode";

export default function BarcodeScanner({ onScan, onError }) {
  const [isScanning, setIsScanning] = useState(false);
  const scannerRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    return () => {
      if (scannerRef.current && isScanning) {
        scannerRef.current.stop().catch(() => {});
      }
    };
  }, [isScanning]);

  const startScanning = async () => {
    try {
      const scanner = new Html5Qrcode("barcode-reader");
      scannerRef.current = scanner;

      await scanner.start(
        { facingMode: "environment" },
        {
          fps: 10,
          qrbox: { width: 250, height: 150 },
        },
        (decodedText) => {
          scanner.stop().then(() => {
            setIsScanning(false);
            onScan(decodedText);
          });
        },
        () => {} // ignore scan failures (no barcode in frame yet)
      );

      setIsScanning(true);
    } catch (err) {
      onError?.(err.message || "Camera access denied");
    }
  };

  const stopScanning = () => {
    if (scannerRef.current) {
      scannerRef.current.stop().then(() => setIsScanning(false));
    }
  };

  return (
    <div className="space-y-4">
      <div
        id="barcode-reader"
        ref={containerRef}
        className="w-full rounded-lg overflow-hidden border border-border bg-muted"
        style={{ minHeight: isScanning ? 250 : 0 }}
      />
      {!isScanning ? (
        <button
          type="button"
          onClick={startScanning}
          className="w-full rounded-lg bg-primary px-4 py-3 text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
        >
          Start Camera Scan
        </button>
      ) : (
        <button
          type="button"
          onClick={stopScanning}
          className="w-full rounded-lg bg-destructive px-4 py-3 text-destructive-foreground font-medium hover:bg-destructive/90 transition-colors"
        >
          Stop Camera
        </button>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Create LoginPage**

Create `frontend/src/pages/LoginPage.jsx`:

```jsx
import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/use-auth";
import BarcodeScanner from "@/components/BarcodeScanner";

export default function LoginPage() {
  const [tab, setTab] = useState("teacher");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [matricule, setMatricule] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { loginTeacher, loginStudent, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const matriculeRef = useRef(null);

  // Redirect if already logged in
  useEffect(() => {
    if (isAuthenticated) {
      navigate(user?.role === "teacher" ? "/" : "/exam", { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

  // USB scanner detection: rapid keystrokes
  const keystrokeBuffer = useRef("");
  const keystrokeTimer = useRef(null);

  useEffect(() => {
    if (tab !== "student") return;

    const handleKeyDown = (e) => {
      if (document.activeElement !== matriculeRef.current) return;
      if (e.key === "Enter" && keystrokeBuffer.current.length > 3) {
        e.preventDefault();
        setMatricule(keystrokeBuffer.current);
        handleStudentLogin(keystrokeBuffer.current);
        keystrokeBuffer.current = "";
        return;
      }
      if (e.key.length === 1) {
        keystrokeBuffer.current += e.key;
        clearTimeout(keystrokeTimer.current);
        keystrokeTimer.current = setTimeout(() => {
          keystrokeBuffer.current = "";
        }, 100);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [tab]);

  const handleTeacherLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await loginTeacher(email, password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStudentLogin = async (mat) => {
    const value = mat || matricule;
    if (!value.trim()) return;
    setError("");
    setLoading(true);
    try {
      await loginStudent(value.trim());
      navigate("/exam", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold">SmartGrader</h1>
          <p className="text-muted-foreground mt-1">Sign in to continue</p>
        </div>

        {/* Tab switcher */}
        <div className="flex rounded-lg bg-muted p-1">
          <button
            className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              tab === "teacher"
                ? "bg-background shadow text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
            onClick={() => { setTab("teacher"); setError(""); }}
          >
            Teacher
          </button>
          <button
            className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              tab === "student"
                ? "bg-background shadow text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
            onClick={() => { setTab("student"); setError(""); }}
          >
            Student
          </button>
        </div>

        {error && (
          <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
            {error}
          </div>
        )}

        {/* Teacher login form */}
        {tab === "teacher" && (
          <form onSubmit={handleTeacherLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
                placeholder="teacher@university.dz"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
                placeholder="Enter your password"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading || !email || !password}
              className="w-full rounded-lg bg-primary px-4 py-2 text-primary-foreground font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>
        )}

        {/* Student login: barcode scanner + manual */}
        {tab === "student" && (
          <div className="space-y-4">
            <BarcodeScanner
              onScan={(code) => handleStudentLogin(code)}
              onError={(msg) => setError(msg)}
            />

            <div className="flex items-center gap-3">
              <div className="h-px flex-1 bg-border" />
              <span className="text-xs text-muted-foreground">or enter manually</span>
              <div className="h-px flex-1 bg-border" />
            </div>

            <form onSubmit={(e) => { e.preventDefault(); handleStudentLogin(); }} className="space-y-4">
              <input
                ref={matriculeRef}
                type="text"
                value={matricule}
                onChange={(e) => setMatricule(e.target.value)}
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
                placeholder="Matricule number"
                autoFocus
              />
              <button
                type="submit"
                disabled={loading || !matricule.trim()}
                className="w-full rounded-lg bg-primary px-4 py-2 text-primary-foreground font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
              >
                {loading ? "Signing in..." : "Login"}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
cd frontend && git add src/components/BarcodeScanner.jsx src/pages/LoginPage.jsx
git commit -m "feat(auth): add LoginPage with teacher form and barcode scanner"
```

---

## Task 14: Frontend — Admin Pages (Teacher Management & Student Import)

**Files:**
- Create: `frontend/src/pages/TeacherManagement.jsx`
- Create: `frontend/src/pages/StudentImport.jsx`

- [ ] **Step 1: Create TeacherManagement page**

Create `frontend/src/pages/TeacherManagement.jsx`:

```jsx
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAPI } from "@/lib/api";

export default function TeacherManagement() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", password: "" });

  const { data: teachers = [], isLoading } = useQuery({
    queryKey: ["admin", "teachers"],
    queryFn: () => fetchAPI("/admin/teachers"),
  });

  const createMutation = useMutation({
    mutationFn: (data) =>
      fetchAPI("/admin/teachers", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "teachers"] });
      setForm({ name: "", email: "", password: "" });
      setShowForm(false);
    },
  });

  const deactivateMutation = useMutation({
    mutationFn: (id) => fetchAPI(`/admin/teachers/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "teachers"] }),
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    createMutation.mutate(form);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Teacher Management</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
        >
          {showForm ? "Cancel" : "Add Teacher"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="rounded-lg border border-border p-4 space-y-3">
          <input
            type="text"
            placeholder="Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
            required
          />
          <input
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
            required
          />
          <input
            type="password"
            placeholder="Password (min 8 characters)"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
            required
            minLength={8}
          />
          {createMutation.isError && (
            <p className="text-sm text-destructive">{createMutation.error.message}</p>
          )}
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {createMutation.isPending ? "Creating..." : "Create Teacher"}
          </button>
        </form>
      )}

      {isLoading ? (
        <p className="text-muted-foreground">Loading teachers...</p>
      ) : (
        <div className="space-y-2">
          {teachers.map((teacher) => (
            <div
              key={teacher.id}
              className="flex items-center justify-between rounded-lg border border-border p-4"
            >
              <div>
                <div className="font-medium">{teacher.name}</div>
                <div className="text-sm text-muted-foreground">{teacher.email}</div>
                <div className="flex gap-2 mt-1">
                  {teacher.is_admin && (
                    <span className="text-xs rounded bg-primary/10 text-primary px-2 py-0.5">Admin</span>
                  )}
                  {!teacher.is_active && (
                    <span className="text-xs rounded bg-destructive/10 text-destructive px-2 py-0.5">Disabled</span>
                  )}
                </div>
              </div>
              {teacher.is_active && !teacher.is_admin && (
                <button
                  onClick={() => deactivateMutation.mutate(teacher.id)}
                  className="text-sm text-destructive hover:underline"
                >
                  Deactivate
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Create StudentImport page**

Create `frontend/src/pages/StudentImport.jsx`:

```jsx
import { useState, useRef } from "react";
import { uploadFile } from "@/lib/api";

export default function StudentImport() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);
  const fileRef = useRef(null);

  const handleFile = (file) => {
    if (!file || !file.name.endsWith(".csv")) {
      setError("Please select a CSV file");
      return;
    }
    setError("");
    setResult(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      const lines = text.trim().split("\n");
      const headers = lines[0].split(",").map((h) => h.trim());
      const rows = lines.slice(1, 6).map((line) =>
        line.split(",").map((cell) => cell.trim())
      );
      setPreview({ headers, rows, total: lines.length - 1 });
    };
    reader.readAsText(file);
  };

  const handleUpload = async () => {
    const file = fileRef.current?.files[0];
    if (!file) return;

    setLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const data = await uploadFile("/admin/students/import", formData);
      setResult(data);
      setPreview(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Import Students (CSV)</h1>

      <div className="rounded-lg border border-dashed border-border p-8 text-center">
        <input
          ref={fileRef}
          type="file"
          accept=".csv"
          onChange={(e) => handleFile(e.target.files[0])}
          className="hidden"
          id="csv-upload"
        />
        <label htmlFor="csv-upload" className="cursor-pointer">
          <div className="text-muted-foreground">
            <p className="text-lg font-medium">Click to select CSV file</p>
            <p className="text-sm mt-1">Expected columns: name, matricule, email</p>
          </div>
        </label>
      </div>

      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {preview && (
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">
            Preview ({preview.total} rows total, showing first 5):
          </p>
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-muted">
                  {preview.headers.map((h, i) => (
                    <th key={i} className="px-4 py-2 text-left font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.rows.map((row, i) => (
                  <tr key={i} className="border-t border-border">
                    {row.map((cell, j) => (
                      <td key={j} className="px-4 py-2">{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <button
            onClick={handleUpload}
            disabled={loading}
            className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {loading ? "Importing..." : `Import ${preview.total} students`}
          </button>
        </div>
      )}

      {result && (
        <div className="rounded-lg border border-border p-4 space-y-2">
          <h3 className="font-medium">Import Complete</h3>
          <div className="text-sm space-y-1">
            <p className="text-green-500">Created: {result.created}</p>
            <p className="text-yellow-500">Skipped (duplicates): {result.skipped}</p>
            {result.errors.length > 0 && (
              <div>
                <p className="text-destructive">Errors: {result.errors.length}</p>
                <ul className="list-disc list-inside text-destructive mt-1">
                  {result.errors.map((err, i) => (
                    <li key={i}>Row {err.row}: {err.message}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
cd frontend && git add src/pages/TeacherManagement.jsx src/pages/StudentImport.jsx
git commit -m "feat(auth): add TeacherManagement and StudentImport admin pages"
```

---

## Task 15: Frontend — Update App.jsx with Routes & Navigation

**Files:**
- Modify: `frontend/src/App.jsx`

- [ ] **Step 1: Update App.jsx with auth routes**

Replace `frontend/src/App.jsx` with:

```jsx
import { Routes, Route } from "react-router-dom";
import AppLayout from "@/components/layout/AppLayout";
import ProtectedRoute from "@/components/ProtectedRoute";
import LoginPage from "@/pages/LoginPage";
import Dashboard from "@/pages/Dashboard";
import Exams from "@/pages/Exams";
import ExamDetail from "@/pages/ExamDetail";
import Scanner from "@/pages/Scanner";
import Students from "@/pages/Students";
import Results from "@/pages/Results";
import Settings from "@/pages/Settings";
import Documentation from "@/pages/Documentation";
import AcademicDocs from "@/pages/AcademicDocs";
import AIConfig from "@/pages/AIConfig";
import SampleData from "@/pages/SampleData";
import LegacyCode from "@/pages/LegacyCode";
import Help from "@/pages/Help";
import TeacherManagement from "@/pages/TeacherManagement";
import StudentImport from "@/pages/StudentImport";

export default function App() {
  return (
    <Routes>
      {/* Public route */}
      <Route path="/login" element={<LoginPage />} />

      {/* Teacher routes */}
      <Route element={<ProtectedRoute role="teacher" />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/exams" element={<Exams />} />
          <Route path="/exams/:id" element={<ExamDetail />} />
          <Route path="/scanner" element={<Scanner />} />
          <Route path="/students" element={<Students />} />
          <Route path="/results" element={<Results />} />
          <Route path="/documentation" element={<Documentation />} />
          <Route path="/academic-docs" element={<AcademicDocs />} />
          <Route path="/samples" element={<SampleData />} />
          <Route path="/legacy" element={<LegacyCode />} />
          <Route path="/ai-config" element={<AIConfig />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/help" element={<Help />} />
        </Route>
      </Route>

      {/* Admin routes */}
      <Route element={<ProtectedRoute role="teacher" requireAdmin />}>
        <Route element={<AppLayout />}>
          <Route path="/admin/teachers" element={<TeacherManagement />} />
          <Route path="/admin/import" element={<StudentImport />} />
        </Route>
      </Route>
    </Routes>
  );
}
```

- [ ] **Step 2: Verify frontend builds**

Run: `cd frontend && npm run build`
Expected: build succeeds with no errors

- [ ] **Step 3: Commit**

```bash
cd frontend && git add src/App.jsx
git commit -m "feat(auth): update routing with login, protected routes, admin pages"
```

---

## Task 16: Add Logout & Admin Navigation to AppLayout

**Files:**
- Modify: `frontend/src/components/layout/AppLayout.jsx` (or whatever the sidebar/nav component is)

- [ ] **Step 1: Find and read the AppLayout component**

Run: find the AppLayout file and read it. It should be in `frontend/src/components/layout/AppLayout.jsx`.

- [ ] **Step 2: Add auth-aware navigation**

Add to the sidebar/navigation:
- Show current user name/email at the bottom
- Add a Logout button
- If user is admin, show "Teachers" and "Import Students" links under an Admin section

Import `useAuth`:
```jsx
import { useAuth } from "@/hooks/use-auth";
import { useNavigate } from "react-router-dom";
```

Inside the component:
```jsx
const { user, logout, isAdmin } = useAuth();
const navigate = useNavigate();

const handleLogout = async () => {
  await logout();
  navigate("/login", { replace: true });
};
```

Add to the sidebar JSX (admin section):
```jsx
{isAdmin && (
  <>
    <SidebarGroupLabel>Admin</SidebarGroupLabel>
    <NavLink to="/admin/teachers">Teachers</NavLink>
    <NavLink to="/admin/import">Import Students</NavLink>
  </>
)}
```

Add at the bottom of the sidebar:
```jsx
<div className="border-t border-border p-4">
  <div className="text-sm font-medium">{user?.name}</div>
  <div className="text-xs text-muted-foreground">{user?.email}</div>
  <button
    onClick={handleLogout}
    className="mt-2 text-sm text-destructive hover:underline"
  >
    Sign out
  </button>
</div>
```

Note: The exact implementation depends on the current AppLayout structure. Read the file first and adapt the additions to match the existing pattern.

- [ ] **Step 3: Verify frontend builds**

Run: `cd frontend && npm run build`
Expected: build succeeds

- [ ] **Step 4: Commit**

```bash
cd frontend && git add src/components/layout/
git commit -m "feat(auth): add logout button and admin nav links to sidebar"
```

---

## Task 17: End-to-End Verification

- [ ] **Step 1: Run full backend test suite**

Run: `pytest tests/ -v --tb=short`
Expected: all tests pass (old + new)

- [ ] **Step 2: Run frontend build**

Run: `cd frontend && npm run build`
Expected: build succeeds

- [ ] **Step 3: Manual smoke test**

Start the app:
```bash
python run.py
```

In another terminal, start the frontend:
```bash
cd frontend && npm run dev
```

Test these flows:
1. Visit `http://localhost:5173/` — should redirect to `/login`
2. Create admin: `python -m scripts.create_admin --email admin@test.dz --password password123`
3. Login as teacher at `/login` with admin credentials
4. Navigate existing pages (exams, students, etc.) — should work as before
5. Go to `/admin/teachers` — create a new teacher
6. Go to `/admin/import` — upload a CSV with student data
7. Logout — should redirect to `/login`
8. On student tab, type a matricule from the CSV import — should log in

- [ ] **Step 4: Final commit if any fixes were needed**

```bash
git add -A
git commit -m "fix(auth): address issues found during smoke testing"
```

---

## Summary

| Task | Description | Tests |
|------|-------------|-------|
| 1 | Dependencies & config | - |
| 2 | User model | 7 tests |
| 3 | JWT helpers & decorators | - |
| 4 | Auth service | 12 tests |
| 5 | Auth routes | 10 tests |
| 6 | Admin routes & CSV import | 12 tests |
| 7 | Protect existing routes | 2 new + updated existing |
| 8 | Flask-Limiter | - |
| 9 | Create admin CLI | - |
| 10 | Database migration | - |
| 11 | Frontend API layer | - |
| 12 | AuthContext & ProtectedRoute | - |
| 13 | Login page & barcode scanner | - |
| 14 | Admin pages | - |
| 15 | App.jsx routing | - |
| 16 | Sidebar navigation | - |
| 17 | End-to-end verification | manual |

**Total: 17 tasks, ~43 automated tests, 17 commits**
