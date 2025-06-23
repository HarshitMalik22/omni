#!/bin/bash

# Set colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting OmniAuction Setup...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
else
    echo -e "${GREEN}Activating existing virtual environment...${NC}"
    source venv/bin/activate
fi

# Install requirements
echo -e "${GREEN}Installing requirements...${NC}"
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${GREEN}Creating .env file...${NC}"
    cat > .env <<EOL
# API Configuration
AUCTION_API_URL=http://localhost:8000/api

# Database Configuration (if needed)
# DATABASE_URL=sqlite:///./auction.db

# Authentication (if needed)
# SECRET_KEY=your-secret-key
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=30
EOL
else
    echo -e "${YELLOW}.env file already exists.${NC}"
fi

echo -e "\n${GREEN}✅ Setup complete!${NC}"
echo -e "\nTo start the backend server, run:${NC}"
echo -e "  ${YELLOW}source venv/bin/activate && uvicorn api.main:app --reload${NC}"
echo -e "\nThen open http://localhost:8000 in your browser to access the API documentation.${NC}"

echo -e "\nTo start the auction dashboard, run:${NC}"
echo -e "  ${YELLOW}source venv/bin/activate && streamlit run auction_dashboard.py${NC}"
