# Phase 4: Network & Deployment — Design Spec

## Overview

Make SmartGrader easy to deploy in two modes: LAN mode (teacher runs one command, students connect on local network) and university server mode (Gunicorn + Nginx on Linux). Docker provided as an optional alternative. SQLite used in both modes. Configuration via environment variables.

## Goals

- LAN mode: single-command startup (`python run.py --lan`), Flask serves API + frontend
- Optional self-signed SSL for LAN webcam access (`--ssl` flag)
- University server: Gunicorn + Nginx config files + systemd service
- Docker optional: Dockerfile + docker-compose.yml
- Environment-based configuration (.env file)
- CORS hardening for production
- Deployment documentation

## Non-Goals

- PostgreSQL support (SQLite is sufficient for exam workloads)
- Cloud platform deployment (Railway, Render, etc.)
- CI/CD pipeline
- Load balancing / horizontal scaling
- AI model deployment config (already handled gracefully)

---

## 1. LAN Mode

### How it works

`python run.py --lan` starts the app for classroom use:

- Flask serves the API on `0.0.0.0:5000` (all interfaces)
- Flask also serves the built React frontend from `frontend/dist/` as static files
- On startup, auto-detects and prints the teacher's LAN IP: "Students can connect at http://192.168.1.x:5000"
- Uses ProductionConfig (DEBUG=False) with SQLite
- Optional `--port` flag to change port (default 5000)

### SSL Flag

`python run.py --lan --ssl`:

- Generates a self-signed SSL certificate in `instance/ssl/` on first run
- Serves on HTTPS (port 5000 by default)
- Prints: "Students can connect at https://192.168.1.x:5000 (accept certificate warning)"
- Uses Python's `ssl` module — no new dependencies

### Static File Serving

In LAN mode, Flask serves `frontend/dist/`:
- `/` → `frontend/dist/index.html`
- `/assets/*` → `frontend/dist/assets/*`
- `/api/*` → Flask API routes (as before)
- All non-API, non-asset routes → `index.html` (SPA fallback for client-side routing)

### Build Prerequisite

Frontend must be built first: `cd frontend && npm run build`

The `--lan` flag checks for `frontend/dist/index.html` and prints an error if missing.

### LAN IP Detection

Uses Python's `socket` module to find the machine's LAN IP:
```python
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip = s.getsockname()[0]
s.close()
```

Falls back to `127.0.0.1` if detection fails.

---

## 2. University Server Mode

### Gunicorn

Config file: `deploy/gunicorn.conf.py`

```
bind = "127.0.0.1:8000"
workers = 4
accesslog = "logs/gunicorn-access.log"
errorlog = "logs/gunicorn-error.log"
```

Start: `gunicorn -c deploy/gunicorn.conf.py "app:create_app('production')"`

### Nginx

Config file: `deploy/nginx.conf`

- Serves `frontend/dist/` for all non-API routes (static files + SPA fallback)
- Proxies `/api/*` requests to Gunicorn (`http://127.0.0.1:8000`)
- Sets security headers (X-Frame-Options, X-Content-Type-Options)
- HTTPS configuration block (commented, with Let's Encrypt instructions)
- Uploads: proxies to Flask, sets `client_max_body_size 50M`

### Systemd

Service file: `deploy/smartgrader.service`

- Runs Gunicorn as a systemd service
- WorkingDirectory points to the app root
- EnvironmentFile reads from `.env`
- Auto-restart on failure

### Deployment Script

`deploy/setup.sh`:

1. Creates virtual environment
2. Installs Python dependencies
3. Builds React frontend
4. Creates `instance/`, `uploads/`, `logs/` directories
5. Runs database migration (`flask db upgrade`)
6. Creates initial admin account (interactive prompt)
7. Prints remaining manual steps (copy Nginx config, enable systemd service)

---

## 3. Docker (Optional)

### Dockerfile

Multi-stage build:

**Stage 1 (Node):**
- FROM node:20-alpine
- Copy `frontend/`, run `npm ci && npm run build`

**Stage 2 (Python):**
- FROM python:3.11-slim
- Copy requirements.txt, install deps
- Copy app code + built frontend from Stage 1
- Expose port 5000
- CMD: Gunicorn with static file serving (same as LAN mode but production-grade)

### docker-compose.yml

```yaml
services:
  smartgrader:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./instance:/app/instance
      - ./uploads:/app/uploads
    env_file: .env
    restart: unless-stopped
```

### .dockerignore

```
node_modules/
frontend/node_modules/
.git/
__pycache__/
instance/
uploads/
logs/
.env
```

---

## 4. Configuration

### .env.example

```env
# Required — generate with: python -m scripts.generate_secret
SECRET_KEY=change-me-to-a-random-string

# Environment: development, testing, production
FLASK_ENV=production

# Database (default: SQLite in instance/)
DATABASE_URL=sqlite:///instance/smart_grader.db

# CORS allowed origins (comma-separated, * for all)
ALLOWED_ORIGINS=*

# Set to true when Flask should serve frontend static files (LAN/Docker mode)
SERVE_STATIC=false
```

### Config Changes (app/config.py)

Add to `Config` base class:
```python
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*")
SERVE_STATIC = os.environ.get("SERVE_STATIC", "false").lower() == "true"
```

`ProductionConfig` already reads `SECRET_KEY` and `DATABASE_URL` from env. Verify these work correctly.

### CORS Changes (app/__init__.py)

Update CORS initialization:
```python
origins = app.config.get("ALLOWED_ORIGINS", "*")
if origins != "*":
    origins = [o.strip() for o in origins.split(",")]
CORS(app, origins=origins)
```

### Static Serving (app/__init__.py)

When `SERVE_STATIC=true` or `--lan` mode:
- Register a catch-all route that serves `frontend/dist/index.html` for non-API routes
- Serve `frontend/dist/assets/` as static files

---

## 5. Scripts

### scripts/generate_secret.py

```python
"""Generate a random SECRET_KEY."""
import secrets
print(secrets.token_hex(32))
```

Usage: `python -m scripts.generate_secret`

### scripts/build.sh

```bash
#!/bin/bash
cd frontend && npm ci && npm run build
echo "Frontend built to frontend/dist/"
```

---

## 6. Documentation

### deploy/README.md

Deployment guide covering:

1. **Quick Start (LAN Mode)**
   - Install Python deps
   - Build frontend
   - Run `python run.py --lan`
   - Share URL with students

2. **University Server Deployment**
   - Server requirements (Python 3.11+, Node 20+, Nginx)
   - Run `deploy/setup.sh`
   - Configure Nginx (copy config, enable site)
   - Enable systemd service
   - Set up HTTPS (Let's Encrypt certbot instructions)
   - Create admin account

3. **Docker Deployment**
   - Copy `.env.example` to `.env`, edit SECRET_KEY
   - `docker-compose up -d`
   - Create admin: `docker-compose exec smartgrader python -m scripts.create_admin ...`

4. **Configuration Reference**
   - All environment variables documented
   - CORS configuration
   - SSL options

### Update main README.md

Add a "Deployment" section with links to `deploy/README.md` and quick-start commands for both modes.

---

## 7. File Structure

```
NEW FILES:
  deploy/
    gunicorn.conf.py        — Gunicorn configuration
    nginx.conf              — Nginx site template
    smartgrader.service     — systemd unit file
    setup.sh                — deployment helper script
    README.md               — deployment documentation
  Dockerfile                — multi-stage build
  docker-compose.yml        — single service config
  .dockerignore             — build exclusions
  .env.example              — environment variable template
  scripts/generate_secret.py — SECRET_KEY generator
  scripts/build.sh          — frontend build script

MODIFIED FILES:
  run.py                    — add --lan, --ssl, --port args, LAN IP detection
  app/config.py             — add ALLOWED_ORIGINS, SERVE_STATIC, verify env var reading
  app/__init__.py           — conditional CORS origins, conditional static file serving
  README.md                 — add deployment section
```

### New Python Dependencies

None.

### Testing

No new automated tests — this phase is configuration and scripts. Manual testing:
1. `python run.py --lan` → access from another device on LAN
2. `python run.py --lan --ssl` → verify HTTPS, webcam access
3. `docker-compose up` → verify app on port 5000
4. `pytest tests/ -v` → verify all existing tests still pass
