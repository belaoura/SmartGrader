# Phase 1: Authentication & Student Login — Design Spec

## Overview

Add authentication to SmartGrader so that teachers log in with email/password and students log in by scanning their barcode card (or typing their matricule). This is the foundation for all subsequent online exam features (Phases 2–4).

## Goals

- Teacher accounts with email + password login, managed by an admin
- Student login via barcode card scan (webcam or USB scanner) with manual matricule fallback
- JWT-based auth with httpOnly cookies, single-session enforcement
- Role-based route protection (teacher, student, admin)
- CSV bulk import for student accounts
- Zero breaking changes to existing models or API contracts

## Non-Goals (deferred to later phases)

- Online exam-taking UI (Phase 2)
- Anti-cheat / proctoring (Phase 3)
- Network deployment / WebSocket (Phase 4)
- 2FA / OAuth
- Student card generation

---

## 1. Data Model

### New Model: User

| Column | Type | Notes |
|--------|------|-------|
| id | Integer, PK | Auto-increment |
| name | String(200) | Teacher display name. NULL for students (name comes from Student model) |
| email | String(200), UNIQUE | Teacher login identifier. NULL for students (SQLite allows multiple NULLs in UNIQUE) |
| password_hash | String(256) | bcrypt hash. NULL for students |
| role | String(20), NOT NULL | "teacher" or "student" |
| is_admin | Boolean, default False | Admin flag on teacher accounts only |
| student_id | Integer, FK → students | Links to existing Student model. NULL for teachers |
| token_version | Integer, default 0 | Bump to invalidate all tokens (single-session) |
| is_active | Boolean, default True | Disable account without deleting |
| created_at | String(30) | ISO timestamp |

File: `app/models/user.py`

### Relationship: User ↔ Student

- A User with `role="student"` has a FK to the existing `Student` model via `student_id`
- A User with `role="teacher"` has `student_id=NULL`
- The existing `Student` model is NOT modified — auth is a separate concern
- One-to-one relationship: each Student has at most one User

### Existing Models — No Changes

Student, Exam, Question, Choice, Result, StudentAnswer, AICorrection — all remain exactly as they are. Existing scanner, grading, and AI flows are unaffected.

---

## 2. API Endpoints

### Auth Endpoints (public)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/auth/login | None | Teacher login (email + password) → sets JWT cookies |
| POST | /api/auth/scan | None | Student login (matricule from barcode) → sets JWT cookies |
| POST | /api/auth/refresh | Refresh token | Get new access token using refresh cookie |
| POST | /api/auth/logout | Access token | Bump token_version, clear cookies |
| GET | /api/auth/me | Access token | Get current user info (role, name, admin status) |

### Admin Endpoints (require is_admin=True)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/admin/teachers | Create teacher account (email, password, name) |
| GET | /api/admin/teachers | List all teacher accounts |
| DELETE | /api/admin/teachers/\<id\> | Deactivate teacher account |
| POST | /api/admin/students/import | CSV upload → bulk create Student + User records |

### Existing Endpoints — Migration

All existing `/api/exams`, `/api/students`, `/api/scan`, `/api/results`, `/api/ai` routes get `@require_auth` + `@require_role("teacher")` decorators added. No API signature changes — just auth required.

### Route Blueprint

File: `app/routes/auth.py` — new blueprint registered at `/api/auth`
File: `app/routes/admin.py` — new blueprint registered at `/api/admin`

---

## 3. Auth Flow

### Teacher Login

1. Teacher enters email + password on `/login` page
2. `POST /api/auth/login` with `{email, password}`
3. Server verifies bcrypt hash against `User.password_hash`
4. Bumps `User.token_version` (invalidates any existing sessions)
5. Creates access JWT (15min TTL) + refresh JWT (7 day TTL)
6. Sets both as httpOnly, secure, sameSite=Lax cookies
7. Returns `{user: {id, email, role, is_admin}}` → frontend redirects to dashboard

### Student Barcode Login

1. Student scans card (webcam/USB scanner) or types matricule
2. `POST /api/auth/scan` with `{matricule}`
3. Server looks up `Student` by matricule
4. Finds linked `User` record via `student_id` FK
5. Bumps `User.token_version` (invalidates any existing sessions)
6. Creates access JWT + refresh JWT
7. Sets cookies → frontend redirects to student view

### Token Refresh

1. Access token expires (15min)
2. Frontend gets 401 on an API call
3. Frontend calls `POST /api/auth/refresh` (refresh cookie sent automatically)
4. Server validates refresh JWT + checks `token_version` matches DB
5. Issues new access JWT, sets new cookie
6. If `token_version` mismatch → 401, forced re-login

### Single-Session Enforcement

- Every login bumps `token_version` by 1
- Every authenticated request checks JWT's `ver` claim matches `User.token_version` in DB
- If another device logs in, `token_version` bumps → old device's JWT `ver` is stale → 401
- Logout also bumps `token_version`, invalidating all tokens instantly

---

## 4. JWT Implementation

### Access Token Payload

```json
{
  "sub": 42,
  "role": "student",
  "ver": 3,
  "type": "access",
  "exp": 1712345678
}
```

Cookie: `access_token`, httpOnly, secure (prod only), sameSite=Lax, path=/

### Refresh Token Payload

```json
{
  "sub": 42,
  "ver": 3,
  "type": "refresh",
  "exp": 1712950478
}
```

Cookie: `refresh_token`, httpOnly, secure (prod only), sameSite=Lax, path=/api/auth/refresh

### Signing

- Algorithm: HS256
- Secret: Flask `SECRET_KEY` from config
- Library: PyJWT

---

## 5. Middleware / Decorators

### @require_auth

- Reads `access_token` from httpOnly cookie
- Decodes JWT, verifies signature and expiry
- Loads `User` from DB by `sub` claim
- Checks `User.token_version` matches JWT `ver` claim
- Checks `User.is_active` is True
- Sets `g.current_user` on the Flask request context
- Returns 401 JSON if any check fails

### @require_role(role_name)

- Must be used after `@require_auth`
- Checks `g.current_user.role == role_name`
- Returns 403 JSON if wrong role

### @require_admin

- Must be used after `@require_auth`
- Checks `g.current_user.is_admin == True`
- Returns 403 JSON if not admin

File: `app/auth.py` (decorators + JWT helpers)

---

## 6. Backend Services

### auth_service.py

| Function | Description |
|----------|-------------|
| `login_teacher(email, password)` | Verify bcrypt hash, bump token_version, return User + generate JWTs |
| `login_student(matricule)` | Lookup Student by matricule, find linked User, bump token_version, return User + generate JWTs |
| `refresh_token(refresh_jwt)` | Validate refresh JWT, check token_version matches DB, issue new access JWT |
| `logout(user_id)` | Bump token_version (invalidates all tokens) |
| `get_current_user(access_jwt)` | Decode JWT, verify token_version, return User |
| `create_teacher(email, password, name, is_admin)` | Hash password with bcrypt, create User with role="teacher" |

File: `app/services/auth_service.py`

### import_service.py

| Function | Description |
|----------|-------------|
| `import_students_csv(file)` | Parse CSV, validate rows, create Student + User per row, skip duplicates, return results |

Expected CSV columns: `name`, `matricule`, `email`

Returns: `{created: N, skipped: N, errors: [{row: N, message: "..."}]}`

File: `app/services/import_service.py`

---

## 7. Frontend Changes

### New Pages

| Route | Component | Access |
|-------|-----------|--------|
| /login | LoginPage | Public |
| /admin/teachers | TeacherManagement | Admin only |
| /admin/import | StudentImport | Admin only |

### LoginPage

Two-tab layout:
- **Teacher tab:** email + password form → `POST /api/auth/login`
- **Student tab:** webcam barcode scanner (camera preview) + manual matricule text input → `POST /api/auth/scan`

### Barcode Scanning (Browser-Side)

**Webcam scanner:**
- Library: `html5-qrcode` (npm)
- Supports QR codes and 1D barcodes (Code128, Code39, EAN, etc.)
- Real-time camera preview in the student login tab
- On successful scan → extract matricule string → auto-submit to `/api/auth/scan`
- No server-side image processing needed — decoding is entirely client-side

**USB barcode scanner:**
- USB scanners act as keyboards — send characters as keystrokes, ending with Enter
- The matricule text input catches this automatically
- Distinguish scanner from typing by keystroke speed (<50ms between characters)

**Manual fallback:**
- Student types matricule into text field and clicks Login
- Same endpoint, same flow

### Auth Context

- `AuthProvider` React context wraps the app
- Calls `GET /api/auth/me` on mount to restore session from cookies
- Provides `user`, `login()`, `logout()`, `isAuthenticated`, `isTeacher`, `isAdmin`
- Automatic token refresh: intercept 401 responses, call `/api/auth/refresh`, retry original request

### Route Protection

- `ProtectedRoute` component wraps routes that require auth
- Checks role from AuthProvider context
- Unauthenticated → redirect to `/login`
- Wrong role → show 403 page

**Route mapping:**
- Public: `/login`, `/api/health`
- Teacher: `/dashboard`, `/exams`, `/students`, `/scanner`, `/results`, `/settings`, `/docs`, `/help`
- Admin: `/admin/teachers`, `/admin/import`
- Student: placeholder routes for Phase 2

---

## 8. Security

### Password Hashing
- bcrypt with default 12 rounds
- Library: `bcrypt` (Python)

### CSRF Protection
- sameSite=Lax cookies prevent cross-origin cookie submission
- API-only backend with JSON content type — no CSRF tokens needed

### Rate Limiting
- Flask-Limiter on login endpoints: 5 attempts per minute per IP
- Prevents brute force on teacher passwords and matricule enumeration

### JWT Security
- httpOnly cookies — JavaScript cannot access tokens (XSS-immune)
- secure flag in production (HTTPS only)
- sameSite=Lax prevents cross-site request forgery
- Short-lived access tokens (15min) limit exposure window
- Refresh token scoped to `/api/auth/refresh` path only

### Input Validation
- Matricule: alphanumeric characters only, sanitized before DB lookup
- Email: format validation
- Password: minimum 8 characters
- CSV rows: validated before insert (required fields, unique matricule check, email format)

### Account Security
- `is_active` flag allows disabling accounts without deletion
- `token_version` bump on every login ensures single-session
- Logout invalidates all tokens instantly

---

## 9. New Dependencies

### Python (requirements.txt)

- `PyJWT>=2.8.0` — JWT encode/decode
- `bcrypt>=4.1.0` — password hashing
- `Flask-Limiter>=3.5.0` — rate limiting

### JavaScript (package.json)

- `html5-qrcode` — browser-side barcode/QR code scanning

---

## 10. CLI Commands

### Create Admin

```bash
python -m scripts.create_admin --email admin@school.dz --password ********
```

- Creates the first admin teacher account
- Refuses to run if an admin User already exists
- File: `scripts/create_admin.py`

---

## 11. Database Migration

- New `users` table added via Flask-Migrate
- `flask db migrate -m "add users table for authentication"`
- `flask db upgrade`
- No changes to existing tables

---

## 12. Configuration Additions

Added to `app/config.py`:

```python
# JWT
JWT_ACCESS_TOKEN_EXPIRES = 900        # 15 minutes in seconds
JWT_REFRESH_TOKEN_EXPIRES = 604800    # 7 days in seconds

# Rate Limiting
RATELIMIT_LOGIN = "5 per minute"

# Auth
BCRYPT_LOG_ROUNDS = 12
```

---

## 13. Testing Strategy

### Unit Tests
- `tests/test_models/test_user.py` — User model CRUD, to_dict, relationships
- `tests/test_services/test_auth_service.py` — login, token generation, token_version logic
- `tests/test_services/test_import_service.py` — CSV parsing, validation, duplicate handling

### Integration Tests
- `tests/test_routes/test_auth.py` — login/logout/refresh flows, cookie handling, 401/403 responses
- `tests/test_routes/test_admin.py` — teacher CRUD, CSV import, admin-only access

### Key Test Cases
- Teacher login with correct/wrong credentials
- Student login with valid/invalid matricule
- Single-session enforcement (second login invalidates first)
- Token refresh with valid/expired/revoked refresh token
- Rate limiting blocks after 5 failed attempts
- CSV import with valid data, duplicates, and malformed rows
- Protected routes return 401 without auth, 403 with wrong role
- Inactive user cannot authenticate

---

## File Structure (new/modified files)

```
app/
  models/
    user.py                    # NEW — User model
  services/
    auth_service.py            # NEW — auth business logic
    import_service.py          # NEW — CSV import logic
  routes/
    auth.py                    # NEW — /api/auth/* blueprint
    admin.py                   # NEW — /api/admin/* blueprint
    exams.py                   # MODIFIED — add @require_auth, @require_role("teacher")
    students.py                # MODIFIED — add @require_auth, @require_role("teacher")
    questions.py               # MODIFIED — add @require_auth, @require_role("teacher")
    scanning.py                # MODIFIED — add @require_auth, @require_role("teacher")
    grading.py                 # MODIFIED — add @require_auth, @require_role("teacher")
    ai.py                      # MODIFIED — add @require_auth, @require_role("teacher")
  auth.py                      # NEW — decorators (@require_auth, @require_role, @require_admin) + JWT helpers
  config.py                    # MODIFIED — add JWT/rate-limit/bcrypt settings
  __init__.py                  # MODIFIED — register auth/admin blueprints, init Flask-Limiter

frontend/src/
  contexts/
    AuthContext.tsx             # NEW — auth state, login/logout, token refresh
  components/
    ProtectedRoute.tsx         # NEW — role-based route guard
    BarcodeScanner.tsx         # NEW — webcam barcode scanner (html5-qrcode)
  pages/
    LoginPage.tsx              # NEW — teacher/student login tabs
    TeacherManagement.tsx      # NEW — admin teacher CRUD
    StudentImport.tsx          # NEW — CSV upload + preview

scripts/
  create_admin.py              # NEW — CLI bootstrap command

tests/
  test_models/test_user.py     # NEW
  test_services/test_auth_service.py    # NEW
  test_services/test_import_service.py  # NEW
  test_routes/test_auth.py     # NEW
  test_routes/test_admin.py    # NEW
```
