#!/bin/bash

# kill any existing instances on port 8000 or 5173
fuser -k 8000/tcp 2>/dev/null
fuser -k 5173/tcp 2>/dev/null

echo "🚀 Starting Gesture Object Vision Backend & Frontend..."

# start fastapi backend server in background
PYTHONPATH=. ./venv/bin/python backend/main.py &
BACKEND_PID=$!

# wait 2 seconds for backend to initialize
sleep 2

# start react frontend dev server
cd frontend
npm run dev

# cleanup backend when user stops script (CTRL+C)
trap "kill $BACKEND_PID" EXIT
