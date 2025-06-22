# OmniAuction Prototype — Instructions

## Quick Start

### 1. Install Requirements
```bash
pip install streamlit
```

### 2. Run the Command-Line Auction Agent
```bash
python omni/auction_agent.py
```

#### Example CLI Commands
- `list` — Show all auction items
- `info iphone` — Show info for a product (e.g., iPhone)
- `bid 1200 on iphone` — Place a bid
- `help` — Show available commands
- `exit` — Quit the program

### 3. Run the Streamlit Dashboard
```bash
streamlit run omni/auction_dashboard.py
```
- Select a product from the dropdown at the top.
- View product details and recent bidding history.
- Enter your name and bid amount, then click "Place Bid".
- Success or error messages will appear below the bid form.

## Troubleshooting
- **Bids not updating?**
  - Make sure you are using the latest Streamlit version (`pip install --upgrade streamlit`).
  - The dashboard uses session state to persist auction data during your session.
- **Messages not showing after bid?**
  - Messages are stored in session state and shown after rerun. If you don't see them, check your Streamlit version and browser refresh.

## Demo Tips
- Show the CLI and dashboard side by side for comparison.
- Demonstrate placing a bid and seeing the update in real time.
- Highlight the in-memory nature (data resets on restart).
- Mention that the final product will have persistent storage, real-time updates, and a more advanced UI/UX.

## Prototype Reminder
This is a prototype for demonstration and ideation. The final version will look and function very differently, with possible web/mobile/voice integration, persistent storage, and more advanced features.
