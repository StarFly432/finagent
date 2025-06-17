import streamlit as st
import json
import requests
import uuid
from google.oauth2 import service_account
import google.auth.transport.requests

# Load secrets
PROJECT_ID = st.secrets["PROJECT_ID"]
LOCATION = st.secrets["LOCATION"]
REASONING_ENGINE_ID = st.secrets["REASONING_ENGINE_ID"]
SERVICE_ACCOUNT_JSON = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])

# API base
API_BASE = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}"

# UI
st.set_page_config(page_title="Vertex Agent Chat", layout="centered")
st.title("💬 Chat with Vertex AI Agent")

# Store session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Auth token
def get_access_token():
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_JSON,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return credentials.token

# Create a session
def create_session():
    access_token = get_access_token()
    url = f"{API_BASE}/sessions"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    session_uuid = str(uuid.uuid4())
    payload = {"sessionId": session_uuid}

    res = requests.post(url, headers=headers, json=payload)
    res.raise_for_status()
    session = res.json()
    return session["name"]  # Full session path

# Send a message
def send_input_to_agent(session_path, user_input):
    access_token = get_access_token()
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/{session_path}:interact"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "interactRequest": {
            "input": {"textInput": {"text": user_input}}
        }
    }
    res = requests.post(url, headers=headers, json=payload)
    res.raise_for_status()
    return res.json()

# User input
user_input = st.text_input("You:", "")

# Handle interaction
if st.button("Send") and user_input:
    try:
        st.write("📨 Sending request to agent...")

        if not st.session_state.session_id:
            st.write("🧠 Creating session...")
            st.session_state.session_id = create_session()
            st.success("✅ Session created.")

        # Send user input
        session_path = st.session_state.session_id
        response = send_input_to_agent(session_path, user_input)

        # Display agent reply
        reply_text = response.get("interactResponse", {}).get("output", {}).get("textOutput", {}).get("text", "(No response)")
        st.markdown("### 🤖 Agent says:")
        st.write(reply_text)

    except Exception as e:
        st.error(f"❌ Error: {e}")
