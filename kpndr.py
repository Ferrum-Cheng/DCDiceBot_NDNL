import json
import os

data_KP = "KPs.json"

def load_kps():
    if not os.path.exists(data_KP):
        return {}
    try:
        with open(data_KP, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_kp(guild_id, user_id):
    data = load_kps()
    data[str(guild_id)] = user_id
    with open(data_KP, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def remove_kp(guild_id):
    data = load_kps()
    if str(guild_id) in data:
        del data[str(guild_id)]
        with open(data_KP, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)