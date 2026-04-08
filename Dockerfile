# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python app
FROM python:3.11-slim
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# App code
COPY app/ app/
COPY migrations/ migrations/
COPY scripts/ scripts/
COPY run.py .

# Frontend build from Stage 1
COPY --from=frontend-build /app/frontend/dist frontend/dist

# Create directories
RUN mkdir -p instance uploads logs

# Environment
ENV FLASK_ENV=production
ENV SERVE_STATIC=true

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:create_app('production')"]
