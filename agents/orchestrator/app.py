
import sys
from pathlib import Path
import streamlit as st
from groq import Groq
from gtts import gTTS
from pypdf import PdfReader
import io
import uuid

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from agents.orchestrator.agent import run_orchestrator, api_key
from agents.specialists.document_agent.agent import answer_from_document

st.set_page_config(page_title="Enterprise Agent Platform", layout="centered")

# ---- Session management ----
if "conversations" not in st.session_state:
    first_id = str(uuid.uuid4())
    st.session_state.conversations = {
        first_id: {"name": "New Chat", "messages": []}
    }
    st.session_state.active_conversation = first_id

if "document_text" not in st.session_state:
    st.session_state.document_text = None

if "document_name" not in st.session_state:
    st.session_state.document_name = None


def create_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.conversations[new_id] = {"name": "New Chat", "messages": []}
    st.session_state.active_conversation = new_id


def switch_chat(chat_id):
    st.session_state.active_conversation = chat_id


def delete_chat(chat_id):
    if len(st.session_state.conversations) > 1:
        del st.session_state.conversations[chat_id]
        if st.session_state.active_conversation == chat_id:
            st.session_state.active_conversation = list(st.session_state.conversations.keys())[0]


# ---- Sidebar: conversation list ----
st.sidebar.header("Conversations")

if st.sidebar.button("+ New Chat", use_container_width=True):
    create_new_chat()
    st.rerun()

st.sidebar.divider()

for chat_id, chat_data in list(st.session_state.conversations.items()):
    col1, col2 = st.sidebar.columns([4, 1])
    is_active = chat_id == st.session_state.active_conversation
    label = ("➤ " if is_active else "") + chat_data["name"]
    if col1.button(label, key="switch_" + chat_id, use_container_width=True):
        switch_chat(chat_id)
        st.rerun()
    if col2.button("x", key="del_" + chat_id):
        delete_chat(chat_id)
        st.rerun()

st.sidebar.divider()

# ---- Sidebar: document upload ----
st.sidebar.header("Document Upload")
uploaded_file = st.sidebar.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None:
    if st.session_state.document_name != uploaded_file.name:
        with st.spinner("Reading document..."):
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            st.session_state.document_text = text
            st.session_state.document_name = uploaded_file.name
        st.sidebar.success("Loaded: " + uploaded_file.name)
        st.sidebar.write("Characters extracted: " + str(len(st.session_state.document_text)))
    else:
        st.sidebar.info("Currently loaded: " + uploaded_file.name)

if st.session_state.document_text:
    if st.sidebar.button("Clear document"):
        st.session_state.document_text = None
        st.session_state.document_name = None
        st.rerun()

# ---- Main chat area ----
active_id = st.session_state.active_conversation
active_chat = st.session_state.conversations[active_id]

st.title("Enterprise Agent Platform")
st.caption("Multi-agent orchestration - routing, tools, guardrails, voice, documents")

for msg in active_chat["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "audio" in msg:
            st.audio(msg["audio"], format="audio/mp3")

st.divider()
st.subheader("Voice Input")
audio_value = st.audio_input("Record your question")

text_input = st.chat_input("Ask a question, or ask about your uploaded document...")

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
    active_chat["messages"].append({"role": "user", "content": user_input})

    if active_chat["name"] == "New Chat":
        active_chat["name"] = user_input[:30]

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if st.session_state.document_text:
                    reply = answer_from_document(user_input, st.session_state.document_text)
                else:
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
    active_chat["messages"].append(msg_entry)
