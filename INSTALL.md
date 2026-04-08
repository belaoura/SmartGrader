# Installation Guide

Step-by-step instructions for setting up SmartGrader on Windows or Linux.

## Prerequisites

| Requirement | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Backend, AI model |
| Node.js | 18+ | Frontend build |
| Git | any | Version control |
| NVIDIA GPU | 6+ GB VRAM | AI grading (optional -- MCQ scanning works without GPU) |

## 1. Clone the Repository

```bash
git clone https://github.com/your-org/SmartGrader.git
cd SmartGrader
```

## 2. Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

### Dependencies installed

Flask, SQLAlchemy, Flask-Migrate, Flask-CORS, Flask-Limiter, PyJWT, bcrypt, OpenCV (opencv-python-headless), NumPy, pdfkit, pytest, python-dotenv, gunicorn.

## 3. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

```
SECRET_KEY=<long-random-string>
JWT_SECRET=<another-long-random-string>
FLASK_ENV=development
```

All other values have safe defaults for development.

## 4. Database Setup

The database auto-creates on first run. To seed sample data:

```bash
python -m scripts.seed_data
```

This creates:
- 7 exams (Mathematics, Biology, Physics, Chemistry, Computer Science, English, History)
- 59 questions with 2-5 choices each
- 10 students with Algerian university emails
- 50+ grading results with randomized scores

To reset the database:

```bash
rm instance/smart_grader.db
python -m scripts.seed_data
```

## 5. Create the First Admin Account

```bash
python -m scripts.create_admin
```

Follow the prompts to set admin email and password. This account can then create teacher accounts from the Admin Panel UI.

## 6. CUDA and GPU Setup (for AI Grading)

AI grading requires a CUDA-compatible NVIDIA GPU. MCQ optical scanning works without a GPU.

```bash
# Check your CUDA version
nvidia-smi

# Install PyTorch with CUDA support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install AI dependencies
pip install transformers accelerate bitsandbytes qwen-vl-utils
```

Verify GPU:

```bash
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

### Model Download

The Qwen2.5-VL-3B-Instruct model downloads automatically on first use (~6 GB). To pre-download:

```bash
python -c "
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
Qwen2VLForConditionalGeneration.from_pretrained('Qwen/Qwen2.5-VL-3B-Instruct')
AutoProcessor.from_pretrained('Qwen/Qwen2.5-VL-3B-Instruct')
"
```

## 7. wkhtmltopdf (for PDF Answer Sheets)

Required for generating printable PDF answer sheets.

**Windows:** Download from https://wkhtmltopdf.org/downloads.html and add to PATH.

**Linux:**
```bash
sudo apt-get install wkhtmltopdf
```

## 8. Frontend Setup

```bash
cd frontend
npm install
```

## 9. Running the Application

### Development (two terminals)

```bash
# Terminal 1: Flask backend
python run.py
# API runs at http://localhost:5000

# Terminal 2: React frontend
cd frontend
npm run dev
# App runs at http://localhost:3000
```

### LAN Mode (Classroom -- single process)

Build the frontend once, then run Flask in LAN mode to serve everything from one URL:

```bash
cd frontend && npm run build && cd ..
python run.py --lan
# Backend + frontend at http://<your-ip>:5000
```

Optional SSL (self-signed certificate generated automatically):

```bash
python run.py --lan --ssl
```

Students connect to `https://<your-ip>:5000`. They will see a browser certificate warning for self-signed certs -- they can proceed by clicking "Advanced" > "Accept risk".

### University Server (Gunicorn + Nginx + systemd)

See `deploy/` directory for full configuration files. Summary:

```bash
# Install Gunicorn
pip install gunicorn

# Test Gunicorn manually
gunicorn -w 4 -b 127.0.0.1:5000 "app:create_app()"

# Copy systemd service file
sudo cp deploy/smartgrader.service /etc/systemd/system/
sudo systemctl enable smartgrader
sudo systemctl start smartgrader

# Configure Nginx reverse proxy
sudo cp deploy/nginx.conf /etc/nginx/sites-available/smartgrader
sudo ln -s /etc/nginx/sites-available/smartgrader /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### Docker

```bash
# Copy and edit environment file
cp .env.example .env
# Edit SECRET_KEY, JWT_SECRET, FLASK_ENV=production

# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

The compose file starts:
- `web` -- Flask + Gunicorn
- `nginx` -- Nginx reverse proxy on port 80
- Volumes for `instance/` (SQLite DB) and `uploads/`

For HTTPS on the university server, obtain a certificate from Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.example.com
```

## 10. Running Tests

```bash
pytest tests/ -v              # All 191 tests
pytest tests/test_models/ -v  # Model tests only
pytest tests/test_auth/ -v    # Auth tests only
pytest tests/ --tb=short      # Compact output
```

## 11. Building the Thesis PDF

```bash
# Using Python (recommended, no external tools needed)
pip install markdown xhtml2pdf pyyaml
python docs/thesis/build_pdf.py
# Output: docs/thesis/thesis.pdf

# Using Pandoc (alternative, requires pandoc + XeLaTeX)
bash docs/thesis/build.sh
```

## Troubleshooting

### Port 5000 blocked on Windows

Windows 11 reserves port 5000. Use a different port:

```bash
# In run.py, change port=5000 to port=5005
# Update frontend/vite.config.js proxy to match
```

### AI model out of memory

The model needs ~6-8 GB VRAM. If you get OOM errors:
- Close other GPU applications
- Ensure 4-bit quantization is enabled (default)
- Try reducing `max_new_tokens` in `app/config.py`

### Database locked

Stop all Python processes accessing the database, then retry:
```bash
taskkill /F /IM python.exe    # Windows
pkill python                  # Linux
```

### JWT cookie not sent (HTTPS mismatch)

If the frontend is on HTTP but the cookie has `Secure=True`, the browser will not send it. In development, ensure `COOKIE_SECURE=False` in `.env`. In production with HTTPS, set `COOKIE_SECURE=True`.

### Docker container cannot write uploads

The `uploads/` and `instance/` directories must be writable. If you see permission errors:

```bash
sudo chown -R 1000:1000 instance/ uploads/
```
