import base64
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


def analyze_image(question: str, image_bytes: bytes) -> str:
    """
    Analyzes an image and answers a question about it using a vision model.
    """
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/jpeg;base64," + base64_image
                        }
                    }
                ]
            }
        ],
        max_tokens=600
    )
    return response.choices[0].message.content
