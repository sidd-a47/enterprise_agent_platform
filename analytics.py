import json
from pathlib import Path
from datetime import datetime

LOG_FILE = Path(__file__).resolve().parent / "usage_log.json"


def log_usage(route, agent_type):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "route": route,
        "agent_type": agent_type
    }
    data = []
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []
    data.append(entry)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def get_usage_data():
    if not LOG_FILE.exists():
        return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
