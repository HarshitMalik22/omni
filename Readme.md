# OmniAuction - Real-Time Auction System for OmniDimension

## 🚀 Overview

OmniAuction is a real-time auction system designed for seamless integration with OmniDimension's no-code platform. It provides a complete set of RESTful APIs for managing auctions, products, and bids, allowing OmniDimension to handle all user interactions through its visual interface.

## ✨ Features

### Core Features

- **RESTful API**: Fully documented endpoints for all auction operations
- **Real-time Bidding**: WebSocket support for live bid updates
- **Product Management**: CRUD operations for auction products
- **Bid Management**: Place and track bids with full history
- **Auto-bidding**: Support for automatic bid management
- **Time-based Auctions**: Configurable auction durations with countdowns

## 🛠️ Tech Stack

### Backend

- **FastAPI**: High-performance web framework for building APIs
- **WebSockets**: Real-time bidirectional communication
- **Uvicorn**: ASGI server for running FastAPI applications
- **Pydantic**: Data validation and settings management

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Local Development

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/omniauction.git
   cd omniauction
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the development server:

   ```bash
   cd api
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`

## 🌐 Deployment

### Recommended Deployment Options

1. **Render** (Easiest)
   - Connect your GitHub repository
   - Select the `api` directory as the root
   - Set the following environment variables:
     - `PYTHON_VERSION`: 3.9+
     - `INSTALL_COMMAND`: pip install -r requirements.txt
     - `START_COMMAND`: uvicorn main:app --host 0.0.0.0 --port $PORT

2. **Railway**
   - Import your GitHub repository
   - Select the `api` directory
   - Use the Python template
   - Set the start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## 🔌 OmniDimension Integration

### Required Environment Variables

- `API_BASE_URL`: The public URL of your deployed API (e.g., `https://yourapp.onrender.com`)

### API Endpoints

#### List All Products

- **GET** `/api/products`
- Returns: Array of product objects with current bid information

#### Get Product Details

- **GET** `/api/products/{product_id}`
- Returns: Detailed product information including bid history

#### Place a Bid

- **POST** `/api/bids`
- Body: `{ "product_id": "string", "user": "string", "amount": float }`
- Returns: Confirmation of the placed bid

#### Get Bid History

- **GET** `/api/products/{product_id}/bids`
- Returns: Complete bid history for a product

#### Set Auto-Bid

- **POST** `/api/products/{product_id}/auto-bid`
- Body: `{ "user": "string", "max_bid": float }`
- Returns: Confirmation of auto-bid settings

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

2. **Run the setup script**:
   ```bash
   ./setup_and_run.sh
   ```
   This will:
   - Create a virtual environment
   - Install all dependencies
   - Set up environment variables

3. **Start all services**:
   ```bash
   ./run_all.sh
   ```
   This will start:
   - FastAPI backend on http://localhost:8000
   - Streamlit dashboard on http://localhost:8501

4. **Access the services**:
   - API Documentation: http://localhost:8000/docs
   - Admin Dashboard: http://localhost:8501

### Manual Installation

If you prefer to set up manually:

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd omni
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🏃‍♂️ Running the Application

### 1. Start the API Server
```bash
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

### 2. Start the Web Dashboard
```bash
streamlit run auction_dashboard.py
```

Access the dashboard at `http://localhost:8501`

### 3. Start the Voice Agent
```bash
python voice_agent.py
```

## 🌐 API Endpoints

### Products
- `GET /api/products` - List all products
- `GET /api/products/{product_id}` - Get product details
- `POST /api/bids` - Place a new bid

### WebSocket
- `ws://localhost:8000/ws` - WebSocket endpoint for real-time updates

## 🗣️ Voice Commands

### Basic Commands
- "List all products" - List available auction items
- "Tell me about iPhone" - Get details about a specific product
- "Bid $1000 on iPhone" - Place a bid on an item
- "What's my status?" - Check your bidding status
- "Help" - Show available commands

### Example Conversation
```
User: List all products
Assistant: Here are the available items: 
1. iPhone 15 Pro - Current bid: $1200. 10m 30s remaining.
2. MacBook Pro 16 - Current bid: $2500. 25m 15s remaining.

User: Tell me about iPhone
Assistant: iPhone 15 Pro. Latest iPhone with A17 Pro chip and 48MP camera. 
Current highest bid is $1200. 10m 15s remaining. 
Would you like to place a bid?

User: Bid $1300
Assistant: Your bid of $1300 has been placed! Success! Your bid of $1300.00 on iPhone 15 Pro has been placed.
```

## 📊 Dashboard Features

### Product Listing
- View all available auction items
- See current highest bid and time remaining
- Sort and filter products

### Product Details
- View detailed product information
- See bidding history with timestamps
- Interactive bid history chart

### Bid Management
- Place new bids with validation
- Real-time bid updates
- Bid confirmation and notifications

## 📱 Voice Agent Features

### Natural Language Understanding
- Understands product names and numbers
- Handles variations in commands
- Supports multi-turn conversations

### Real-time Updates
- Notifications for new bids
- Auction status updates
- Time remaining announcements

### User Context
- Remembers user preferences
- Tracks conversation context
- Personalizes responses

## 🛠️ Development

### Project Structure
```
omni/
├── api/
│   └── main.py           # FastAPI application
├── static/
│   └── js/
│       └── auction.js    # WebSocket client
├── auction_agent.py      # Core auction logic
├── auction_dashboard.py  # Streamlit dashboard
├── voice_agent.py        # Voice interface
└── requirements.txt      # Dependencies
```

### Environment Variables
Create a `.env` file in the root directory with the following variables:
```
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# WebSocket Configuration
WS_HOST=0.0.0.0
WS_PORT=8000

# Application Settings
DEBUG=True
```

### Running Tests
```bash
pytest tests/
```

## 📈 Monitoring and Logging

### Logs
Application logs are written to `logs/auction.log` with the following format:
```
[2023-11-01 12:00:00] INFO: New bid placed - Product: iPhone 15 Pro, Amount: $1300.00, User: JohnDoe
```

### Monitoring Endpoints
- `GET /health` - Health check endpoint
- `GET /metrics` - Application metrics (Prometheus format)

## 🤝 Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Future Enhancements

### Short-term
- [ ] Add user authentication
- [ ] Implement payment processing
- [ ] Add email notifications
- [ ] Support for product images

### Long-term
- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] AI-powered bid suggestions
- [ ] Multi-language support

## 📞 Support
For support, please open an issue in the GitHub repository or contact the development team at [your-email@example.com](mailto:your-email@example.com).

---
Built with ❤️ by the OmniAuction Team
