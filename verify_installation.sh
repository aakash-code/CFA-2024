#!/bin/bash

###############################################################################
#                                                                             #
#            CFA Prep Tool - Installation Verification Script                #
#                                                                             #
#     Run this anytime to check your installation status                     #
#                                                                             #
###############################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║           CFA Prep Tool - Installation Verification           ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

TOTAL_CHECKS=0
PASSED_CHECKS=0
WARNINGS=0

check_item() {
    local name="$1"
    local status="$2"
    local message="$3"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [ "$status" = "pass" ]; then
        echo -e "${GREEN}✓${NC} $name"
        [ -n "$message" ] && echo "  └─ $message"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    elif [ "$status" = "warn" ]; then
        echo -e "${YELLOW}⚠${NC} $name"
        [ -n "$message" ] && echo "  └─ $message"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${RED}✗${NC} $name"
        [ -n "$message" ] && echo "  └─ $message"
    fi
}

echo "Running system checks..."
echo ""

###############################################################################
# System Checks
###############################################################################

echo -e "${BLUE}System Requirements:${NC}"

# Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    check_item "Python 3" "pass" "Version $PYTHON_VERSION"
else
    check_item "Python 3" "fail" "Not installed - Install from https://python.org"
fi

# pip
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | awk '{print $2}')
    check_item "pip" "pass" "Version $PIP_VERSION"
else
    check_item "pip" "fail" "Not installed"
fi

# Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | awk '{print $3}')
    check_item "Git" "pass" "Version $GIT_VERSION"
else
    check_item "Git" "warn" "Not installed (optional)"
fi

# RAM
OS="$(uname -s)"
if [ "$OS" = "Darwin" ]; then
    TOTAL_RAM=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
elif [ "$OS" = "Linux" ]; then
    TOTAL_RAM=$(grep MemTotal /proc/meminfo | awk '{print int($2/1024/1024)}')
fi

if [ "$TOTAL_RAM" -ge 16 ]; then
    check_item "RAM" "pass" "${TOTAL_RAM}GB (Excellent)"
elif [ "$TOTAL_RAM" -ge 8 ]; then
    check_item "RAM" "pass" "${TOTAL_RAM}GB (Good)"
else
    check_item "RAM" "warn" "${TOTAL_RAM}GB (May be slow, 8GB+ recommended)"
fi

echo ""

###############################################################################
# Project Files
###############################################################################

echo -e "${BLUE}Project Files:${NC}"

# Virtual environment
if [ -d "cfa-venv" ]; then
    check_item "Virtual Environment" "pass" "Found at ./cfa-venv"
else
    check_item "Virtual Environment" "fail" "Not found - Run ./install.sh"
fi

# Backend files
if [ -d "cfa-prep-tool/backend" ]; then
    check_item "Backend Directory" "pass" "Found"
else
    check_item "Backend Directory" "fail" "Not found"
fi

# Requirements file
if [ -f "cfa-prep-tool/backend/requirements.txt" ]; then
    check_item "Requirements File" "pass" "Found"
else
    check_item "Requirements File" "fail" "Not found"
fi

# Environment config
if [ -f "cfa-prep-tool/backend/.env" ]; then
    check_item "Environment Config" "pass" "Found (.env file)"
else
    check_item "Environment Config" "warn" "Not found - Run: cp cfa-prep-tool/backend/.env.example.hybrid cfa-prep-tool/backend/.env"
fi

echo ""

###############################################################################
# Python Packages
###############################################################################

echo -e "${BLUE}Python Dependencies:${NC}"

# Check if venv is activated or use system Python
if [ -n "$VIRTUAL_ENV" ]; then
    PYTHON_CMD="python"
    check_item "Virtual Env Active" "pass" "Currently activated"
else
    PYTHON_CMD="python3"
    check_item "Virtual Env Active" "warn" "Not activated - Run: source cfa-venv/bin/activate"
fi

# Check key packages
PACKAGES=("fastapi" "uvicorn" "sqlalchemy" "httpx")
for pkg in "${PACKAGES[@]}"; do
    if $PYTHON_CMD -c "import $pkg" 2>/dev/null; then
        VERSION=$($PYTHON_CMD -c "import $pkg; print($pkg.__version__)" 2>/dev/null || echo "installed")
        check_item "$pkg" "pass" "Version $VERSION"
    else
        check_item "$pkg" "fail" "Not installed - Run: pip install -r cfa-prep-tool/backend/requirements.txt"
    fi
done

echo ""

###############################################################################
# Ollama & Models
###############################################################################

echo -e "${BLUE}Ollama & AI Models:${NC}"

# Ollama installed
if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama --version 2>&1 | head -n1)
    check_item "Ollama Installed" "pass" "$OLLAMA_VERSION"
else
    check_item "Ollama Installed" "fail" "Not installed - Visit https://ollama.com/download"
fi

# Ollama running
if pgrep -x "ollama" > /dev/null; then
    check_item "Ollama Service" "pass" "Running"

    # Check models
    if command -v ollama &> /dev/null; then
        MODEL_COUNT=$(ollama list 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')
        if [ "$MODEL_COUNT" -gt 0 ]; then
            check_item "AI Models" "pass" "$MODEL_COUNT model(s) installed"

            # Check for Finance-LLM
            if ollama list 2>/dev/null | grep -q "finance-llm"; then
                check_item "Finance-LLM" "pass" "Installed (CFA-specialized)"
            else
                check_item "Finance-LLM" "warn" "Not installed - Run: cd cfa-prep-tool/backend && ./setup_finance_llm.sh"
            fi

            # Check for fallback models
            if ollama list 2>/dev/null | grep -q "qwen2.5-coder:7b\|deepseek-coder"; then
                check_item "Fallback Models" "pass" "Available"
            else
                check_item "Fallback Models" "warn" "Install recommended: ollama pull qwen2.5-coder:7b"
            fi
        else
            check_item "AI Models" "fail" "No models installed - Run: cd cfa-prep-tool/backend && ./setup_finance_llm.sh"
        fi
    fi
else
    check_item "Ollama Service" "fail" "Not running - Run: ollama serve"
fi

echo ""

###############################################################################
# Database
###############################################################################

echo -e "${BLUE}Database:${NC}"

if [ -f "cfa-prep-tool/backend/cfa_prep.db" ]; then
    DB_SIZE=$(du -h "cfa-prep-tool/backend/cfa_prep.db" | awk '{print $1}')
    check_item "SQLite Database" "pass" "Exists ($DB_SIZE)"
else
    check_item "SQLite Database" "warn" "Not created yet (will be created on first run)"
fi

echo ""

###############################################################################
# Summary
###############################################################################

echo "═══════════════════════════════════════════════════════════"
echo -e "${BLUE}Installation Status Summary:${NC}"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  Total Checks: $TOTAL_CHECKS"
echo -e "  ${GREEN}Passed: $PASSED_CHECKS${NC}"
echo -e "  ${YELLOW}Warnings: $WARNINGS${NC}"
echo -e "  ${RED}Failed: $((TOTAL_CHECKS - PASSED_CHECKS - WARNINGS))${NC}"
echo ""

# Overall status
if [ $PASSED_CHECKS -eq $TOTAL_CHECKS ]; then
    echo -e "${GREEN}✓ Perfect! Everything is installed correctly.${NC}"
    echo ""
    echo "You're ready to start:"
    echo "  1. source cfa-venv/bin/activate"
    echo "  2. cd cfa-prep-tool/backend"
    echo "  3. python app.py"
    echo "  4. Open http://localhost:8000"
elif [ $((PASSED_CHECKS + WARNINGS)) -ge $((TOTAL_CHECKS * 80 / 100)) ]; then
    echo -e "${YELLOW}⚠ Installation is mostly complete with some warnings.${NC}"
    echo ""
    echo "You can likely run the app, but check warnings above for optimal performance."
else
    echo -e "${RED}✗ Installation is incomplete.${NC}"
    echo ""
    echo "Please address the failed checks above."
    echo "Run ./install.sh to complete installation."
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "For help, see: LOCAL_SETUP_GUIDE.md"
echo "═══════════════════════════════════════════════════════════"
