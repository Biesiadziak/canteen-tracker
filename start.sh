#!/bin/bash

# Configuration
PROJECT_DIR="/home/esa5/site/canteen-tracker"
LOG_FILE="$PROJECT_DIR/backend.log"
PORT=8000

# Navigate to project directory
cd "$PROJECT_DIR" || { echo "Directory not found"; exit 1; }

# Activate virtual environment
source venv/bin/activate

# Kill any process currently using the port
if command -v fuser >/dev/null; then
    fuser -k $PORT/tcp >/dev/null 2>&1
fi

# Start the application in the background
nohup python backend/app.py > "$LOG_FILE" 2>&1 &

echo "Canteen Tracker started on port $PORT"
echo "Logs are being written to $LOG_FILE"
