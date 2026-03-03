"""
Shared utilities for all tools in this project.
Import this at the top of any tool script:
    from _base import env, save_tmp, load_tmp
"""

import os
import json
import pathlib
from dotenv import load_dotenv

# Load .env from project root (works regardless of where the script is called from)
ROOT = pathlib.Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

TMP = ROOT / ".tmp"
TMP.mkdir(exist_ok=True)


def env(key: str) -> str:
    """Get a required environment variable or raise a clear error."""
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Missing env var: {key}\n"
            f"Add it to your .env file (see .env.example)"
        )
    return value


def save_tmp(filename: str, data) -> pathlib.Path:
    """Save data to .tmp/<filename>. Accepts dict/list (JSON) or string."""
    path = TMP / filename
    if isinstance(data, (dict, list)):
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        path.write_text(str(data))
    print(f"[saved] {path}")
    return path


def load_tmp(filename: str):
    """Load a file from .tmp/. Returns parsed JSON if possible, else raw string."""
    path = TMP / filename
    if not path.exists():
        raise FileNotFoundError(f".tmp/{filename} not found — run the preceding step first.")
    text = path.read_text()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text
