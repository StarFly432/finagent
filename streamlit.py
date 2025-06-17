import streamlit as st
import uuid
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# Load secrets
API_QUERY_URL = st.secrets["API_QUERY_URL"]
SERVICE_ACCOUNT_JSON = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])

# Setup UI
st.set_page_config(page_title="Agent Engine Chat", layout="centered")
st.title("🤖 Chat with Vertex AI Reasoning Engine")

# Session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Get access token
def get_access_token():
    try:
        credentials = service_account.Credentials.from_service_account_info(
            SERVICE_ACCOUNT_JSON,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(google.auth.transport.requests.Request())
        return credentials.token
    except Exception as e:
        st.error(f"❌ Auth error: {e}")
        return None

# User input
user_input = st.text_input("You:", "")

if st.button("Send") and user_input:
    access_token = get_access_token()
    if not access_token:
        st.stop()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # ✅ CORRECT payload for reasoningEngines:query
    payload = {
        "input": user_input
    }

    try:
        response = requests.post(API_QUERY_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # Try to extract agent's message (if structured)
        reply = data.get("response", {}).get("text") or json.dumps(data, indent=2)
        st.markdown("### 🤖 Agent says:")
        st.write(reply)

    except requests.exceptions.HTTPError as http_err:
        st.error(f"❌ HTTP error: {http_err}")
        try:
            st.json(response.json())
        except Exception:
            st.text(response.text)

    except Exception as e:
        st.error(f"❌ General error: {e}")
