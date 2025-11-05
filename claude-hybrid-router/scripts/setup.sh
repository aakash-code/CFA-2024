#!/bin/bash
# Claude Hybrid Router - Setup Script

set -e

echo "=========================================="
echo "Claude Hybrid Router - Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Ollama is installed
echo -e "${YELLOW}[1/6]${NC} Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓${NC} Ollama is installed"
else
    echo -e "${RED}✗${NC} Ollama is not installed"
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Start Ollama service
echo ""
echo -e "${YELLOW}[2/6]${NC} Starting Ollama service..."
if pgrep -x "ollama" > /dev/null; then
    echo -e "${GREEN}✓${NC} Ollama is already running"
else
    echo "Starting Ollama in background..."
    nohup ollama serve > /dev/null 2>&1 &
    sleep 2
    echo -e "${GREEN}✓${NC} Ollama started"
fi

# Pull recommended models
echo ""
echo -e "${YELLOW}[3/6]${NC} Pulling recommended models..."
echo "This may take a while depending on your internet connection..."

models=("qwen2.5-coder:7b" "deepseek-coder:33b")
for model in "${models[@]}"; do
    echo ""
    echo "Pulling $model..."
    if ollama list | grep -q "$model"; then
        echo -e "${GREEN}✓${NC} $model already exists"
    else
        ollama pull "$model"
        echo -e "${GREEN}✓${NC} $model downloaded"
    fi
done

# Create environment file
echo ""
echo -e "${YELLOW}[4/6]${NC} Setting up environment configuration..."
if [ ! -f "/root/claude-hybrid-router/config/.env" ]; then
    cp /root/claude-hybrid-router/config/.env.example /root/claude-hybrid-router/config/.env
    echo -e "${GREEN}✓${NC} Created .env file from template"
    echo -e "${YELLOW}⚠${NC}  Please edit /root/claude-hybrid-router/config/.env with your API keys"
else
    echo -e "${GREEN}✓${NC} .env file already exists"
fi

# Test router
echo ""
echo -e "${YELLOW}[5/6]${NC} Testing router configuration..."
python3 /root/claude-hybrid-router/scripts/router.py

# Create Claude Code configuration
echo ""
echo -e "${YELLOW}[6/6]${NC} Configuring Claude Code..."

# Backup existing config if it exists
if [ -f "/root/.claude/settings.json" ]; then
    cp /root/.claude/settings.json /root/.claude/settings.json.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✓${NC} Backed up existing Claude settings"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit your API keys in: /root/claude-hybrid-router/config/.env"
echo "2. Start the router proxy (coming soon)"
echo "3. Configure Claude Code to use the router"
echo ""
echo "Quick start:"
echo "  # Test Ollama"
echo "  ollama run qwen2.5-coder:7b 'Write hello world in Python'"
echo ""
echo "  # View router config"
echo "  cat /root/claude-hybrid-router/config/router-config.json"
echo ""
echo "  # Test routing logic"
echo "  python3 /root/claude-hybrid-router/scripts/router.py"
echo ""
echo "For documentation: cat /root/claude-hybrid-router/README.md"
echo ""
