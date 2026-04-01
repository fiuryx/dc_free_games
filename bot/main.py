import os
import asyncio
import discord
from discord.ext import tasks, commands
from discord import app_commands
from datetime import datetime, timedelta

from bot.sources.epic import fetch_epic_games
from bot.sources.gamerpower import fetch_gamerpower_games
from bot.db import load_db, save_db

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 3600))  # en segundos
MAX_ALERTS_PER_HOUR = int(os.getenv("MAX_ALERTS_PER_HOUR", 5))
RESEND_DAYS = int(os.getenv("RESEND_DAYS", 7))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Ahora guardamos juegos con fecha de envío
sent_games = load_db()  # formato: {game_id: "YYYY-MM-DD"}

def safe_fetch(fn):
    try:
        return asyncio.run(fn())
    except Exception as e:
        print(f"[ERROR] {fn.__name__}:", e)
        return []

def deduplicate(games):
    seen = set()
    result = []
    for g in games:
        title = g["title"].lower()
        if title not in seen:
            seen.add(title)
            result.append(g)
    return result

def can_send(game_id):
    """Devuelve True si no se ha enviado antes o si pasó RESEND_DAYS"""
    from datetime import datetime
    if game_id not in sent_games:
        return True
    last_sent = datetime.strptime(sent_games[game_id], "%Y-%m-%d")
    return (datetime.utcnow() - last_sent).days >= RESEND_DAYS

@bot.event
async def on_ready():
    print(f"[OK] Bot conectado como {bot.user}")
    try:
        synced = await tree.sync()
        print(f"[OK] Slash commands sincronizados: {len(synced)}")
    except Exception as e:
        print("[ERROR] Sync:", e)
    check_games.start()

@tasks.loop(seconds=CHECK_INTERVAL)
async def check_games():
    print("[INFO] Buscando juegos gratis...")

    epic = await fetch_epic_games()
    gamer = await fetch_gamerpower_games()
    all_games = deduplicate(epic + gamer)

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("[WARN] Canal no encontrado")
        return

    alerts_sent = 0
    for game in all_games:
        if alerts_sent >= MAX_ALERTS_PER_HOUR:
            print("[INFO] Límite de alertas por hora alcanzado")
            break

        if not can_send(game["id"]):
            continue

        embed = discord.Embed(
            title=game["title"],
            url=game["url"],
            description=game.get("description", "Juego gratis disponible"),
            color=0x00ff00
        )
        if game.get("image"):
            embed.set_image(url=game["image"])

        await channel.send(embed=embed)
        sent_games[game["id"]] = datetime.utcnow().strftime("%Y-%m-%d")
        alerts_sent += 1

    save_db(sent_games)
    print(f"[INFO] Nuevos juegos enviados: {alerts_sent}")

# Slash command moderno
@tree.command(name="freegames", description="Ver cantidad de juegos detectados")
async def freegames(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"🎮 Juegos registrados: {len(sent_games)}"
    )

bot.run(TOKEN)