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


def run_retrieval_agent(query: str):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a retrieval specialist. Answer the user's question "
                    "factually and concisely. Reply in the same language the "
                    "user wrote their question in - if they write in Marathi, "
                    "reply in Marathi; if Hindi, reply in Hindi; if English, "
                    "reply in English."
                )
            },
            {"role": "user", "content": query}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print("Retrieval Agent - type exit to quit")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        reply = run_retrieval_agent(user_input)
        print("Retrieval Agent: " + reply)
