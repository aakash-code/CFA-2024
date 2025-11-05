#!/bin/bash

# CFA Prep Tool - Startup Script

echo "================================================"
echo "CFA Exam Prep Tool - Starting Server"
echo "================================================"
echo ""

# Check if we're in the correct directory
if [ ! -f "backend/app.py" ]; then
    echo "Error: Please run this script from the cfa-prep-tool directory"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Check for .env file
if [ ! -f "backend/.env" ]; then
    echo "⚠️  No .env file found"
    echo "Creating .env from template..."
    cp backend/.env.example backend/.env
    echo ""
    echo "IMPORTANT: Please edit backend/.env and add your ANTHROPIC_API_KEY"
    echo "Get your API key from: https://console.anthropic.com/"
    echo ""
    read -p "Press Enter to continue (you can add the API key later)..."
fi

# Install dependencies
echo "Installing dependencies..."
cd backend
pip3 install -q -r requirements.txt 2>&1 | grep -v "WARNING"

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "⚠️  Some warnings during installation (usually safe to ignore)"
fi

echo ""
echo "Starting server on http://localhost:8000"
echo ""
echo "To stop the server, press Ctrl+C"
echo ""
echo "================================================"
echo ""

# Start the server
python3 app.py
