#!/usr/bin/env bash
# Build script for Render deployment

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs

# Set permissions
echo "Setting permissions..."
chmod +x backend/main.py

echo "Build completed successfully!" 