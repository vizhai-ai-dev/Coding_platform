#!/bin/bash

# Initialize the database
cd backend
source venv/bin/activate
python init_db.py

# Start the backend server
uvicorn main:app --reload &
BACKEND_PID=$!

# Function to handle cleanup
cleanup() {
    echo "Shutting down server..."
    kill $BACKEND_PID
    exit 0
}

# Set up trap for cleanup
trap cleanup SIGINT SIGTERM

# Wait for the process
wait 