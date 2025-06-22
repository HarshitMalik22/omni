# OmniAuction Prototype

## Overview
OmniAuction is a prototype for a real-time auction system, designed to demonstrate core auction logic, user interaction, and extensibility. This prototype features:
- Command-line interface (CLI) for text-based interaction
- A simple web dashboard built with Streamlit
- (Optional) Voice simulation layer for conversational flow (text-based)
- In-memory auction logic with products, bidding, and history

## Features
- List all auction items with current highest bids and time remaining
- View detailed product information and bidding history
- Place bids with validation (must be higher than current bid, auction must be active)
- Simple, extensible code structure for rapid prototyping

## Requirements
- Python 3.8+
- [Streamlit](https://streamlit.io/) (`pip install streamlit`)

## Installation
1. Clone this repository or copy the `omni/` folder to your project directory.
2. Install dependencies:
   ```bash
   pip install streamlit
   ```

## How to Run

### 1. Command-Line Interface (CLI)
Run the auction agent in your terminal:
```bash
python omni/auction_agent.py
```
- Use commands like `list`, `info [product]`, `bid [amount] on [product]`, `help`, and `exit`.

### 2. Streamlit Dashboard
Launch the web dashboard:
```bash
streamlit run omni/auction_dashboard.py
```
- Select a product from the dropdown.
- View product details and bidding history.
- Place a bid using the form.
- Success/error messages are shown after bidding.

### 3. Voice Simulation (Text-Based)
If present, run:
```bash
python omni/voice_simulation.py
```
- Simulates a voice assistant using text prompts and responses.

## File Structure
- `auction_agent.py` — Core auction logic and CLI
- `auction_dashboard.py` — Streamlit dashboard for web-based interaction
- `voice_simulation.py` — (Optional) Text-based voice simulation
- `README.md` — This file

## Prototype Limitations
- All data is in-memory; no persistence between runs
- No real-time multi-user support
- No authentication or user management
- UI is basic and for demonstration only
- Voice simulation is text-only (no speech recognition or synthesis)

## Future Directions
The final version will look and function very differently, potentially including:
- Persistent storage (database)
- Real-time web or mobile interface
- True voice assistant integration
- User authentication and profiles
- Enhanced UI/UX and security

---
This prototype is for demonstration and ideation. Feedback and contributions are welcome!
