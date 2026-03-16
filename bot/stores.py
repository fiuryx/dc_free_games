import requests
import os

def gamerpower_games():
    return []

def cheapshark_games():
    return []

def epic_games():
    return []

def prime_games():
    return []

# --- Nuevas fuentes ---
ITAD_API_KEY = os.getenv("ITAD_API_KEY")

def itad_games():
    if not ITAD_API_KEY:
        return []
    url = f"https://api.isthereanydeal.com/v01/deals/list/?key={ITAD_API_KEY}&region=us&limit=50&isFree=1"
    res = requests.get(url)
    data = res.json()
    games = []
    for deal in data.get("data", {}).get("list", []):
        store = deal.get("shop_name", "Unknown")
        games.append({
            "title": deal.get("title"),
            "store": store,
            "url": deal.get("urls", {}).get("game", ""),
            "image": deal.get("image", ""),
            "startDate": deal.get("added"),
            "endDate": deal.get("expiration")
        })
    return games

def ggdeals_games():
    url = "https://gg.deals/api/games/free/"
    res = requests.get(url)
    data = res.json()
    games = []
    for item in data.get("games", []):
        store = item.get("store", "Unknown")
        games.append({
            "title": item.get("title"),
            "store": store,
            "url": item.get("url"),
            "image": item.get("image"),
            "startDate": item.get("start"),
            "endDate": item.get("end")
        })
    return games