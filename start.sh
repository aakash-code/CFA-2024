#!/bin/bash

###############################################################################
#                                                                             #
#            CFA Prep Tool - Quick Start Script                              #
#                                                                             #
#     Activates virtual environment and starts the application               #
#                                                                             #
###############################################################################

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting CFA Prep Tool...${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "cfa-venv" ]; then
    echo -e "${RED}✗ Virtual environment not found!${NC}"
    echo "Please run ./install.sh first"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}✓${NC} Activating virtual environment..."
source cfa-venv/bin/activate

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${RED}⚠${NC} Ollama is not running!"
    echo "Starting Ollama in background..."
    ollama serve > /dev/null 2>&1 &
    sleep 2
    echo -e "${GREEN}✓${NC} Ollama started"
fi

# Navigate to backend
cd cfa-prep-tool/backend

# Start the application
echo -e "${GREEN}✓${NC} Starting CFA Prep Tool..."
echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "${GREEN}Application will start on: http://localhost:8000${NC}"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the app
python app.py
