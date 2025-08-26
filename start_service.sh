#!/bin/bash

# Styled AI - Data Science Processing Service
# Startup Script

echo "Starting Styled AI Data Science Processing Service..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p models logs

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Please create one based on config.env.example"
    echo "Starting with default configuration..."
fi

# Start the service
echo "Starting the service..."
python -m uvicorn src.styled_ai.main:app --host 0.0.0.0 --port 8000 --reload
