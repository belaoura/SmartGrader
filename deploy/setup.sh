#!/bin/bash
# SmartGrader University Server Setup
set -e

APP_DIR="/opt/smartgrader"
echo "=== SmartGrader University Server Setup ==="

# Create directories
mkdir -p "$APP_DIR"/{instance,uploads,logs}

# Python environment
echo "Setting up Python environment..."
python3 -m venv "$APP_DIR/venv"
source "$APP_DIR/venv/bin/activate"
pip install -r requirements.txt

# Build frontend
echo "Building frontend..."
cd "$APP_DIR/frontend"
npm ci
npm run build
cd "$APP_DIR"

# Environment config
if [ ! -f .env ]; then
    cp .env.example .env
    SECRET=$(python -m scripts.generate_secret)
    sed -i "s/change-me-to-a-random-string/$SECRET/" .env
    echo "Generated .env with random SECRET_KEY"
fi

# Database
echo "Running database migrations..."
export FLASK_APP=run.py
flask db upgrade

# Create admin
echo ""
read -p "Create admin account? (y/n): " create_admin
if [ "$create_admin" = "y" ]; then
    read -p "Admin email: " admin_email
    read -sp "Admin password: " admin_pass
    echo ""
    python -m scripts.create_admin --email "$admin_email" --password "$admin_pass"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Remaining manual steps:"
echo "  1. Copy Nginx config:  sudo cp deploy/nginx.conf /etc/nginx/sites-available/smartgrader"
echo "  2. Enable Nginx site:  sudo ln -s /etc/nginx/sites-available/smartgrader /etc/nginx/sites-enabled/"
echo "  3. Test Nginx config:  sudo nginx -t"
echo "  4. Reload Nginx:       sudo systemctl reload nginx"
echo "  5. Copy systemd unit:  sudo cp deploy/smartgrader.service /etc/systemd/system/"
echo "  6. Enable service:     sudo systemctl enable --now smartgrader"
echo "  7. (Optional) HTTPS:   sudo certbot --nginx -d exams.university.dz"
