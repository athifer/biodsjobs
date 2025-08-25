#!/bin/bash

# Stop any existing BioDSJobs servers

echo "🛑 Stopping BioDSJobs servers..."

# Kill processes on common ports
for port in 8000 8001 8002 8003; do
    if lsof -i :$port >/dev/null 2>&1; then
        echo "   Stopping server on port $port..."
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
    fi
done

# Kill any python processes running start_server.py
pkill -f "python start_server.py" 2>/dev/null || true
pkill -f "uvicorn.*app:app" 2>/dev/null || true

echo "✅ All BioDSJobs servers stopped"
