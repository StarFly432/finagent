import streamlit as st
import uuid
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# Set page config FIRST
st.set_page_config(page_title="Agent Chat", layout="centered")

# Load secrets from Streamlit
try:
    API_QUERY_URL = st.secrets["API_QUERY_URL"]
    SERVICE_ACCOUNT_JSON = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])
except Exception as e:
    st.error("Failed to load API secrets.")
    st.stop()

st.title("🤖 Vertex AI Agent Chat")

# Generate session ID for user
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Get access token from service account
def get_access_token():
    try:
        st.info("🔐 Generating credentials...")
        credentials = service_account.Credentials.from_service_account_info(
            SERVICE_ACCOUNT_JSON,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        return credentials.token
    except Exception as e:
        st.error(f"Failed to get access token: {e}")
        st.stop()

# Input box
user_input = st.text_input("You:", "")

if st.button("Send") and user_input:
    try:
        st.info("📨 Sending request to agent...")
        access_token = get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "query": user_input,
            "sessionId": st.session_state.session_id
        }

        response = requests.post(API_QUERY_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        st.success("✅ Agent responded!")
        st.markdown("### 🤖 Agent says:")
        st.write(data)

    except requests.exceptions.HTTPError as e:
        st.error(f"❌ HTTP error: {e}")
        if e.response is not None:
            try:
                st.json(e.response.json())
            except:
                st.text(e.response.text)

    except Exception as e:
        st.error(f"❌ General error: {e}")
