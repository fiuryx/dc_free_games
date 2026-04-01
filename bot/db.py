import json
import os

DB_FILE = "games_db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}  # formato: {game_id: "YYYY-MM-DD"}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)