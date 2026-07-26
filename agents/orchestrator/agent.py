import os
import sys
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

project_root = env_path.parent
sys.path.insert(0, str(project_root))

from agents.specialists.retrieval_agent.agent import run_retrieval_agent
from tools.registry import TOOLS
from governance.guardrails.checker import check_input_safety, check_output_safety

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

def decide_route(user_request: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "Classify the user's message into exactly one word: "
                    "'calculation' if it involves math that needs computing, "
                    "'factual' if it needs looked-up facts/data, or "
                    "'chat' for general conversation. "
                    "Reply with ONLY one word: calculation, factual, or chat."
                )
            },
            {"role": "user", "content": user_request}
        ],
        max_tokens=10
    )
    return response.choices[0].message.content.strip().lower()


def run_orchestrator(user_request: str):
    is_safe, reason = check_input_safety(user_request)
    if not is_safe:
        return f"BLOCKED: {reason}"

    route = decide_route(user_request)
    # print(f"[Orchestrator routing decision: {route}]")  # commented out for web UI

    if "calculation" in route:
        result = TOOLS["calculator"](user_request.replace("what is", "").replace("?", "").strip())
        response_text = f"The result is: {result}"
    elif "factual" in route:
        response_text = run_retrieval_agent(user_request)
    else:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": user_request}],
            max_tokens=500
        )
        response_text = response.choices[0].message.content

    output_safe, output_reason = check_output_safety(response_text)
    if not output_safe:
        return f"BLOCKED: {output_reason}"

    return response_text


if __name__ == "__main__":
    print("Orchestrator Agent - type exit to quit")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        try:
            reply = run_orchestrator(user_input)
            print(f"Agent: {reply}")
        except Exception as e:
            print(f"Error: {e}")