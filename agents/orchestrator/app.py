import sys
from pathlib import Path
import streamlit as st

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from agents.orchestrator.agent import run_orchestrator

st.set_page_config(page_title="Enterprise Agent Platform", page_icon="🤖", layout="centered")

st.title("🤖 Enterprise Agent Platform")
st.caption("Multi-agent orchestration — routing, tools, guardrails")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Ask me anything...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply = run_orchestrator(user_input)
            except Exception as e:
                reply = f"⚠️ Error: {e}"
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})