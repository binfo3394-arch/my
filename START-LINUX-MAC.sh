#!/bin/bash
echo "========================================"
echo "  ST Mobile & Designing — POS v19"
echo "  Flask + SQLite Web Server"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 install නෑ!"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "Mac: brew install python3"
    exit 1
fi

# Install Flask
pip3 install flask -q 2>/dev/null || pip install flask -q

echo "Starting server..."
echo ""
echo "Open browser: http://localhost:5000"
echo ""
echo "Server stop කරන්න: Ctrl+C"
echo "========================================"
echo ""

python3 app.py
