import json
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config.json"


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)