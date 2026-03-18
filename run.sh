#!/usr/bin/env bash
# Adaptive Cachy Beauty Engine — launcher

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/venv"
PYTHON="$VENV/bin/python"

# Check if venv exists
if [ ! -f "$PYTHON" ]; then
    echo "❌ Virtual environment not found. Run first:"
    echo "   python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Allow passing log level: ./run.sh debug
if [ "$1" = "debug" ]; then
    export ACB_LOG_LEVEL=DEBUG
    echo "🔍 Debug mode enabled (ACB_LOG_LEVEL=DEBUG)"
fi

echo "🚀 Starting Adaptive Cachy Beauty Engine..."
exec "$PYTHON" "$SCRIPT_DIR/src/main.py"
