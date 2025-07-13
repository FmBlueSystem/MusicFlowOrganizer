#!/bin/bash
# MusicFlow Organizer - Virtual Environment Launcher
# ==================================================
# 
# Convenient script to launch MusicFlow Organizer from virtual environment
# 
# Usage:
#   ./musicflow.sh              # Launch GUI
#   ./musicflow.sh demo         # Run demo
#   ./musicflow.sh test         # Run tests
#   ./musicflow.sh console      # Interactive console
#
# Developed by BlueSystemIO

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv_musicflow"
VENV_PYTHON="$VENV_DIR/bin/python"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎼 MusicFlow Organizer - Virtual Environment Launcher${NC}"
echo "=" ========================================================

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}❌ Virtual environment not found at: $VENV_DIR${NC}"
    echo -e "${YELLOW}Please create it with: python3 -m venv venv_musicflow${NC}"
    exit 1
fi

# Check if Python exists in venv
if [ ! -f "$VENV_PYTHON" ]; then
    echo -e "${RED}❌ Python not found in virtual environment${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Virtual environment found${NC}"
echo -e "${GREEN}✅ Python executable: $VENV_PYTHON${NC}"

# Change to project directory
cd "$SCRIPT_DIR"

# Parse command line argument
MODE="${1:-gui}"

case "$MODE" in
    "gui"|"")
        echo -e "${BLUE}🚀 Launching GUI...${NC}"
        "$VENV_PYTHON" run_musicflow.py --gui
        ;;
    "demo")
        echo -e "${BLUE}🎭 Running demo...${NC}"
        "$VENV_PYTHON" run_musicflow.py --demo
        ;;
    "test")
        echo -e "${BLUE}🧪 Running tests...${NC}"
        "$VENV_PYTHON" run_musicflow.py --test
        ;;
    "console")
        echo -e "${BLUE}💻 Launching console...${NC}"
        "$VENV_PYTHON" run_musicflow.py --console
        ;;
    "install")
        echo -e "${BLUE}📦 Installing dependencies...${NC}"
        "$VENV_PYTHON" -m pip install --upgrade pip
        "$VENV_PYTHON" -m pip install PySide6 numpy scikit-learn pytest
        echo -e "${GREEN}✅ Dependencies installed${NC}"
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [MODE]"
        echo ""
        echo "Available modes:"
        echo "  gui      Launch GUI application (default)"
        echo "  demo     Run SOLID architecture demo"
        echo "  test     Run test suite"
        echo "  console  Launch interactive console"
        echo "  install  Install/update dependencies"
        echo "  help     Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./musicflow.sh           # Launch GUI"
        echo "  ./musicflow.sh demo      # Run demo"
        echo "  ./musicflow.sh test      # Run tests"
        ;;
    *)
        echo -e "${RED}❌ Unknown mode: $MODE${NC}"
        echo "Use './musicflow.sh help' for available options"
        exit 1
        ;;
esac

exit_code=$?
echo ""
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✅ Completed successfully${NC}"
else
    echo -e "${RED}❌ Exited with code: $exit_code${NC}"
fi

exit $exit_code