#!/bin/bash

# Start the FastAPI server in the background
echo "Starting FastAPI server..."
uvicorn api.main:app --reload &
FASTAPI_PID=$!

# Wait for the server to start
echo "Waiting for server to start..."
sleep 5

# Start the Streamlit dashboard in the background
echo "Starting Streamlit dashboard..."
streamlit run auction_dashboard.py &
STREAMLIT_PID=$!

# Start the voice agent in the foreground
echo "Starting Voice Agent..."
python voice_agent.py

# Cleanup function to stop background processes
cleanup() {
    echo "Shutting down..."
    kill $FASTAPI_PID $STREAMLIT_PID 2>/dev/null
    exit 0
}

# Set up trap to catch script termination
trap cleanup SIGINT SIGTERM

# Keep the script running
wait $FASTAPI_PID $STREAMLIT_PID
