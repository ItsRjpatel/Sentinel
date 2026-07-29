#!/bin/bash
set -e

echo "Starting Sentinel Backend..."

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Please run scripts/setup.sh first."
    exit 1
fi

source .venv/bin/activate
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
