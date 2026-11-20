import json
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config.json"


def load_config():
    """Load local config.json when present; return {} if missing (Cloud Run uses env)."""
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}
    except OSError:
        return {}
    except json.JSONDecodeError:
        return {}

    if not isinstance(data, dict):
        return {}
    return data
