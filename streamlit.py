import streamlit as st
import uuid
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# SET THESE:
API_QUERY_URL = "import streamlit as st
import uuid
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# SET THESE:
API_QUERY_URL = st.secrets["API_QUERY_URL"]
SERVICE_ACCOUNT_FILE = st.secrets["SERVICE_ACCOUNT_FILE"]

# Initialize Streamlit UI
st.set_page_config(page_title="Agent Engine Chat", layout="centered")
st.title("🤖 Chat with Vertex AI Agent (via Service Account)")

# Generate session ID for each user session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Authenticate with service account
def get_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return credentials.token

# Input UI
user_input = st.text_input("You:", "")

if st.button("Send") and user_input:
    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "queryInput": {
            "text": {
                "text": user_input
            },
            "languageCode": "en"
        },
        "session": f"projects/YOUR_PROJECT_ID/locations/us-central1/agents/YOUR_AGENT_ID/sessions/{st.session_state.session_id}"
    }

    try:
        response = requests.post(API_QUERY_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # Extract agent response text
        messages = data.get("queryResult", {}).get("responseMessages", [])
        if messages:
            agent_reply = messages[0].get("text", {}).get("text", [""])[0]
        else:
            agent_reply = "(No response from agent.)"

        st.markdown("### 🤖 Agent says:")
        st.write(agent_reply)

    except Exception as e:
        st.error(f"Error communicating with Agent Engine: {e}")"
SERVICE_ACCOUNT_FILE = "path/to/your-service-account.json"

# Initialize Streamlit UI
st.set_page_config(page_title="Agent Engine Chat", layout="centered")
st.title("🤖 Chat with Vertex AI Agent (via Service Account)")

# Generate session ID for each user session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Authenticate with service account
def get_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return credentials.token

# Input UI
user_input = st.text_input("You:", "")

if st.button("Send") and user_input:
    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "queryInput": {
            "text": {
                "text": user_input
            },
            "languageCode": "en"
        },
        "session": f"projects/YOUR_PROJECT_ID/locations/us-central1/agents/YOUR_AGENT_ID/sessions/{st.session_state.session_id}"
    }

    try:
        response = requests.post(API_QUERY_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # Extract agent response text
        messages = data.get("queryResult", {}).get("responseMessages", [])
        if messages:
            agent_reply = messages[0].get("text", {}).get("text", [""])[0]
        else:
            agent_reply = "(No response from agent.)"

        st.markdown("### 🤖 Agent says:")
        st.write(agent_reply)

    except Exception as e:
        st.error(f"Error communicating with Agent Engine: {e}")
