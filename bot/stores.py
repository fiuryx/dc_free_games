# stores.py
import requests
import os
from logger import logger

def gamerpower_games():
    # Ejemplo placeholder
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
    """
    Lista de juegos gratis desde IsThereAnyDeal
    """
    if not ITAD_API_KEY:
        logger.warning("No se encontró ITAD_API_KEY en las variables de entorno")
        return []

    url = f"https://api.isthereanydeal.com/v01/deals/list/?key={ITAD_API_KEY}&region=us&limit=50&isFree=1"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        try:
            data = res.json()
        except ValueError:
            logger.warning("ITAD no devolvió JSON válido")
            return []
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
    except requests.RequestException as e:
        logger.error(f"Error al consultar ITAD: {e}")
        return []

def ggdeals_games():
    """
    Lista de juegos gratis desde GG.deals
    """
    url = "https://gg.deals/api/games/free/"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        try:
            data = res.json()
        except ValueError:
            logger.warning("GG.deals no devolvió JSON válido")
            return []
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
    except requests.RequestException as e:
        logger.error(f"Error al consultar GG.deals: {e}")
        return []