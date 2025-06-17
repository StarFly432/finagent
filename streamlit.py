import streamlit as st
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Load configuration from secrets
PROJECT_ID = st.secrets["PROJECT_ID"]
LOCATION = st.secrets["LOCATION"]
REASONING_ENGINE_ID = st.secrets["REASONING_ENGINE_ID"]
SERVICE_ACCOUNT_INFO = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])

# Construct the Reasoning Engine API URL
API_URL = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/"
    f"{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}:query"
)

# Set page configuration
st.set_page_config(page_title="Vertex AI Agent Chat", layout="centered")
st.title("🤖 Chat with Vertex AI Reasoning Engine")

# Function to get OAuth access token from service account
@st.cache_data(show_spinner=False)
def get_access_token():
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(Request())
    return credentials.token

# UI input field
user_input = st.text_input("You:", "")

if st.button("Send") and user_input:
    st.write("📨 Sending request to Vertex AI Reasoning Engine...")

    # Get token
    try:
        access_token = get_access_token()
    except Exception as e:
        st.error(f"❌ Failed to authenticate: {e}")
        st.stop()

    # Prepare request headers and payload
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    payload = {
        "input": {
            "input": user_input
        }
    }

    st.code(f"🔗 POST {API_URL}")
    st.code(f"📦 Payload:\n{json.dumps(payload, indent=2)}")

    # Send request
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        st.subheader("🤖 Agent says:")
        st.write(result.get("output", "(No output from agent)"))

    except requests.exceptions.HTTPError as http_err:
        st.error(f"❌ HTTP error: {http_err}")
        st.code(f"🔻 Response:\n{response.text}")
    except Exception as e:
        st.error(f"❌ General error: {e}")
