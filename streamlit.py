import streamlit as st
import uuid
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# Load secrets from .streamlit/secrets.toml
API_QUERY_URL = st.secrets["API_QUERY_URL"]
SERVICE_ACCOUNT_JSON = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])

# 🧠 UI setup
st.set_page_config(page_title="Agent Engine Chat", layout="centered")
st.title("🤖 Chat with Vertex AI Reasoning Engine")

# Generate session ID for tracking
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# 🔐 Authenticate with service account and get access token
def get_access_token():
    try:
        credentials = service_account.Credentials.from_service_account_info(
            SERVICE_ACCOUNT_JSON,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        st.success("✅ Token generated")
        return credentials.token
    except Exception as e:
        st.error(f"❌ Auth error: {e}")
        return None

# 💬 User input
user_input = st.text_input("You:", "")

if st.button("Send") and user_input:
    st.markdown("📨 Sending request to Reasoning Engine...")

    access_token = get_access_token()
    if not access_token:
        st.stop()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # ⚙️ Required payload structure
    payload = {
        "inputs": {
            "text": user_input
        }
    }

    try:
        response = requests.post(API_QUERY_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # 🧠 Display the response
        st.markdown("### 🤖 Response:")
        st.json(data)

    except requests.exceptions.HTTPError as http_err:
        st.error(f"❌ HTTP error: {http_err}")
        try:
            st.json(response.json())
        except Exception:
            st.write(response.text)

    except Exception as e:
        st.error(f"❌ General error: {e}")
