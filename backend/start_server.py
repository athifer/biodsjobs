#!/usr/bin/env python3
"""
Simple server startup script that ensures correct working directory.
"""
import os
import sys

# Change to the backend directory (where this script is located)
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)
print(f"Changed working directory to: {os.getcwd()}")

# Add the backend directory to Python path
sys.path.insert(0, backend_dir)

# Now import and run uvicorn
import uvicorn

if __name__ == "__main__":
    # Import the FastAPI app
    from app import app
    
    print("Starting biodsjobs API server...")
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[backend_dir]
    )
