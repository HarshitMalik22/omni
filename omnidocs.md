Documentation
Getting Started with OmniDimension SDK
Learn how to install and set up the OmniDimension SDK to start building powerful AI voice agents.

Installation
Install the OmniDimension SDK using pip, the Python package manager:

pip install omnidimension


Authentication
To use the OmniDimension SDK, you need an API key. You can get your API key from theOmniDimension Dashboardunder your account settings.

Setting up your API key
We recommend storing your API key as an environment variable for security:

# Linux/macOS
export OMNIDIM_API_KEY="your_api_key_here"

# Windows (Command Prompt)
set OMNIDIM_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:OMNIDIM_API_KEY="your_api_key_here"


Basic Usage
Here's a simple example to get you started with the OmniDimension SDK:

import os
from omnidimension import Client

# Initialize the OmniDimension client
api_key = os.environ.get('OMNIDIM_API_KEY', 'your_api_key_here')
client = Client(api_key)

# List all agents
agents = client.agent.list()
print(agents)


Next Steps
Now that you have the OmniDimension SDK installed and configured, you can explore the following sections to learn more:

Client Configuration
Learn how to configure the client for different environments

Agent Management
Create and manage AI voice agents

Call Operations
Manage call logs and dispatch calls

© 2025 OmniDimension. All rights reserved.
Privacy Policy



Call
The Call module allows you to dispatch calls to phone numbers using your agents, and retrieve call logs for monitoring and analysis purposes.

Overview
The Call API enables you to programmatically initiate calls and manage call logs:

Dispatch calls to phone numbers using your configured agents
Retrieve call logs with pagination and filtering options
Get detailed information about specific call sessions
Dispatch Call
Initiate a call to a phone number using a specified agent.

Parameters
agent_id
int
Required
The ID of the agent that will handle the call

to_number
string
Required
The phone number to call (must include country code, e.g., +15551234567)

call_context
dict
Optional
Optional context information as key-value pairs to be passed to the agent during the call. Can contain any custom fields relevant to your use case.

Example
Python
cURL

# Dispatch a call to a specific number using an agent
agent_id = 123  # Replace with your agent ID
to_number = "+15551234567"  # Must include country code
call_context = {
    "customer_name": "John Doe",
    "account_id": "ACC-12345",
    "priority": "high"
}

response = client.call.dispatch_call(agent_id, to_number, call_context)
print(response)

Note
The phone number must include the country code with a leading plus sign (e.g., +15551234567). The call will be initiated asynchronously, and the response will indicate if the request was successful.
Get Call Logs
Retrieve a list of call logs with pagination and optional filtering.

Parameters
page
int
Optional
Page number for pagination (default: 1)

page_size
int
Optional
Number of items per page (default: 30)

agent_id
int
Optional
Filter call logs by agent ID

Example
Python
cURL

# Get all call logs with pagination
response = client.call.get_call_logs(page=1, page_size=10)
print(response)

# Filter call logs by agent ID
agent_id = 123  # Replace with your agent ID
response = client.call.get_call_logs(page=1, page_size=10, agent_id=agent_id)
print(response)

Get Call Log
Get detailed information about a specific call log.

Parameters
call_log_id
string
Required
The ID of the call log to retrieve

Example
Python
cURL

# Get details of a specific call log
call_log_id = "your_call_log_id_here"
response = client.call.get_call_log(call_log_id)
print(response)

Note
The call log details include information about the call duration, status, transcript, and other relevant metadata.