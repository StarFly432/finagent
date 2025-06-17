import streamlit as st
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# Load Streamlit secrets
API_QUERY_URL = st.secrets["API_QUERY_URL"]  # Must point to ...:query (no /sessions)
SERVICE_ACCOUNT_JSON = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])

# Streamlit UI
st.set_page_config(page_title="Vertex AI Agent Engine Chat", layout="centered")
st.title("🤖 Chat with Vertex AI Agent")

# Function to get access token
def get_access_token():
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_JSON,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return credentials.token

# User input
user_input = st.text_input("You:", "")

# Submit
if st.button("Send") and user_input:
    try:
        st.write("📨 Sending request to Vertex AI Agent Engine...")
        access_token = get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # This is the correct payload for REST call (v1beta1)
        payload = {
            "class_method": "query",
            "input": {
                "input": user_input
            }
        }

        st.code(f"POST to: {API_QUERY_URL}")
        st.code(f"Payload:\n{json.dumps(payload, indent=2)}")

        response = requests.post(API_QUERY_URL, headers=headers, json=payload)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            st.error(f"❌ HTTP error: {http_err}")
            st.code(f"Response:\n{response.text}")
            raise

        result = response.json()
        st.markdown("### 🤖 Agent says:")
        st.write(result.get("output", "(No response from agent)"))

    except Exception as e:
        st.error(f"❌ General error: {e}")
