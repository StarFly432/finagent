import streamlit as st
import json
import uuid
from google.oauth2 import service_account
import vertexai
from vertexai.preview import reasoning_engines

# Load secrets
PROJECT_ID = st.secrets["PROJECT_ID"]
REASONING_ENGINE_ID = st.secrets["REASONING_ENGINE_ID"]
SERVICE_ACCOUNT_JSON = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])

# UI
st.set_page_config(page_title="Vertex Reasoning Engine", layout="centered")
st.title("🤖 Chat with Vertex AI Reasoning Engine")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

user_input = st.text_input("Ask a question:", "")

if st.button("Send") and user_input:
    try:
        st.info("🔐 Authenticating with Vertex AI...")

        credentials = service_account.Credentials.from_service_account_info(
            SERVICE_ACCOUNT_JSON,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        vertexai.init(project=PROJECT_ID, location="us-central1", credentials=credentials)

        reasoning_engine = reasoning_engines.ReasoningEngine(REASONING_ENGINE_ID)

        st.info("📨 Sending query...")
        response = reasoning_engine.query(question=user_input)  # Note: use a valid named argument

        st.success("🤖 Agent says:")
        st.write(str(response))

    except AttributeError as ae:
        st.error("❌ The `.query()` method is not available. Please confirm you are using google-cloud-aiplatform >= 1.49.0.")
        st.exception(ae)
    except Exception as e:
        st.error(f"❌ Error: {e}")
