import asyncio
import websockets

async def test_websocket():
    try:
        async with websockets.connect('ws://localhost:8000/ws') as websocket:
            print("Successfully connected to WebSocket!")
            # Send a test message
            await websocket.send("Hello, WebSocket!")
            # Wait for a response
            response = await websocket.recv()
            print(f"Received: {response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test_websocket())
