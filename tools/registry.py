from pathlib import Path
from tavily import TavilyClient


def find_env_file(start_path: Path):
    current = start_path.resolve()
    for _ in range(6):
        candidate = current / ".env"
        if candidate.exists():
            return candidate
        current = current.parent
    return None


def get_tavily_key():
    try:
        import streamlit as st
        return st.secrets["TAVILY_API_KEY"]
    except Exception:
        pass

    env_path = find_env_file(Path(__file__).resolve().parent)
    if env_path and env_path.exists():
        with open(env_path, "r", encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line.startswith("TAVILY_API_KEY"):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def calculator(expression: str) -> str:
    allowed_chars = set("0123456789+-*/(). ")
    if not all(c in allowed_chars for c in expression):
        return "Error: Expression contains invalid characters."
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return "Error: " + str(e)


def web_search(query: str) -> str:
    api_key = get_tavily_key()
    if not api_key:
        return "Error: Tavily API key not configured."
    try:
        client = TavilyClient(api_key=api_key)
        results = client.search(query=query, max_results=3)
        summary_parts = []
        for r in results.get("results", []):
            title = r.get("title", "")
            content = r.get("content", "")
            summary_parts.append(title + ": " + content)
        if not summary_parts:
            return "No results found."
        return "\n\n".join(summary_parts)
    except Exception as e:
        return "Error: " + str(e)


TOOLS = {
    "calculator": calculator,
    "web_search": web_search,
}
