import sys
from pathlib import Path
import streamlit as st
from groq import Groq
from gtts import gTTS
import io

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from agents.orchestrator.agent import run_orchestrator, api_key

st.set_page_config(page_title="Enterprise Agent Platform", layout="centered")

st.title("Enterprise Agent Platform")
st.caption("Multi-agent orchestration - routing, tools, guardrails, voice")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "audio" in msg:
            st.audio(msg["audio"], format="audio/mp3")

st.divider()
st.subheader("Voice Input")
audio_value = st.audio_input("Record your question")

text_input = st.chat_input("Or type your question...")

user_input = None

if audio_value is not None:
    with st.spinner("Transcribing..."):
        groq_client = Groq(api_key=api_key)
        transcription = groq_client.audio.transcriptions.create(
            file=("audio.wav", audio_value.read()),
            model="whisper-large-v3-turbo",
        )
        user_input = transcription.text

if text_input:
    user_input = text_input

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

        audio_bytes = None
        try:
            tts = gTTS(text=reply, lang="en")
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            audio_bytes = audio_buffer.read()
            st.audio(audio_bytes, format="audio/mp3")
        except Exception:
            pass

    msg_entry = {"role": "assistant", "content": reply}
    if audio_bytes:
        msg_entry["audio"] = audio_bytes
    st.session_state.messages.append(msg_entry)
