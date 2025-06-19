import streamlit as st
import uuid
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# Load secrets
API_BASE = st.secrets["API_BASE_URL"]  # e.g. https://us-central1-aiplatform.googleapis.com/v1
PROJECT_ID = st.secrets["PROJECT_ID"]
LOCATION = st.secrets["LOCATION"]
REASONING_ENGINE_ID = st.secrets["REASONING_ENGINE_ID"]
SERVICE_ACCOUNT_INFO = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])

# Streamlit UI
st.set_page_config(page_title="Agent Engine Chat", layout="centered")
st.title("🤖 Vertex AI Reasoning Engine Chat")

# Generate session ID once
if "session_name" not in st.session_state:
    st.session_state.session_name = None

# Authenticate
@st.cache_resource(show_spinner=False)
def get_access_token():
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(google.auth.transport.requests.Request())
    return credentials.token

# Create a session if none exists
def create_session():
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = f"{API_BASE}/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}:create_session"
    payload = {
        "session": {
            "user": f"user-{str(uuid.uuid4())}"
        }
    }

    st.write("🔄 Creating session...")
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    session_info = response.json()
    session_name = session_info["name"]
    st.session_state.session_name = session_name
    st.success(f"✅ Session created: {session_name}")
    return session_name

# Send query to deployed agent method (must exist in your class)
def send_message(session_name, user_input):
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = f"{API_BASE}/{session_name}:message"
    payload = {
        "class_method": "message",  # must match method name in your agent class
        "input": {
            "input": user_input
        }
    }

    st.code(f"🔍 POST {url}")
    st.code(f"📦 Payload:\n{json.dumps(payload, indent=2)}")

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

# UI input
user_input = st.text_input("You:")

if st.button("Start Session"):
    try:
        create_session()
    except Exception as e:
        st.error(f"Failed to create session: {e}")

if st.button("Send") and user_input:
    if not st.session_state.session_name:
        st.warning("Please start a session first.")
    else:
        try:
            result = send_message(st.session_state.session_name, user_input)
            output = result.get("output", result)
            st.markdown("### 🤖 Agent says:")
            st.write(output)
        except Exception as e:
            st.error(f"❌ Error: {e}")
