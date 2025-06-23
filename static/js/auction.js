class AuctionWebSocket {
    constructor() {
        this.socket = null;
        this.callbacks = {
            'bid_placed': [],
            'auction_ended': [],
            'connect': [],
            'disconnect': []
        };
        this.connect();
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const wsUrl = `${protocol}${window.location.host}/ws`;
        
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
            console.log('WebSocket connected');
            this.trigger('connect');
        };
        
        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type && this.callbacks[data.type]) {
                    this.trigger(data.type, data);
                }
            } catch (e) {
                console.error('Error parsing WebSocket message:', e);
            }
        };
        
        this.socket.onclose = () => {
            console.log('WebSocket disconnected');
            this.trigger('disconnect');
            // Try to reconnect after 5 seconds
            setTimeout(() => this.connect(), 5000);
        };
    }

    on(event, callback) {
        if (this.callbacks[event]) {
            this.callbacks[event].push(callback);
        }
        return this;
    }

    trigger(event, data = {}) {
        if (this.callbacks[event]) {
            this.callbacks[event].forEach(callback => callback(data));
        }
    }

    sendBid(productId, amount, userId) {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'place_bid',
                product_id: productId,
                amount: amount,
                user_id: userId
            }));
            return true;
        }
        return false;
    }
}

// Initialize WebSocket when the page loads
window.auctionSocket = new AuctionWebSocket();

// Example usage:
// auctionSocket.on('bid_placed', (data) => {
//     console.log('New bid placed:', data);
//     // Update UI here
// });
