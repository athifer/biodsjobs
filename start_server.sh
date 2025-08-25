#!/bin/bash

# BioDSJobs Server Startup Script
# Automatically activates virtual environment and starts the server

set -e

# Get the project root directory (where this script is located)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
VENV_DIR="$PROJECT_ROOT/.venv"

echo "🚀 Starting BioDSJobs Server"
echo "=============================="
echo "📁 Project root: $PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at $VENV_DIR"
    echo "Please run ./deploy.sh first to set up the environment"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Change to backend directory
cd "$BACKEND_DIR"
echo "📁 Changed to backend directory: $(pwd)"

# Check if uvicorn is installed
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "❌ uvicorn not found in virtual environment"
    echo "Please run ./deploy.sh to install dependencies"
    exit 1
fi

# Start the server
echo "🚀 Starting server..."
echo "   Frontend: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Health:   http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python start_server.py
