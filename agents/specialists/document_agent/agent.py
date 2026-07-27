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


def answer_from_document(question: str, document_text: str) -> str:
    """
    Answers a question using only the content of the provided document.
    """
    max_chars = 12000
    truncated_text = document_text[:max_chars]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a document analysis specialist. Answer the "
                    "user's question using ONLY the information in the "
                    "document below. If the answer is not in the document, "
                    "say so clearly instead of guessing.\n\n"
                    "DOCUMENT:\n" + truncated_text
                )
            },
            {"role": "user", "content": question}
        ],
        max_tokens=600
    )
    return response.choices[0].message.content
