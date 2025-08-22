#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Optional: run initial ingestion before starting the server
echo "Running initial job ingestion..."
python ingestor.py

# Start the API server with automatic updates every 4 hours
echo "Starting bioinfojobs API server on http://localhost:8000"
echo "Jobs will be automatically updated every 4 hours"
uvicorn app:app --reload --port 8000
