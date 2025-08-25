#!/bin/bash
cd backend
source ../.venv/bin/activate
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000
