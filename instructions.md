# 🧠 Project Instructions: Voice Agent for Real-Time Auction (OmniDimension Only)

## ✅ Objective

Build a voice agent using **OmniDimension** that allows a user to:

1. Participate in a real-time auction using voice
2. Listen to product details, time left, and current bid
3. Place a bid by voice if the amount is higher
4. Get feedback through voice responses

All functionality must be self-contained within **OmniDimension** using its built-in memory, tools, and capabilities — **no external APIs or services**.

---

## 🧱 Data Model (Store In Memory or OmniDimension Table)

Each product must include:
- `id`
- `name`
- `description`
- `current_highest_bid`
- `auction_end_time` (simulate countdown)
- `bidding_history` (list of bids with user, amount, timestamp)

---

## 🗣️ Voice Agent Requirements

### The voice agent must:
1. Welcome the user
2. List available auction items by voice
3. Allow queries like:
   - “What’s the current bid on the iPhone?”
   - “Tell me about the laptop”
4. Understand bid commands:
   - “Place a bid of 4000 on iPhone”
   - “Bid 6000 for the MacBook”
5. Validate:
   - Auction is still running
   - Bid is higher than current
6. Store bid in memory
7. Reply with confirmation or failure by voice

---

## 💾 Internal State

Use OmniDimension’s internal data structures to simulate:
- Product catalog (array or table)
- Current auction timers (simplified or countdown-based)
- Bidding history tracking

No external file storage, no database, no API — everything should be **in-memory within OmniDimension**.

---

## 🧪 Voice Testing (Simulated)

If voice is not available, simulate the interaction using:
- Text input/output
- Manual triggers or test flows

---

## ⚠️ Rules for Windsurf

- Do not use external APIs, servers, or databases
- Do not create frontend or dashboard
- All logic, data, and interaction must remain inside OmniDimension
- Stick exactly to what’s written here — no additional features or UI

---

## ✅ Completion Checklist

- [ ] Voice agent runs in OmniDimension only
- [ ] Product list and bids are handled internally
- [ ] User can hear product info and place bids
- [ ] All bid logic and history are stored in memory
