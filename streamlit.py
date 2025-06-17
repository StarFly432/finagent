import streamlit as st
import uuid
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# ✅ Set page config FIRST
st.set_page_config(page_title="Agent Engine Chat", layout="centered")
st.title("🤖 Chat with Vertex AI Reasoning Engine")

# 🔐 Load secrets
API_SESSION_URL = st.secrets["API_SESSION_URL"]  # Ex: "https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/us-central1/reasoningEngines/YOUR_ENGINE_ID:sessions"
SERVICE_ACCOUNT_JSON = st.secrets["SERVICE_ACCOUNT_JSON"]

# 🧠 Session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# 🔐 Get access token from service account
def get_access_token():
    st.write("🔐 Generating credentials...")
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_JSON,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(google.auth.transport.requests.Request())
    return credentials.token

# 💬 Input
user_input = st.text_input("You:", "")

if st.button("Send") and user_input:
    try:
        access_token = get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "session": {
                "sessionId": st.session_state.session_id,
                "textInput": {
                    "text": user_input
                }
            }
        }

        st.write("📨 Sending request to agent...")

        response = requests.post(API_SESSION_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # 🔍 Debug print
        st.json(data)

        # Show response (you might need to adjust based on actual format)
        if "session" in data and "response" in data["session"]:
            st.markdown("### 🤖 Agent says:")
            st.write(data["session"]["response"])
        else:
            st.warning("No response returned from agent.")

    except Exception as e:
        st.error(f"❌ General error: {e}")
