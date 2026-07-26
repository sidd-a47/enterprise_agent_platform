import sys
from pathlib import Path
import streamlit as st

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from agents.orchestrator.agent import run_orchestrator

st.set_page_config(page_title="Enterprise Agent Platform", layout="centered")

st.title("Enterprise Agent Platform")
st.caption("Multi-agent orchestration - routing, tools, guardrails")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask me anything...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply = run_orchestrator(user_input)
            except Exception as e:
                reply = "Error: " + str(e)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
