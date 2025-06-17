import streamlit as st
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Load from Streamlit secrets
PROJECT_ID = st.secrets["PROJECT_ID"]
LOCATION = st.secrets["LOCATION"]
REASONING_ENGINE_ID = st.secrets["REASONING_ENGINE_ID"]
SERVICE_ACCOUNT_INFO = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])

# API endpoint (includes :query)
API_URL = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1/"
    f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}:query"
)

# Page UI
st.set_page_config(page_title="Vertex AI Agent", layout="centered")
st.title("🧠 Vertex AI Agent Engine")

# Token function
@st.cache_data(show_spinner=False)
def get_access_token():
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(Request())
    return credentials.token

# Chat input
user_input = st.text_input("Ask the agent:", "")

if st.button("Send") and user_input:
    st.write("📨 Sending request...")

    try:
        token = get_access_token()
    except Exception as e:
        st.error(f"❌ Auth Error: {e}")
        st.stop()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # ✅ CORRECT payload format with `class_method`
    payload = {
        "class_method": "query",
        "input": {
            "input": user_input
        }
    }

    st.code(f"POST {API_URL}")
    st.code(json.dumps(payload, indent=2))

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
