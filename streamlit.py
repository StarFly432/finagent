import streamlit as st
import uuid
import vertexai
from vertexai import agent_engines
from google.oauth2 import service_account

# Load secrets
PROJECT_ID = st.secrets["PROJECT_ID"]
LOCATION = st.secrets["LOCATION"]
AGENT_ENGINE_ID = st.secrets["AGENT_ENGINE_ID"]
SERVICE_ACCOUNT_INFO = dict(st.secrets["SERVICE_ACCOUNT_JSON"])
# Set page config
st.set_page_config(page_title="Agent Engine Chat", layout="centered")
st.title("🤖 Chat with Vertex AI Agent Engine")

# Create unique user/session IDs
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user-{uuid.uuid4()}"

# Authenticate and initialize Vertex AI
credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO,
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    credentials=credentials
)

# Get agent instance and create session
try:
    agent = agent_engines.get(AGENT_ENGINE_ID)
    if "agent_session" not in st.session_state:
        st.session_state.agent_session = agent.create_session(user_id=st.session_state.user_id)
        st.success("✅ Session created successfully.")
except Exception as e:
    st.error(f"❌ Failed to create session: {e}")
    st.stop()

# Input UI
user_input = st.text_input("You:", "")

if st.button("Send") and user_input:
    try:
        st.write("📨 Sending to agent...")
        # Stream response from agent
        response_text = ""
        for event in agent.stream_query(
            user_id=st.session_state.user_id,
            session_id=st.session_state.agent_session["id"],
            message=user_input
        ):
            if "content" in event and "parts" in event["content"]:
                for part in event["content"]["parts"]:
                    if "text" in part:
                        response_text += part["text"]
        st.markdown("### 🤖 Agent says:")
        st.write(response_text or "(No response)")
    except Exception as e:
        st.error(f"❌ Error communicating with agent: {e}")
