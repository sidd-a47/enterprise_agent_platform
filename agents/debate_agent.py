from pathlib import Path
from groq import Groq
import streamlit as st


def find_env_file(start_path: Path):
    current = start_path.resolve()
    for _ in range(6):
        candidate = current / ".env"
        if candidate.exists():
            return candidate
        current = current.parent
    return None


env_path = find_env_file(Path(__file__).resolve().parent)

api_key = None

try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

if not api_key and env_path is not None and env_path.exists():
    with open(env_path, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line.startswith("GROQ_API_KEY"):
                api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

if not api_key:
    raise ValueError("API key not found in Streamlit secrets or .env file!")

client = Groq(api_key=api_key)

DEBATE_PERSONAS = {
    "Optimist": "You are an optimist. Always find the positive, hopeful angle on the topic. Keep responses to 2-3 sentences.",
    "Devil's Advocate": "You are a devil's advocate. Always challenge and find flaws or risks in the topic. Keep responses to 2-3 sentences.",
    "Realist": "You are a realist. Give balanced, practical, fact-based takes. Keep responses to 2-3 sentences.",
    "Skeptic": "You are a skeptic. Question assumptions and demand evidence. Keep responses to 2-3 sentences.",
}


def get_debate_reply(persona_name, topic, conversation_history):
    system_prompt = DEBATE_PERSONAS.get(persona_name, "You are a debater.")

    messages = [{"role": "system", "content": system_prompt}]
    messages.append({"role": "user", "content": "The topic is: " + topic})

    for turn in conversation_history:
        role = "assistant" if turn["speaker"] == persona_name else "user"
        messages.append({"role": role, "content": turn["text"]})

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        max_tokens=150
    )
    return response.choices[0].message.content
