import streamlit as st
import uuid
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# Setup
API_QUERY_URL = st.secrets["API_QUERY_URL"]
SERVICE_ACCOUNT_JSON = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])

# Streamlit UI
st.set_page_config(page_title="Agent Engine Chat", layout="centered")
st.title("🤖 Chat with Vertex AI Agent Engine")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Auth
def get_access_token():
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_JSON,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return credentials.token

# UI
user_input = st.text_input("You:", "")

if st.button("Send") and user_input:
    st.write("📨 Sending request to agent...")
    try:
        access_token = get_access_token()
        st.write("🔐 Access token generated.")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "input": user_input
        }

        response = requests.post(API_QUERY_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        agent_reply = data.get("response", {}).get("text", "(No text response)")
        st.markdown("### 🤖 Agent says:")
        st.write(agent_reply)

    except Exception as e:
        st.error(f"❌ Error communicating with Agent Engine: {e}")
