import streamlit as st
import vertexai
from vertexai import agent_engines
import uuid
import os

# Initialize Vertex AI
vertexai.init(
    project=st.secrets["PROJECT_ID"],
    location=st.secrets["LOCATION"]
)

# Load agent
AGENT_ID = st.secrets["AGENT_ENGINE_ID"]
USER_ID = st.session_state.get("user_id", str(uuid.uuid4()))
agent = agent_engines.get(AGENT_ID)

# Ensure session
if "session_id" not in st.session_state:
    session = agent.create_session(user_id=USER_ID)
    st.session_state.session_id = session["id"]

# UI
st.title("🤖 Chat with Vertex AI Agent Engine")
user_input = st.text_input("You:")

if st.button("Send") and user_input:
    st.markdown("### 🤖 Agent says:")
    response_text = ""
    for event in agent.stream_query(
        user_id=USER_ID,
        session_id=st.session_state.session_id,
        message=user_input
    ):
        if "content" in event and "parts" in event["content"]:
            for part in event["content"]["parts"]:
                if "text" in part:
                    response_text += part["text"]
                    st.write(response_text)
