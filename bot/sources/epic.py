import aiohttp

URL = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions"

async def fetch_epic_games():
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as resp:
            data = await resp.json()

    games = []
    elements = data["data"]["Catalog"]["searchStore"]["elements"]

    for item in elements:
        promos = item.get("promotions")
        if promos and promos.get("promotionalOffers"):
            games.append({
                "id": item["id"],
                "title": item["title"],
                "url": f"https://store.epicgames.com/es-ES/p/{item['productSlug']}",
                "image": item.get("keyImages", [{}])[0].get("url")
            })
    return games