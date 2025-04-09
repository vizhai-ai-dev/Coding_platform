#!/bin/bash

# Start the backend server
cd backend
source venv/bin/activate
uvicorn main:app --reload &
BACKEND_PID=$!

# Start the frontend server
cd ../frontend
npm start &
FRONTEND_PID=$!

# Function to handle cleanup
cleanup() {
    echo "Shutting down servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit 0
}

# Set up trap for cleanup
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait 