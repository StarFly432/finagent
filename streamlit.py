import streamlit as st
import uuid
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# Load secrets
API_QUERY_URL = st.secrets["API_QUERY_URL"]
SERVICE_ACCOUNT_JSON = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])

# Page setup
st.set_page_config(page_title="Agent Engine Chat", layout="centered")
st.title("🤖 Chat with Vertex AI Agent Engine")

# Generate session ID per user (still useful for local state tracking)
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Auth function
def get_access_token():
    st.write("🔐 Loading credentials...")
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_JSON,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    st.write("✅ Access token obtained.")
    return credentials.token

# Text input
user_input = st.text_input("You:", "")

if st.button("Send") and user_input:
    try:
        st.write("📨 Sending request to agent...")
        access_token = get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "input": {
                "textInput": {
                    "text": user_input
                }
            }
        }

        st.code(f"🔍 POST to: {API_QUERY_URL}")
        st.code(f"🧾 Payload:\n{json.dumps(payload, indent=2)}")

        response = requests.post(API_QUERY_URL, headers=headers, json=payload)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            st.error(f"❌ HTTP error: {http_err}")
            st.code(f"🔻 Response body:\n{response.text}")
            raise

        data = response.json()
        agent_reply = data.get("output", {}).get("text", "(No text response)")
        st.markdown("### 🤖 Agent says:")
        st.write(agent_reply)

    except Exception as e:
        st.error(f"❌ General error: {e}")
