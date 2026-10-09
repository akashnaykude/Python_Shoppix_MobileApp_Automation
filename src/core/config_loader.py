import json
from pathlib import Path


def load_json(path: str) -> dict:
    data_path = Path(path)
    if not data_path.exists():
        raise FileNotFoundError(f"Config file missing: {data_path}")
    return json.loads(data_path.read_text(encoding="utf-8"))
