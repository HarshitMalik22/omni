#!/bin/bash

# Set colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required commands
for cmd in python3 pip uvicorn streamlit; do
    if ! command_exists "$cmd"; then
        echo -e "${YELLOW}Error: $cmd is not installed. Please install it and try again.${NC}"
        exit 1
    fi
done

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}Virtual environment not found. Please run setup_and_run.sh first.${NC}"
    exit 1
fi

# Start FastAPI backend in the background
echo -e "${GREEN}Starting FastAPI backend...${NC}
${YELLOW}API will be available at: http://localhost:8000${NC}"
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start Streamlit dashboard in the background
echo -e "\n${GREEN}Starting Streamlit dashboard...${NC}"
echo -e "${YELLOW}Dashboard will be available at: http://localhost:8501${NC}"
streamlit run auction_dashboard.py &
DASHBOARD_PID=$!

# Function to clean up background processes
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $BACKEND_PID $DASHBOARD_PID 2>/dev/null
    deactivate
    echo -e "${GREEN}All services stopped.${NC}"
    exit 0
}

# Set up trap to catch Ctrl+C
trap cleanup INT

echo -e "\n${GREEN}🚀 OmniAuction is now running!${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}"

# Keep the script running
wait $BACKEND_PID $DASHBOARD_PID
