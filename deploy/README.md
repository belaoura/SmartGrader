# SmartGrader Deployment Guide

This guide covers three deployment scenarios: LAN classroom mode, university server, and Docker.

---

## 1. Quick Start — LAN Mode (Classroom)

Run SmartGrader from a teacher's laptop so students on the same Wi-Fi can access it in a browser.

**Prerequisites:** Python 3.10+, Node.js 18+

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Build the frontend
cd frontend && npm install && npm run build && cd ..

# 3. Start in LAN mode
python run.py --lan

# 4. Share the printed URL with students
#    SmartGrader LAN Mode
#    Students can connect at: http://192.168.1.x:5000
```

**With HTTPS** (required for webcam access in browsers):

```bash
python run.py --lan --ssl
# Students must accept the browser security warning once
```

**Custom port:**

```bash
python run.py --lan --port 8080
```

---

## 2. University Server Deployment

For a permanent installation on a Linux server with a domain name.

### Prerequisites

- Ubuntu 22.04 / Debian 12
- Python 3.10+, Node.js 18+
- Nginx
- (Optional) Certbot for HTTPS

### Automated Setup

Copy the project to `/opt/smartgrader`, then run:

```bash
cd /opt/smartgrader
bash deploy/setup.sh
```

The script:
- Creates `instance/`, `uploads/`, `logs/` directories
- Sets up a Python virtual environment and installs dependencies
- Builds the React frontend
- Generates `.env` with a random `SECRET_KEY`
- Runs database migrations

### Configure Nginx

```bash
# Edit the server_name in deploy/nginx.conf first
nano deploy/nginx.conf

sudo cp deploy/nginx.conf /etc/nginx/sites-available/smartgrader
sudo ln -s /etc/nginx/sites-available/smartgrader /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Enable systemd Service

```bash
sudo cp deploy/smartgrader.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now smartgrader

# Check status
sudo systemctl status smartgrader
sudo journalctl -u smartgrader -f
```

### HTTPS with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d exams.university.dz

# Auto-renewal (runs twice daily)
sudo systemctl enable certbot.timer
```

After obtaining the certificate, uncomment the HTTPS server block in `nginx.conf` and reload Nginx.

---

## 3. Docker

### Quick Start

```bash
# 1. Copy and configure environment
cp .env.example .env
# Edit .env: set SECRET_KEY (generate with: python -m scripts.generate_secret)

# 2. Build and start
docker-compose up -d

# 3. Access at http://localhost:5000
```

### Persistent Data

Docker Compose mounts `./instance` and `./uploads` as volumes, so data survives container restarts and rebuilds.

### Rebuild after code changes

```bash
docker-compose up -d --build
```

---

## 4. Configuration Reference

All settings can be set via environment variables (in `.env` or shell):

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `change-me-in-production` | Flask session secret. **Must be changed in production.** Generate with `python -m scripts.generate_secret` |
| `FLASK_ENV` | `development` | `development`, `testing`, or `production` |
| `DATABASE_URL` | SQLite in `instance/` | SQLAlchemy database URI |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins. Comma-separated list or `*` for all. Example: `https://exams.university.dz` |
| `SERVE_STATIC` | `false` | When `true`, Flask serves the built React frontend. Automatically set by `--lan` flag. |

---

## 5. Troubleshooting

### Webcam not working (HTTP)

Browsers block camera access on non-secure origins (plain HTTP). Solutions:
- Use `--ssl` flag with `--lan` mode: `python run.py --lan --ssl`
- Or use a proper HTTPS domain with Let's Encrypt on a server

### CORS errors in browser

The frontend and backend are on different origins. Set `ALLOWED_ORIGINS` to match your frontend URL:

```bash
ALLOWED_ORIGINS=http://192.168.1.5:3000,http://localhost:3000
```

### Self-signed certificate warning

When using `--ssl`, students will see a browser security warning. They should:
1. Click "Advanced" (Chrome) or "More Information" (Firefox)
2. Click "Proceed to site" / "Accept the Risk and Continue"

This only needs to be done once per browser session.

### Frontend dist not found

```
Error: frontend/dist/ not found. Build the frontend first:
  cd frontend && npm run build
```

Run `bash scripts/build.sh` or manually `cd frontend && npm run build`.

### Database migration errors

```bash
# Apply pending migrations
flask db upgrade

# Check current migration state
flask db current
```

### Gunicorn not starting

Check logs:
```bash
sudo journalctl -u smartgrader -n 50
cat logs/gunicorn-error.log
```

Common causes: port already in use, missing `instance/` directory, invalid `.env` syntax.
