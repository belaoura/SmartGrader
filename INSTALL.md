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

Flask, SQLAlchemy, Flask-Migrate, Flask-CORS, OpenCV (opencv-python-headless), NumPy, pdfkit, pytest.

## 3. Database Setup

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

## 4. CUDA and GPU Setup (for AI Grading)

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

## 5. wkhtmltopdf (for PDF Answer Sheets)

Required for generating printable PDF answer sheets.

**Windows:** Download from https://wkhtmltopdf.org/downloads.html and add to PATH.

**Linux:**
```bash
sudo apt-get install wkhtmltopdf
```

## 6. Frontend Setup

```bash
cd frontend
npm install
```

## 7. Running the Application

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

### Production Build

```bash
cd frontend
npm run build
# Output in frontend/dist/ -- serve with Flask or Nginx
```

## 8. Running Tests

```bash
pytest tests/ -v              # All 40+ tests
pytest tests/test_models/ -v  # Model tests only
pytest tests/ --tb=short      # Compact output
```

## 9. Building the Thesis PDF

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
