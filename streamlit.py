import streamlit as st
import uuid
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# 🔹 App start
st.write("🟢 App starting...")

# 🔹 Load secrets
st.write("🔹 Loading secrets...")
API_QUERY_URL = st.secrets["API_QUERY_URL"]
SERVICE_ACCOUNT_JSON = st.secrets["SERVICE_ACCOUNT_JSON"]
st.write("✅ Secrets loaded successfully.")

# 🔹 Streamlit UI setup
st.set_page_config(page_title="Agent Engine Chat", layout="centered")
st.title("🤖 Chat with Vertex AI Agent (via Service Account)")

# 🔹 Generate session ID if not set
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
st.write(f"🆔 Session ID: {st.session_state.session_id}")

# 🔐 Auth function
def get_access_token():
    st.write("🔐 Generating credentials...")
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_JSON,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    st.write("✅ Access token acquired.")
    return credentials.token

# 💬 User input
user_input = st.text_input("You:", "")

# 📤 Send button
if st.button("Send") and user_input:
    st.write("📨 Sending request to agent...")

    try:
        # 🔐 Get token
        access_token = get_access_token()

        # 🧾 Headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # 🧩 Create session path from API_QUERY_URL
        session_base = API_QUERY_URL.split(":")[0]
        session = f"{session_base}/sessions/{st.session_state.session_id}"

        # 📦 Payload
        payload = {
            "queryInput": {
                "text": {
                    "text": user_input
                },
                "languageCode": "en"
            },
            "session": session
        }

        st.write("📡 Sending POST request...")
        response = requests.post(API_QUERY_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        st.write("✅ Response received.")

        # 🤖 Parse response
        messages = data.get("queryResult", {}).get("responseMessages", [])
        if messages:
            agent_reply = messages[0].get("text", {}).get("text", [""])[0]
        else:
            agent_reply = "(No response from agent.)"

        st.markdown("### 🤖 Agent says:")
        st.write(agent_reply)

    except Exception as e:
        st.error(f"❌ Error communicating with Agent Engine: {e}")
