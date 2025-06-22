import streamlit as st
from auction_agent import AuctionAgent

st.set_page_config(page_title="Auction Dashboard", layout="centered")
st.title("🛒 OmniAuction Dashboard")

if "agent" not in st.session_state:
    st.session_state.agent = AuctionAgent()
agent = st.session_state.agent

# Product selection
product_names = list(agent.products.keys())
product_display_names = [agent.products[k].name for k in product_names]
selected_display = st.selectbox("Select a product", product_display_names)
selected_key = product_names[product_display_names.index(selected_display)]
product = agent.products[selected_key]

# Main: Product list
st.header("Current Auction Items")
for p in agent.products.values():
    st.write(f"**{p.name}**: ${p.current_highest_bid:.2f} ({p.time_remaining()})")

# Selected product details (shown when a product is selected)
st.subheader(f"Details for {product.name}")
st.write(product.description)
st.write(f"Current Highest Bid: **${product.current_highest_bid:.2f}**")
st.write(product.time_remaining())

# Bidding history
if product.bidding_history:
    st.markdown("**Bidding History:**")
    for bid in reversed(product.bidding_history[-5:]):
        st.write(f"{bid.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {bid.user}: ${bid.amount:.2f}")
else:
    st.write("No bids yet.")

# Place a bid
st.subheader("Place a Bid")
with st.form(key="bid_form"):
    user = st.text_input("Your Name", value="User")
    amount = st.number_input("Bid Amount", min_value=0.0, step=1.0, value=product.current_highest_bid+1)
    submit = st.form_submit_button("Place Bid")
    if submit:
        result = agent.place_bid(selected_key, amount, user)
        st.session_state['bid_result'] = result
        st.rerun() 