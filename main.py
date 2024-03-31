import requests
import streamlit as st

# Set the Streamlit page layout to wide mode
st.set_page_config(layout="wide")

# Initialize session state variables
if 'data_loaded' not in st.session_state:
    st.session_state['data_loaded'] = False
if 'gcp_auth_token' not in st.session_state:
    st.session_state['gcp_auth_token'] = ''

# Function to call the FastAPI endpoint to load data from GitHub
def load_data(github_url, access_token, gcp_auth_token):
    # The URL of your FastAPI endpoint
    api_url = "http://127.0.0.1:8000/load-repo"
    headers = {"Authorization": f"Bearer {gcp_auth_token}"}
    payload = {
        "github_url": github_url,
        "access_token": access_token,
        "gcp_auth_token": gcp_auth_token
    }
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        if response.status_code == 200:
            return True, "Data loaded successfully!"
        else:
            return False, response.text
    except requests.exceptions.RequestException as e:
        # Handle connection errors
        return False, str(e)

# Function to call the FastAPI endpoint for the chat functionality
def chat_with_code(query, gcp_auth_token):
    # The URL of your FastAPI endpoint for chatting
    chat_api_url = "http://127.0.0.1:8000/chat-code"
    headers = {"Authorization": f"Bearer {gcp_auth_token}"}
    payload = {
        "query": query,
        "gcp_auth_token": gcp_auth_token
    }
    try:
        response = requests.post(chat_api_url, json=payload, headers=headers)
        if response.status_code == 200:
            # Return the response from the chat API (assuming it's a text response)
            return response.text
        else:
            return "Failed to get a response: " + response.text
    except requests.exceptions.RequestException as e:
        # Handle connection errors
        return "Chat Error: " + str(e)

# Set up the layout using columns to align items
col1, col2 = st.columns(2)

with col1:
    st.header('Web UI')

    # Input for GitHub Repository URL
    repo_url = st.text_input('GitHub Repository URL')

    # Input for Personal Access Token
    access_token = st.text_input('Personal Access Token', type="password")

    # Input for GCP Auth Token
    gcp_auth_token = st.text_input('GCP Auth Token', type="password")
    st.session_state['gcp_auth_token'] = gcp_auth_token  # Store the token in the session state

    # Load button
    load_button_clicked = st.button('Load', disabled=not(repo_url and access_token and gcp_auth_token))
    if load_button_clicked:
        # Call function to load data
        data_loaded, message = load_data(repo_url, access_token, gcp_auth_token)
        st.session_state['data_loaded'] = data_loaded
        if data_loaded:
            st.success(message)
        else:
            st.error(message)

with col2:
    st.header('Chat with your code! </>')

# Chatbox functionality
if st.session_state['data_loaded']:
    # Display the chat box
    user_query = st.text_area('What\'s up?', height=100)
    send_button_clicked = st.button('➤', help='Send')
    if send_button_clicked and user_query:
        # Use the GCP auth token stored in the session state
        chat_response = chat_with_code(user_query, st.session_state['gcp_auth_token'])
        st.write(chat_response)
    elif send_button_clicked and not user_query:
        st.error("Please enter a query to chat.")
