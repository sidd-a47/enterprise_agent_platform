import os
import sys
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

if env_path is not None:
    project_root = env_path.parent
else:
    project_root = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(project_root))

from agents.specialists.retrieval_agent.agent import run_retrieval_agent
from tools.registry import TOOLS
from governance.guardrails.checker import check_input_safety, check_output_safety

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


PERSONAS = {
    "Default": "You are a helpful assistant.",
    "Formal Business Advisor": (
        "You are a formal, professional business advisor. Respond with "
        "precise, polished, corporate language. Avoid slang or casual tone."
    ),
    "Friendly Teacher": (
        "You are a warm, patient teacher who explains things simply, "
        "using examples and encouragement. Keep a friendly, supportive tone."
    ),
    "Sarcastic Comedian": (
        "You are a witty, sarcastic comedian. Answer questions accurately "
        "but with humor, dry wit, and playful sarcasm."
    ),
}

LANGUAGE_INSTRUCTION = " IMPORTANT: Always reply in the same language the user wrote their message in."


def decide_route(user_request):
    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Classify the user's message into exactly one word: "
                    "calculation if it involves math, "
                    "price if it asks about a stock or cryptocurrency price, "
                    "websearch if it needs current or recent information, "
                    "factual if it needs general looked-up facts, or "
                    "chat for general conversation. "
                    "Reply with ONLY one word: calculation, price, websearch, factual, or chat."
                )
            },
            {"role": "user", "content": user_request}
        ],
        max_tokens=10
    )
    return resp.choices[0].message.content.strip().lower()


def run_orchestrator(user_request, persona="Default"):
    is_safe, reason = check_input_safety(user_request)
    if not is_safe:
        return "BLOCKED: " + reason

    route = decide_route(user_request)
    persona_prompt = PERSONAS.get(persona, PERSONAS["Default"])

    if "calculation" in route:
        result = TOOLS["calculator"](user_request.replace("what is", "").replace("?", "").strip())
        response_text = "The result is: " + str(result)
    elif "price" in route:
        response_text = TOOLS["price_checker"](user_request)
    elif "websearch" in route:
        search_results = TOOLS["web_search"](user_request)
        resp = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": persona_prompt + " Summarize search results." + LANGUAGE_INSTRUCTION},
                {"role": "user", "content": "Question: " + user_request + "\n\nSearch results:\n" + search_results}
            ],
            max_tokens=500
        )
        response_text = resp.choices[0].message.content
    elif "factual" in route:
        response_text = run_retrieval_agent(user_request)
    else:
        resp = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": persona_prompt + LANGUAGE_INSTRUCTION},
                {"role": "user", "content": user_request}
            ],
            max_tokens=500
        )
        response_text = resp.choices[0].message.content

    output_safe, output_reason = check_output_safety(response_text)
    if not output_safe:
        return "BLOCKED: " + output_reason

    return response_text


if __name__ == "__main__":
    print("Orchestrator Agent - type exit to quit")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        try:
            reply = run_orchestrator(user_input)
            print("Agent: " + reply)
        except Exception as e:
            print("Error: " + str(e))
