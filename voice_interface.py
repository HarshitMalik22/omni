import asyncio
import logging
from voice_agent import VoiceAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    print("🔊 Starting OmniAuction Voice Assistant...")
    print("🎤 Speak naturally to interact with the auction system")
    print("   Say 'help' to see what you can do")
    print("   Press Ctrl+C to exit\n")
    
    try:
        # Initialize the voice agent
        agent = VoiceAgent(use_voice=True)
        
        # Start the WebSocket connection
        await agent.connect_to_websocket()
        
        # Start the interactive voice session
        await agent.start_interaction()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print("\n❌ An error occurred. Please check the logs for details.")

if __name__ == "__main__":
    asyncio.run(main())
