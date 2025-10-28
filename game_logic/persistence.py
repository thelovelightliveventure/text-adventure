# This file contains functions specifically related to user saves and persistence management.
import json, base64

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
