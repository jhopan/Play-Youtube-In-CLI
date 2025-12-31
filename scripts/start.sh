#!/bin/bash

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run ./scripts/setup.sh first"
    exit 1
fi

# Activate venv and run bot
echo "🚀 Starting YT Music Bot..."
source venv/bin/activate
python3 main.py
