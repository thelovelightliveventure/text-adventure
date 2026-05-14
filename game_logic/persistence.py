# This file contains functions specifically related to user saves and persistence management.
import json, base64
from pathlib import Path

DEFAULT_SAVE_FILE = Path.cwd() / "savegame.json"

#############################
#### Saving player state ####
#############################

def generate_save_code(state):
    json_str = json.dumps(state)
    encoded = base64.b64encode(json_str.encode()).decode()
    return encoded


def load_from_code(code):
    try:
        json_str = base64.b64decode(code.encode()).decode()
        state = json.loads(json_str)
        return state
    except Exception:
        print("Invalid save code.")
        return None


def save_to_file(state, filename=None):
    path = Path(filename) if filename else DEFAULT_SAVE_FILE
    json_str = json.dumps(state, indent=2)
    path.write_text(json_str, encoding="utf-8")
    return str(path)


def load_from_file(filename=None):
    path = Path(filename) if filename else DEFAULT_SAVE_FILE
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
