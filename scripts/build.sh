#!/bin/bash
# Build the SmartGrader frontend
set -e

echo "Building frontend..."
cd "$(dirname "$0")/../frontend"
npm ci
npm run build
echo "Frontend built to frontend/dist/"
