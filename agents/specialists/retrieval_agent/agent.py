from pathlib import Path
from groq import Groq


def find_env_file(start_path: Path) -> Path:
    current = start_path.resolve()
    for _ in range(6):
        candidate = current / ".env"
        if candidate.exists():
            return candidate
        current = current.parent
    return None


env_path = find_env_file(Path(__file__).resolve().parent)

if env_path is None:
    raise ValueError("Could not find .env file in any parent directory!")

api_key = None
with open(env_path, "r", encoding="utf-8-sig") as f:
    for line in f:
        line = line.strip()
        if line.startswith("GROQ_API_KEY"):
            api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
            break

if not api_key:
    raise ValueError(f"API key not found in .env at: {env_path}")

client = Groq(api_key=api_key)


def run_retrieval_agent(query: str):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a retrieval specialist. Answer the user's question factually and concisely."
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
        print(f"Retrieval Agent: {reply}")
