import streamlit as st
import uuid
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# Set page config FIRST
st.set_page_config(page_title="Agent Engine Chat", layout="centered")
st.title("🤖 Chat with Vertex AI Reasoning Engine")

# Load secrets
API_SESSION_URL = st.secrets["API_SESSION_URL"]

# Convert JSON string secret to dict, if needed
try:
    if isinstance(st.secrets["SERVICE_ACCOUNT_JSON"], str):
        SERVICE_ACCOUNT_JSON = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])
    else:
        SERVICE_ACCOUNT_JSON = st.secrets["SERVICE_ACCOUNT_JSON"]
except Exception as e:
    st.error("❌ Failed to parse SERVICE_ACCOUNT_JSON secret.")
    st.stop()

# Generate session ID for each user session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Authenticate with service account JSON
def get_access_token():
    try:
        credentials = service_account.Credentials.from_service_account_info(
            SERVICE_ACCOUNT_JSON,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(google.auth.transport.requests.Request())
        return credentials.token
    except Exception as e:
        st.error(f"❌ Failed to generate credentials: {e}")
        raise

# Input UI
user_input = st.text_input("You:", "")

if st.button("Send") and user_input:
    st.write("📨 Sending request to agent...")
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

        # Show payload and headers (for debugging)
        st.write("🔍 Payload:")
        st.json(payload)

        response = requests.post(API_SESSION_URL, headers=headers, json=payload)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            st.error(f"❌ HTTP error: {http_err}")
            try:
                st.json(response.json())
            except Exception:
                st.write(response.text)
            raise

        # Parse response
        data = response.json()
        st.write("✅ Response:")
        st.json(data)

        # Display agent reply if available
        if "session" in data and "response" in data["session"]:
            st.markdown("### 🤖 Agent says:")
            st.write(data["session"]["response"])
        else:
            st.warning("No response returned from agent.")

    except Exception as e:
        st.error(f"❌ General error: {e}")
