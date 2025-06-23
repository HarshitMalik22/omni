import streamlit as st
import requests
import json
import time
import asyncio
import websockets
from datetime import datetime
import plotly.express as px
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import threading
from queue import Queue
import json
import os
from omnidimension import Client

# Initialize OmniDimension client
try:
    OMNIDIM_API_KEY = st.secrets.get('OMNIDIM_API_KEY', os.environ.get('OMNIDIM_API_KEY'))
    if OMNIDIM_API_KEY:
        print("\n=== INITIALIZING OMNIDIMENSION CLIENT ===")
        print(f"Using API Key: {OMNIDIM_API_KEY[:5]}...{OMNIDIM_API_KEY[-5:]}")
        
        # Initialize client with just the API key
        omnidim_client = Client(OMNIDIM_API_KEY)
        
        OMNIDIM_AGENT_ID = int(st.secrets.get('OMNIDIM_AGENT_ID', os.environ.get('OMNIDIM_AGENT_ID', '1')))
        print(f"Using Agent ID: {OMNIDIM_AGENT_ID} (type: {type(OMNIDIM_AGENT_ID).__name__})")
        print("OmniDimension client initialized successfully")
    else:
        st.warning("OmniDimension API key not found. Voice features will be disabled.")
        omnidim_client = None
except Exception as e:
    error_msg = f"Failed to initialize OmniDimension client: {str(e)}"
    st.error(error_msg)
    print(f"!!! ERROR: {error_msg}")
    omnidim_client = None

# Global queue for WebSocket messages
ws_messages = Queue()

# WebSocket client
class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.ws = None
        self.connected = False
        self.should_stop = False
        self.thread = None

    async def connect(self):
        while not self.should_stop:
            try:
                async with websockets.connect(self.uri, ping_interval=None) as ws:
                    self.ws = ws
                    self.connected = True
                    st.rerun()  # Rerun to update connection status
                    
                    async for message in ws:
                        if self.should_stop:
                            break
                        try:
                            data = json.loads(message)
                            ws_messages.put(data)
                            st.rerun()  # Rerun to process new message
                        except json.JSONDecodeError:
                            print(f"Failed to parse message: {message}")
                            
            except Exception as e:
                print(f"WebSocket error: {e}")
                self.connected = False
                st.rerun()  # Rerun to update connection status
                await asyncio.sleep(5)  # Reconnect after 5 seconds

    def start(self):
        def run():
            asyncio.set_event_loop(asyncio.new_event_loop())
            asyncio.get_event_loop().run_until_complete(self.connect())
        
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def stop(self):
        self.should_stop = True
        if self.ws:
            asyncio.get_event_loop().run_until_complete(self.ws.close())
        if self.thread:
            self.thread.join()

# Initialize WebSocket client
ws_uri = f"ws{'s' if 'https' in st.secrets.get('SERVER_URL', '') else ''}://{st.secrets.get('SERVER_URL', 'localhost:8000').replace('http://', '').replace('https://', '')}/ws"
if 'ws_client' not in st.session_state:
    st.session_state.ws_client = WebSocketClient(ws_uri)
    st.session_state.ws_client.start()

# Configuration
API_BASE_URL = "http://localhost:8000/api"

# Set page config
st.set_page_config(
    page_title="🛒 OmniAuction Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding: 2rem 5rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        border-radius: 20px;
        padding: 0.5rem 1rem;
    }
    .stNumberInput>div>div>input {
        border-radius: 20px;
        padding: 0.5rem 1rem;
    }
    .product-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .product-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .bid-history {
        max-height: 300px;
        overflow-y: auto;
        padding: 1rem;
        background: #f9f9f9;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def fetch_products():
    try:
        response = requests.get(f"{API_BASE_URL}/products")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching products: {str(e)}")
        return []

def fetch_product_details(product_id):
    try:
        response = requests.get(f"{API_BASE_URL}/products/{product_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching product details: {str(e)}")
        return None

def place_bid(product_id, user, amount, voice_call=False):
    try:
        response = requests.post(
            f"{API_BASE_URL}/bids",
            json={"product_id": product_id, "user": user, "amount": amount, "voice_call": voice_call}
        )
        response.raise_for_status()
        
        # Show a success toast
        toast_msg = f"✅ Bid of ${amount} placed successfully!"
        if voice_call:
            toast_msg += " 🎙️"
        st.toast(toast_msg)
        
        return True, response.json()["message"]
    except requests.exceptions.HTTPError as e:
        error_msg = str(e.response.json().get("detail", "An error occurred"))
        st.toast(f"❌ {error_msg}", icon="❌")
        return False, error_msg
    except Exception as e:
        error_msg = str(e)
        st.toast(f"❌ {error_msg}", icon="❌")
        return False, error_msg

def make_voice_call(phone_number, product_name, current_bid):
    """Initiate a voice call using OmniDimension Call API
    
    Args:
        phone_number (str): Phone number to call (will be formatted with country code if needed)
        product_name (str): Name of the product for the call context
        current_bid (float): Current bid amount for the product
        
    Returns:
        tuple: (success: bool, message: str)
    """
    if not omnidim_client:
        error_msg = "OmniDimension client not initialized. Please check your API key."
        st.error(error_msg)
        return False, error_msg
    
    try:
        # Clean and validate phone number
        phone_number = str(phone_number).strip().replace(" ", "")  # Remove any spaces
        if not phone_number:
            return False, "Phone number cannot be empty"
            
        # Ensure country code is present (default to +91 for India if not provided)
        if not phone_number.startswith('+'):
            phone_number = f"+91{phone_number}"
        
        # Prepare call context
        call_context = {
            "product_name": str(product_name) if product_name else "Unknown Product",
            "current_bid": str(current_bid) if current_bid is not None else "0",
            "action": "place_bid"
        }
        
        # Make the API call
        try:
            if not hasattr(omnidim_client, 'call') or not hasattr(omnidim_client.call, 'dispatch_call'):
                return False, "OmniDimension client is not properly configured for making calls"
            
            # Log the request details for debugging
            print("\n=== MAKING API REQUEST ===")
            print(f"Agent ID: {OMNIDIM_AGENT_ID}")
            print(f"To Number: {phone_number}")
            print(f"Call Context: {json.dumps(call_context, indent=2)}")
            
            # Make the API call with positional arguments as expected by the API
            response = omnidim_client.call.dispatch_call(
                OMNIDIM_AGENT_ID,  # agent_id as first positional argument
                phone_number,      # to_number as second positional argument
                call_context       # call_context as third positional argument
            )
            
            print("\n=== API RESPONSE ===")
            print(f"Response type: {type(response)}")
            print(f"Response content: {response}")
            
            # Handle response (could be dict or response object)
            if isinstance(response, dict):
                if response.get('success', False):
                    success_msg = "✅ Voice call initiated successfully! Please wait for the call."
                    st.success(success_msg)
                    return True, success_msg
                else:
                    error_msg = response.get('message', 'Failed to initiate call - no error details')
            elif hasattr(response, 'json'):
                response_data = response.json()
                if response.status_code == 200 or response_data.get('success', False):
                    success_msg = "✅ Voice call initiated successfully! Please wait for the call."
                    st.success(success_msg)
                    return True, success_msg
                else:
                    error_msg = response_data.get('message', 'Failed to initiate call - no error details')
            else:
                error_msg = f"Unexpected response format: {response}"
            
            st.error(f"❌ Call failed: {error_msg}")
            return False, error_msg
            
        except Exception as e:
            print("\n!!! API CALL FAILED !!!")
            print(f"Exception type: {type(e).__name__}")
            print(f"Error: {str(e)}")
            
            error_msg = f"API call failed: {str(e)}"
            
            # Log detailed error information
            if hasattr(e, 'response') and e.response is not None:
                print(f"\n=== ERROR RESPONSE DETAILS ===")
                print(f"Status Code: {getattr(e.response, 'status_code', 'N/A')}")
                print(f"Headers: {dict(getattr(e.response, 'headers', {}))}")
                
                try:
                    if hasattr(e.response, 'text'):
                        print(f"Response text: {e.response.text}")
                        error_msg = f"{error_msg}\nResponse: {e.response.text}"
                    
                    if hasattr(e.response, 'json'):
                        error_data = e.response.json()
                        print(f"Response JSON: {error_data}")
                        error_msg = error_data.get('detail', 
                                              error_data.get('message', 
                                                          error_msg))
                except Exception as parse_error:
                    print(f"Failed to parse error response: {str(parse_error)}")
                    error_msg = f"{error_msg} (Failed to parse error details)"
            
            return False, error_msg
            
    except Exception as e:
        error_msg = f"Error in make_voice_call: {str(e)}"
        st.error(f"❌ {error_msg}")
        return False, error_msg
        return False, error_msg

# Process WebSocket messages
def process_ws_messages():
    while not ws_messages.empty():
        message = ws_messages.get()
        if message.get('type') == 'bid_placed':
            st.toast(f"🚀 New bid: ${message['amount']} on {message.get('product_id', 'an item')} by {message.get('user', 'Someone')}")
        ws_messages.task_done()

# Main App
def main():
    st.title("🛒 OmniAuction Live Dashboard")
    
    # Show connection status
    ws_status = "🟢 Connected" if hasattr(st.session_state, 'ws_client') and st.session_state.ws_client.connected else "🔴 Disconnected"
    st.sidebar.markdown(f"### WebSocket Status: {ws_status}")
    
    # Process WebSocket messages
    process_ws_messages()
    
    # Fetch products
    products = fetch_products()
    
    if not products:
        st.warning("No products available for auction.")
        return
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("🏷️ Available Auctions")
        
        # Display product cards
        for product in products:
            with st.container():
                st.markdown(f"""
                <div class="product-card">
                    <h3>{product.get('name', 'Unnamed Product')}</h3>
                    <p>{product.get('description', 'No description available')}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.2em; font-weight: bold; color: #4CAF50;">
                            ${product.get('current_price', 0):,.2f}
                        </span>
                        <span style="color: #666;">
                            {product.get('time_remaining', 'N/A')}
                        </span>
                    </div>
                    <div style="margin-top: 10px; color: #666; font-size: 0.9em;">
                        {len(product.get('bids', []))} bids
                    </div>
                </div>
                """.format(
                    name=product['name'],
                    description=product['description'][:100] + ('...' if len(product['description']) > 100 else ''),
                    current_highest_bid=product['current_highest_bid'],
                    time_remaining=product['time_remaining'],
                    bids_count=product['bids_count']
                ), unsafe_allow_html=True)
        
        # Auto-refresh toggle
        st.markdown("---")
        auto_refresh = st.checkbox("Enable auto-refresh", value=True)
        if auto_refresh:
            st_autorefresh(interval=5000, key='data_refresh')
    
    with col2:
        if 'selected_product' not in st.session_state:
            st.session_state.selected_product = products[0]['id']
        
        # Product selector
        selected_product_id = st.selectbox(
            "Select a product to view details",
            [p['id'] for p in products],
            format_func=lambda x: next((p['name'] for p in products if p['id'] == x), ""),
            key="product_selector"
        )
        
        # Voice call section
        if omnidim_client:
            with st.expander("🔊 Voice Bid Assistant", expanded=False):
                st.write("Place a bid using our voice assistant")
                phone_number = st.text_input("Your Phone Number (with country code)", 
                                           placeholder="+1234567890",
                                           key="phone_number")
                
                if st.button("📞 Call Me to Place Bid"):
                    if not phone_number:
                        st.error("Please enter your phone number")
                    else:
                        product = next((p for p in products if p.get('id') == selected_product_id), None)
                        if product:
                            # Get the current price or default to 0 if not available
                            current_price = product.get('current_price', product.get('current_highest_bid', 0))
                            product_name = product.get('name', 'this item')
                            
                            with st.spinner("Initiating voice call..."):
                                success, message = make_voice_call(
                                    phone_number,
                                    product_name,
                                    current_price
                                )
                                if success:
                                    st.success("Voice call initiated! Please answer the call to place your bid.")
                                else:
                                    st.error(f"Failed to initiate call: {message}")
        
        # Get product details
        product = fetch_product_details(selected_product_id)
        
        if product:
            st.header(product['name'])
            st.markdown(f"*{product['description']}*")
            
            # Current bid and time remaining
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Current Highest Bid", f"${product['current_highest_bid']:,.2f}")
            with col_b:
                st.metric("Time Remaining", product['time_remaining'])
            
            # Bidding form
            st.subheader("Place a Bid")
            with st.form("bid_form"):
                user = st.text_input("Your Name", key="bidder_name")
                min_bid = product['current_highest_bid'] + 1
                amount = st.number_input(
                    "Bid Amount",
                    min_value=min_bid,
                    value=min_bid,
                    step=1.0
                )
                submit = st.form_submit_button("🚀 Place Bid")
                
                # Add voice call option
                use_voice = st.checkbox("Place bid via voice call", 
                                      help="Get a call to confirm and place your bid")
                
                if submit:
                    if not user:
                        st.error("Please enter your name")
                    elif use_voice and not st.session_state.get('phone_number'):
                        st.error("Please enter your phone number in the Voice Bid Assistant section")
                    else:
                        if use_voice and omnidim_client:
                            phone_number = st.session_state.get('phone_number')
                            if phone_number:
                                product = next((p for p in products if p['id'] == selected_product_id), None)
                                if product:
                                    product_name = product.get('name', 'this item')
                                    with st.spinner("Initiating voice call..."):
                                        success, message = make_voice_call(
                                            phone_number,
                                            product_name,
                                            amount
                                        )
                                        if success:
                                            st.success("Voice call initiated! Please answer to confirm your bid.")
                                        else:
                                            st.error(f"Failed to initiate call: {message}")
                        else:
                            success, message = place_bid(
                                selected_product_id,
                                user,
                                amount,
                                voice_call=use_voice
                            )
                        if success:
                            st.success(message)
                            st.balloons()
                        else:
                            st.error(message)
            
            # Bidding history with auto-update
            st.subheader("Bidding History")
            
            # Create a container for the history that we can update
            history_container = st.container()
            
            if product['bidding_history']:
                # Convert to DataFrame for better display
                history_df = pd.DataFrame(product['bidding_history'])
                history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
                
                # Add a visual indicator for the latest bid
                if not history_df.empty:
                    latest_bid = history_df.iloc[-1]
                    st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
                        <div style="font-weight: bold; color: #1f77b4;">
                            Latest Bid: ${latest_bid['amount']:.2f} by {latest_bid['user']}
                        </div>
                        <div style="font-size: 0.9em; color: #666;">
                            {latest_bid['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display as a table
                with history_container:
                    st.dataframe(
                        history_df[['timestamp', 'user', 'amount']].sort_values('timestamp', ascending=False),
                        column_config={
                            'timestamp': 'Time',
                            'user': 'Bidder',
                            'amount': st.column_config.NumberColumn(
                                'Amount',
                                format='$%.2f'
                            )
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                
                # Show bid history chart
                if len(history_df) > 1:
                    st.subheader("Bid History Trend")
                    fig = px.line(
                        history_df.sort_values('timestamp'),
                        x='timestamp',
                        y='amount',
                        title='Bid Amount Over Time',
                        labels={'timestamp': 'Time', 'amount': 'Bid Amount ($)'},
                        markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No bids placed yet. Be the first to bid!")

if __name__ == "__main__":
    main() 