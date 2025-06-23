import os
import json
import asyncio
import websockets
from typing import Dict, Optional, List
import requests
from datetime import datetime
import logging
import speech_recognition as sr
from gtts import gTTS
import pygame
import io
import time
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000/api"

@dataclass
class AuctionItem:
    id: str
    name: str
    current_highest_bid: float
    time_remaining: str
    description: str

class VoiceAgent:
    def __init__(self, use_voice=False):
        self.current_state = "INITIAL"
        self.context = {
            "current_product": None,
            "last_products_list": [],
            "user_name": None,
            "last_bid_amount": None
        }
        self.websocket = None
        self.use_voice = use_voice
        self.recognizer = sr.Recognizer() if use_voice else None
        pygame.mixer.init()
        
    def speak(self, text):
        """Convert text to speech and play it"""
        if not self.use_voice:
            print(f"Agent: {text}")
            return
            
        print(f"Agent: {text}")
        try:
            # Convert text to speech
            tts = gTTS(text=text, lang='en')
            audio_data = io.BytesIO()
            tts.write_to_fp(audio_data)
            audio_data.seek(0)
            
            # Play the audio
            pygame.mixer.music.load(audio_data, 'mp3')
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            print(f"(Couldn't speak: {e})")
    
    def listen(self):
        """Listen for voice input and return the recognized text"""
        if not self.use_voice:
            return input("You: ")
            
        with sr.Microphone() as source:
            print("Listening... (speak now)")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text.lower()
            except sr.WaitTimeoutError:
                print("Listening timed out. Please try again.")
                return ""
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that. Could you please repeat?")
                return ""
            except Exception as e:
                print(f"Error in speech recognition: {e}")
                return ""
    
    async def connect_to_websocket(self):
        """Connect to the WebSocket server for real-time updates"""
        try:
            self.websocket = await websockets.connect("ws://localhost:8000/ws")
            logger.info("Connected to WebSocket server")
            # Start listening for updates in the background
            asyncio.create_task(self.listen_for_updates())
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
    
    async def listen_for_updates(self):
        """Listen for real-time updates from the WebSocket"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                logger.info(f"Received update: {data}")
                # Handle different types of updates
                if data.get('type') == 'bid_placed':
                    await self.handle_bid_update(data)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed, attempting to reconnect...")
            await asyncio.sleep(5)  # Wait before reconnecting
            await self.connect_to_websocket()
    
    async def handle_bid_update(self, data: Dict):
        """Handle incoming bid updates"""
        product_id = data.get('product_id')
        user = data.get('user')
        amount = data.get('amount')
        
        # Only notify if it's not the current user
        if user != self.context.get('user_name'):
            product = await self.get_product_by_id(product_id)
            if product:
                # In a real implementation, you would use TTS to announce this
                print(f"\n[SYSTEM] New bid on {product.name}: ${amount:.2f} by {user}\n")
    
    async def get_products(self) -> List[AuctionItem]:
        """Fetch all available auction items"""
        try:
            response = requests.get(f"{API_BASE_URL}/products")
            response.raise_for_status()
            products = response.json()
            
            # Cache the products for reference
            self.context["last_products_list"] = [
                AuctionItem(
                    id=p["id"],
                    name=p["name"],
                    current_highest_bid=p["current_highest_bid"],
                    time_remaining=p["time_remaining"],
                    description=p["description"]
                ) for p in products
            ]
            return self.context["last_products_list"]
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            return []
    
    async def get_product_by_id(self, product_id: str) -> Optional[AuctionItem]:
        """Fetch a specific product by ID"""
        try:
            response = requests.get(f"{API_BASE_URL}/products/{product_id}")
            response.raise_for_status()
            p = response.json()
            return AuctionItem(
                id=p["id"],
                name=p["name"],
                current_highest_bid=p["current_highest_bid"],
                time_remaining=p["time_remaining"],
                description=p["description"]
            )
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {e}")
            return None
    
    async def place_bid(self, product_id: str, amount: float, user: str) -> Dict:
        """Place a bid on a product"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/bids",
                json={"product_id": product_id, "user": user, "amount": amount}
            )
            response.raise_for_status()
            
            # Update context
            self.context["last_bid_amount"] = amount
            
            return {
                "success": True,
                "message": response.json().get("message", "Bid placed successfully")
            }
        except requests.exceptions.HTTPError as e:
            error_msg = str(e.response.json().get("detail", "Failed to place bid"))
            return {"success": False, "message": error_msg}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    async def process_voice_command(self, command: str) -> str:
        """Process voice commands and return a response"""
        command = command.lower().strip()
        
        # Greeting/Initial state
        if any(word in command for word in ["hello", "hi", "hey"]):
            return "Hello! Welcome to OmniAuction. You can ask me to list available items, get details about a product, or place a bid."
        
        # List products
        list_commands = ["list", "show", "what's available", "what do you have", "what items", "auction items"]
        if any(cmd in command for cmd in list_commands):
            try:
                products = await self.get_products()
                if not products:
                    return "I couldn't find any products available for auction right now."
                
                # Store products in context for reference
                self.context["last_products_list"] = products
                
                response = "Here are the items available for auction:\n"
                for i, product in enumerate(products, 1):
                    response += f"{i}. {product.name} - Current bid: ${product.current_highest_bid:.2f} - {product.time_remaining}\n"
                response += "\nYou can say 'Tell me about item X' or 'Show me details about [product name]' to get more information."
                return response
            except Exception as e:
                logger.error(f"Error listing products: {e}")
                return "I'm having trouble fetching the product list. Please try again in a moment."
        
        # Get product details
        detail_phrases = ["tell me about", "details about", "info on", "show me", "what is", "what's"]
        if any(phrase in command for phrase in detail_phrases):
            try:
                # Try to extract product name or number
                product_ref = None
                
                # Handle "item 1" or "number 1" format
                if ("item" in command or "number" in command) and any(char.isdigit() for char in command):
                    try:
                        idx_part = command.split("item")[1] if "item" in command else command.split("number")[1]
                        idx = int(''.join(filter(str.isdigit, idx_part.split()[0]))) - 1
                        if 0 <= idx < len(self.context.get("last_products_list", [])):
                            product_ref = self.context["last_products_list"][idx].name
                    except (IndexError, ValueError, AttributeError) as e:
                        logger.debug(f"Error parsing item number: {e}")
                
                # If no item number found, try to match product names using more flexible matching
                if not product_ref and self.context.get("last_products_list"):
                    command_lower = command.lower()
                    
                    # First, try exact match of product names
                    for product in self.context["last_products_list"]:
                        if product.name.lower() in command_lower:
                            product_ref = product.name
                            break
                    
                    # If no exact match, try partial matching of product name parts
                    if not product_ref:
                        for product in self.context["last_products_list"]:
                            # Split product name into words and check if any word is in the command
                            product_terms = [term for term in product.name.lower().split() if len(term) > 3]  # Only consider words longer than 3 chars
                            if any(term in command_lower for term in product_terms):
                                product_ref = product.name
                                break
                    
                    # If still no match, try to find the most similar product name
                    if not product_ref and len(self.context["last_products_list"]) > 0:
                        from difflib import get_close_matches
                        all_product_names = [p.name.lower() for p in self.context["last_products_list"]]
                        # Get words from command that might be product names
                        command_terms = [word for word in command_lower.split() if len(word) > 3]
                        for term in command_terms:
                            matches = get_close_matches(term, all_product_names, n=1, cutoff=0.6)
                            if matches:
                                product_ref = matches[0]
                                break
                
                if not product_ref:
                    return "I'm not sure which product you're asking about. Please say something like 'Tell me about the iPhone' or 'Show me item 1'."
                
                # Find the product in our list
                product = next((p for p in self.context["last_products_list"] 
                              if product_ref.lower() in p.name.lower()), None)
                
                if not product:
                    # If we still can't find it, try to fetch it by name
                    products = await self.get_products()
                    product = next((p for p in products if product_ref.lower() in p.name.lower()), None)
                    
                    if not product:
                        return f"I couldn't find details for '{product_ref}'. Please check the product name and try again."
                
                # Update context with the current product
                self.context["current_product"] = product
                
                # Format the response
                return (
                    f"{product.name.upper()}\n"
                    f"{product.description}\n"
                    f"Current highest bid: ${product.current_highest_bid:,.2f}\n"
                    f"Time remaining: {product.time_remaining}\n\n"
                    f"Would you like to place a bid? If yes, just say 'Bid $X' where X is your bid amount."
                )
                
            except Exception as e:
                logger.error(f"Error getting product details: {e}")
                return "I'm having trouble getting the product details. Please try again in a moment."
        
        # Place a bid
        bid_phrases = ["bid", "offer", "place a bid", "i bid", "i'll bid", "i want to bid"]
        if any(phrase in command for phrase in bid_phrases):
            try:
                if not self.context.get("current_product"):
                    # If no current product, try to find one in the command
                    if self.context.get("last_products_list"):
                        for product in self.context["last_products_list"]:
                            if any(term in command for term in product.name.lower().split()):
                                self.context["current_product"] = product
                                break
                    
                    if not self.context.get("current_product"):
                        return "Please select a product first by saying 'Tell me about [product name]'."
                
                # Extract bid amount
                amount = None
                # First try to find a number with $ sign
                for word in command.split():
                    if '$' in word and word.replace('$', '').replace(',', '').replace('.', '').isdigit():
                        amount = float(word.replace('$', '').replace(',', ''))
                        break
                
                # If no $ amount, look for any number that could be a bid
                if amount is None:
                    for word in command.split():
                        if word.replace(',', '').replace('.', '').isdigit():
                            amount = float(word.replace(',', ''))
                            break
                
                if amount is None:
                    return f"I didn't catch the bid amount. Please specify an amount, for example: 'Bid $1200' or 'I want to bid 1200'."
                
                # Get the product
                product = self.context["current_product"]
                
                # Check if the bid is higher than current
                if amount <= product.current_highest_bid:
                    return f"Your bid of ${amount:,.2f} must be higher than the current highest bid of ${product.current_highest_bid:,.2f}."
                
                # Place the bid
                result = await self.place_bid(product.id, amount, "User")
                
                if result.get("success", False):
                    return f"Your bid of ${amount:,.2f} on {product.name} has been placed! {result.get('message', '')}"
                else:
                    return f"I couldn't place your bid: {result.get('message', 'Please try again.')}"
                
            except Exception as e:
                logger.error(f"Error placing bid: {e}")
                return "I'm having trouble placing your bid. Please try again in a moment."
            result = await self.place_bid(
                self.context["current_product"].id,
                amount,
                self.context["user_name"]
            )
            
            if result["success"]:
                return f"Your bid of ${amount:.2f} has been placed! {result['message']}"
            else:
                return f"I couldn't place your bid: {result['message']}"
        
        # Help
        elif "help" in command:
            return (
                "I can help you with the following:\n"
                "- 'List items' - Show all available auction items\n"
                "- 'Tell me about [item]' - Get details about a specific item\n"
                "- 'Bid [amount] on [item]' - Place a bid on an item\n"
                "- 'What's my status?' - Check your bidding status\n"
                "- 'Help' - Show this help message"
            )
        
        # Fallback
        else:
            return "I'm not sure how to help with that. You can ask me to list items, get details about a product, or place a bid. Say 'help' for more options."

async def main():
    # Check if voice mode should be enabled
    use_voice = "--voice" in ' '.join(os.sys.argv[1:])
    
    if use_voice:
        print("Voice mode enabled. Please ensure your microphone is connected and working.")
    
    agent = VoiceAgent(use_voice=use_voice)
    
    try:
        await agent.connect_to_websocket()
        
        # Print header
        print("\n" + "="*50)
        print("OmniAuction Voice Agent" + (" (Voice Mode)" if use_voice else ""))
        print("Type 'exit' to quit")
        print("="*50 + "\n")
        
        # Single welcome message with instructions
        welcome_msg = "Hello! I'm your auction assistant. How can I help you today?"
        if use_voice:
            welcome_msg += " You can say things like 'list items', 'tell me about the iPhone', or 'bid one thousand dollars on the iPhone'"
        else:
            print("You can type commands like 'list items', 'tell me about item 1', or 'bid $1000 on iPhone'")
        
        agent.speak(welcome_msg)
        
        while True:
            try:
                if use_voice:
                    agent.speak("What would you like to do?")
                    command = agent.listen()
                    if not command or not command.strip():
                        continue
                else:
                    command = input("\nYou: ").strip()
                    if not command:
                        continue
                
                if command.lower() in ["exit", "quit", "bye", "goodbye"]:
                    agent.speak("Goodbye! Thank you for using OmniAuction.")
                    print("\nGoodbye!")
                    break
                    
                response = await agent.process_voice_command(command)
                agent.speak(response)
                
                # Small delay to prevent rapid repeating
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                agent.speak("Sorry, I encountered an error. Let's try that again.")
                continue
            
    except KeyboardInterrupt:
        agent.speak("Shutting down the auction assistant.")
        print("\nShutting down...")
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        agent.speak("I'm sorry, something went wrong. Please try again.")
        print(error_msg)
        logger.error(error_msg)
    finally:
        if agent.websocket:
            await agent.websocket.close()

if __name__ == "__main__":
    asyncio.run(main())
