import streamlit as st
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Load values from Streamlit secrets
PROJECT_ID = st.secrets["PROJECT_ID"]
LOCATION = st.secrets["LOCATION"]
REASONING_ENGINE_ID = st.secrets["REASONING_ENGINE_ID"]
SERVICE_ACCOUNT_INFO = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])

# Build API endpoint
API_URL = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/"
    f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}:query"
)

# Streamlit UI
st.set_page_config(page_title="Agent Chat", layout="centered")
st.title("🧠 Vertex AI Agent Engine Chat")

# Authenticate with service account
@st.cache_data(show_spinner=False)
def get_access_token():
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(Request())
    return credentials.token

# Input UI
user_input = st.text_input("You:", "")

if st.button("Send") and user_input:
    st.write("📨 Sending request...")

    # Step 1: Authenticate
    try:
        access_token = get_access_token()
    except Exception as e:
        st.error(f"❌ Auth error: {e}")
        st.stop()

    # Step 2: Prepare request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    payload = {
        "input": {
            "input": user_input
        }
    }

    # Debug info
    st.code(f"POST {API_URL}")
    st.code(f"📦 Payload:\n{json.dumps(payload, indent=2)}")

    # Step 3: Send request
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        agent_output = data.get("output", "(No output received)")
        st.subheader("🤖 Agent says:")
        st.write(agent_output)
    except requests.exceptions.HTTPError as http_err:
        st.error(f"❌ HTTP error: {http_err}")
        st.code(response.text)
    except Exception as e:
        st.error(f"❌ General error: {e}")
