#!/bin/bash
set -e

echo "Setting up Sentinel Backend..."

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
cd backend
python3 -m pip install --upgrade pip
pip install -e ".[dev]"

echo "Setup complete."
