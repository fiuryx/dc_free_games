import requests
from bs4 import BeautifulSoup
from cache import cached_request

def gamerpower_games():
    url = "https://www.gamerpower.com/api/giveaways"
    data = cached_request("gamerpower", url)
    games = []
    for g in data:
        games.append({
            "title": g["title"],
            "store": g["platforms"],
            "url": g["open_giveaway_url"],
            "image": g.get("image", "")
        })
    return games

def cheapshark_games():
    url = "https://www.cheapshark.com/api/1.0/deals?price=0"
    data = cached_request("cheapshark", url)
    games = []
    for g in data:
        games.append({
            "title": g["title"],
            "store": "Steam",
            "url": f"https://www.cheapshark.com/redirect?dealID={g['dealID']}",
            "image": g["thumb"]
        })
    return games

def epic_games():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    data = cached_request("epic", url)
    games = []
    elements = data["data"]["Catalog"]["searchStore"]["elements"]
    for g in elements:
        if g.get("promotions"):
            games.append({
                "title": g["title"],
                "store": "Epic Games",
                "url": f"https://store.epicgames.com/es-ES/p/{g['productSlug']}",
                "image": g["keyImages"][0]["url"]
            })
    return games

def prime_games():
    url = "https://gaming.amazon.com/home"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    games = []
    for img in soup.find_all("img"):
        title = img.get("alt")
        if title and "game" in title.lower():
            games.append({
                "title": title,
                "store": "Prime Gaming",
                "url": url,
                "image": img.get("src")
            })
    return games