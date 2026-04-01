import aiohttp

URL = "https://www.gamerpower.com/api/giveaways"

async def fetch_gamerpower_games():
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as resp:
            data = await resp.json()

    games = []
    for g in data:
        games.append({
            "id": f"gp_{g['id']}",
            "title": g["title"],
            "url": g["open_giveaway_url"],
            "image": g.get("image")
        })
    return games