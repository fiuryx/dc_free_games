import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from logger import logger
from stores import gamerpower_games, cheapshark_games, epic_games, prime_games
from verifier import verify_game
import json
from datetime import datetime, timedelta

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 3600))
RESEND_DAYS = int(os.getenv("RESEND_DAYS", 30))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

LOGOS = {
    "Steam": "https://upload.wikimedia.org/wikipedia/commons/8/83/Steam_icon_logo.svg",
    "Epic Games": "https://upload.wikimedia.org/wikipedia/commons/3/31/Epic_Games_logo.svg",
    "GOG": "https://upload.wikimedia.org/wikipedia/commons/7/7e/GOG.com_logo.svg",
    "Prime Gaming": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg"
}

DATABASE_FILE = "database.json"
MAX_ALERTS_PER_HOUR = 10
alerts_sent = 0

# Cargar DB
if not os.path.exists(DATABASE_FILE):
    with open(DATABASE_FILE, "w") as f:
        json.dump({"games": []}, f)

with open(DATABASE_FILE) as f:
    database = json.load(f)

# Botón reclamar
class ClaimButton(discord.ui.View):
    def __init__(self, url):
        super().__init__()
        self.add_item(discord.ui.Button(label="🎮 Reclamar juego", url=url))

# Embed
def create_embed(game):
    embed = discord.Embed(
        title=game["title"],
        description=f"🎮 Juego gratis en **{game['store']}**",
        color=0x2ecc71
    )
    embed.set_image(url=game["image"])
    logo = LOGOS.get(game["store"])
    if logo:
        embed.set_thumbnail(url=logo)
    embed.set_footer(text="dc_free_games bot")
    return embed

def can_send_alert():
    global alerts_sent
    return alerts_sent < MAX_ALERTS_PER_HOUR

def increment_alerts():
    global alerts_sent
    alerts_sent += 1

@tasks.loop(hours=1)
async def reset_alerts():
    global alerts_sent
    alerts_sent = 0
    logger.info("Reseteadas alertas horarias")

@tasks.loop(seconds=CHECK_INTERVAL)
async def check_games_loop():
    global database
    logger.info("Buscando juegos gratis...")

    gp = gamerpower_games()
    cs = cheapshark_games()
    epic = epic_games()
    prime = prime_games()

    all_games = gp + cs + epic + prime
    verified_games = []

    for game in all_games:
        if verify_game(game, [gp, cs, epic]):
            record = next((g for g in database["games"] if g["title"] == game["title"]), None)
            now = datetime.now()
            send_game = False
            if record:
                last_sent = datetime.fromisoformat(record["last_sent"])
                if now - last_sent > timedelta(days=RESEND_DAYS):
                    send_game = True
                    record["last_sent"] = now.isoformat()
            else:
                send_game = True
                database["games"].append({"title": game["title"], "last_sent": now.isoformat()})

            if send_game:
                verified_games.append(game)

    if verified_games:
        for guild in bot.guilds:
            channel = guild.system_channel
            if not channel:
                continue
            for game in verified_games:
                if can_send_alert():
                    embed = create_embed(game)
                    view = ClaimButton(game["url"])
                    await channel.send(embed=embed, view=view)
                    increment_alerts()
                    logger.info(f"Enviado alerta: {game['title']}")

    with open(DATABASE_FILE, "w") as f:
        json.dump(database, f)

@bot.event
async def on_ready():
    logger.info(f"Bot listo: {bot.user}")
    check_games_loop.start()
    reset_alerts.start()

@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def freegames(ctx):
    gp = gamerpower_games()
    cs = cheapshark_games()
    epic = epic_games()
    prime = prime_games()
    all_games = gp + cs + epic + prime
    for game in all_games[:5]:
        embed = create_embed(game)
        view = ClaimButton(game["url"])
        await ctx.send(embed=embed, view=view)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Espera {round(error.retry_after)} segundos antes de usar el comando otra vez.")

bot.run(TOKEN)