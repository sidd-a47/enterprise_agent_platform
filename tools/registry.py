from pathlib import Path
from tavily import TavilyClient
import requests


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


def calculator(expression):
    allowed_chars = set("0123456789+-*/(). ")
    if not all(c in allowed_chars for c in expression):
        return "Error: Expression contains invalid characters."
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return "Error: " + str(e)


def web_search(query):
    api_key = get_tavily_key()
    if not api_key:
        return "Error: Tavily API key not configured."
    try:
        client = TavilyClient(api_key=api_key)
        results = client.search(query=query, max_results=3)
        parts = []
        for r in results.get("results", []):
            parts.append(r.get("title", "") + ": " + r.get("content", ""))
        if not parts:
            return "No results found."
        return "\n\n".join(parts)
    except Exception as e:
        return "Error: " + str(e)


CRYPTO_MAP = {
    "bitcoin": "bitcoin", "btc": "bitcoin",
    "ethereum": "ethereum", "eth": "ethereum",
    "dogecoin": "dogecoin", "doge": "dogecoin",
    "solana": "solana", "sol": "solana",
    "cardano": "cardano", "ada": "cardano",
    "ripple": "ripple", "xrp": "ripple",
}


def price_checker(query):
    query_lower = query.lower()
    coin_id = None
    for keyword, cg_id in CRYPTO_MAP.items():
        if keyword in query_lower:
            coin_id = cg_id
            break

    if coin_id:
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {"ids": coin_id, "vs_currencies": "usd,inr"}
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            if coin_id in data:
                usd = data[coin_id].get("usd", "N/A")
                inr = data[coin_id].get("inr", "N/A")
                return coin_id.capitalize() + " price: $" + str(usd) + " USD / Rs " + str(inr) + " INR"
            return "Could not find price data for " + coin_id
        except Exception as e:
            return "Error fetching crypto price: " + str(e)
    else:
        return web_search(query + " current stock price")


TOOLS = {
    "calculator": calculator,
    "web_search": web_search,
    "price_checker": price_checker,
}
