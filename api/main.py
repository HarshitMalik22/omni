from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import os
import uvicorn
from auction_agent import AuctionAgent, Product, Bid

app = FastAPI(title="OmniAuction API",
             description="REST API for OmniAuction Voice Agent",
             version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.agent = AuctionAgent()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Models
class BidRequest(BaseModel):
    user: str
    amount: float
    product_id: str

class VoiceCommand(BaseModel):
    text: str
    session_id: str

# API Endpoints
@app.get("/api/products", response_model=List[Dict])
async def list_products():
    """Get list of all auction products"""
    return [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "current_highest_bid": product.current_highest_bid,
            "time_remaining": product.time_remaining(),
            "bids_count": len(product.bidding_history)
        }
        for product in manager.agent.products.values()
    ]

@app.get("/api/products/{product_id}", response_model=Dict)
async def get_product(product_id: str):
    """Get details of a specific product"""
    product = manager.agent._find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "current_highest_bid": product.current_highest_bid,
        "time_remaining": product.time_remaining(),
        "bids_count": len(product.bidding_history),
        "bidding_history": [
            {"user": bid.user, "amount": bid.amount, "timestamp": bid.timestamp.isoformat()}
            for bid in product.bidding_history[-10:]
        ]
    }

@app.post("/api/bids", status_code=201)
async def place_bid(bid: BidRequest):
    """Place a new bid on a product"""
    product = manager.agent._find_product(bid.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    result = manager.agent.place_bid(bid.product_id, bid.amount, bid.user)
    
    if result.startswith("Error"):
        raise HTTPException(status_code=400, detail=result)
    
    # Broadcast the new bid to all connected clients
    await manager.broadcast({
        "type": "bid_placed",
        "product_id": bid.product_id,
        "user": bid.user,
        "amount": bid.amount,
        "message": result
    })
    
    return {"status": "success", "message": result}

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back the received message
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
