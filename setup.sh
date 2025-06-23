#!/bin/bash

# Update pip
echo "Updating pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install additional dependencies for voice agent
echo "Installing voice agent dependencies..."
pip install websockets python-dotenv

# Create necessary directories
echo "Setting up directories..."
mkdir -p logs

# Set execute permissions on scripts
chmod +x run.sh

echo "\nSetup complete! You can now start the application with:\n"
echo "  ./run.sh\n"
echo "Or manually start the components with:"
echo "  1. uvicorn api.main:app --reload"
echo "  2. streamlit run auction_dashboard.py"
echo "  3. python voice_agent.py"
