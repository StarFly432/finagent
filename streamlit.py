import streamlit as st
import uuid
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# Set page config FIRST
st.set_page_config(page_title="Agent Chat", layout="centered")

# Load secrets
try:
    API_QUERY_URL_BASE = st.secrets["API_QUERY_URL"]  # Without `:query`
    SERVICE_ACCOUNT_JSON = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])
except Exception as e:
    st.error("❌ Failed to load secrets.")
    st.stop()

st.title("🤖 Vertex AI Agent Chat")

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
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        return credentials.token
    except Exception as e:
        st.error(f"❌ Error getting token: {e}")
        st.stop()

# UI input
user_input = st.text_input("You:", "")

if st.button("Send") and user_input:
    st.info("📨 Sending request to Vertex AI Reasoning Engine...")

    try:
        token = get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # API URL must include the session ID
        full_url = f"{API_QUERY_URL_BASE}/sessions/{st.session_state.session_id}:query"

        payload = {
            "queryInput": {
                "text": {
                    "text": user_input
                },
                "languageCode": "en"
            }
        }

        response = requests.post(full_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        st.markdown("### 🤖 Agent says:")
        st.json(data)

    except requests.exceptions.HTTPError as e:
        st.error(f"❌ HTTP error: {e}")
        if e.response is not None:
            try:
                st.json(e.response.json())
            except:
                st.text(e.response.text)
    except Exception as e:
        st.error(f"❌ General error: {e}")
