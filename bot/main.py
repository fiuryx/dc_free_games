import os
import discord
from discord.ext import tasks
from discord import app_commands
from dotenv import load_dotenv
from logger import logger
from stores import gamerpower_games, cheapshark_games, epic_games, prime_games
from verifier import verify_game
import json
from datetime import datetime, timedelta
import time

load_dotenv()

# --- Configuración ---
TOKEN = os.getenv("DISCORD_TOKEN")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 3600))
RESEND_DAYS = int(os.getenv("RESEND_DAYS", 30))
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))  # Canal específico
MAX_ALERTS_PER_HOUR = 10

# --- Bot ---
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# --- Logos de tiendas ---
LOGOS = {
    "Steam": "https://upload.wikimedia.org/wikipedia/commons/8/83/Steam_icon_logo.svg",
    "Epic Games": "https://upload.wikimedia.org/wikipedia/commons/3/31/Epic_Games_logo.svg",
    "GOG": "https://upload.wikimedia.org/wikipedia/commons/7/7e/GOG.com_logo.svg",
    "Prime Gaming": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg"
}

# --- Base de datos ---
DATABASE_FILE = "database.json"
alerts_sent = 0

if not os.path.exists(DATABASE_FILE):
    with open(DATABASE_FILE, "w") as f:
        json.dump({"games": []}, f)

with open(DATABASE_FILE) as f:
    database = json.load(f)

# --- Anti-spam para comando slash ---
cooldowns = {}
COOLDOWN_SECONDS = 30

# --- Botón para reclamar juego ---
class ClaimButton(discord.ui.View):
    def __init__(self, url):
        super().__init__()
        self.add_item(discord.ui.Button(label="🎮 Reclamar juego", url=url))

# --- Embed ---
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

# --- Anti-spam de alertas automáticas ---
def can_send_alert():
    global alerts_sent
    return alerts_sent < MAX_ALERTS_PER_HOUR

def increment_alerts():
    global alerts_sent
    alerts_sent += 1

# --- Reset de alertas por hora ---
@tasks.loop(hours=1)
async def reset_alerts():
    global alerts_sent
    alerts_sent = 0
    logger.info("Reseteadas alertas horarias")

# --- Loop de revisión de juegos ---
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
            channel = bot.get_channel(CHANNEL_ID)
            if not channel:
                channel = guild.system_channel
            if not channel:
                logger.warning(f"No se encontró canal para enviar alertas en {guild.name}")
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

# --- Comando slash /freegames ---
@tree.command(name="freegames", description="Muestra los últimos juegos gratis")
async def freegames(interaction: discord.Interaction):
    user_id = interaction.user.id
    now = time.time()
    last = cooldowns.get(user_id, 0)
    if now - last < COOLDOWN_SECONDS:
        await interaction.response.send_message(
            f"⏳ Espera {int(COOLDOWN_SECONDS - (now - last))} segundos antes de usar el comando otra vez.",
            ephemeral=True
        )
        return
    cooldowns[user_id] = now

    gp = gamerpower_games()
    cs = cheapshark_games()
    epic = epic_games()
    prime = prime_games()
    all_games = gp + cs + epic + prime

    for game in all_games[:5]:
        embed = create_embed(game)
        view = ClaimButton(game["url"])
        await interaction.response.send_message(embed=embed, view=view)

# --- Eventos ---
@bot.event
async def on_ready():
    logger.info(f"Bot listo: {bot.user}")
    await tree.sync()
    check_games_loop.start()
    reset_alerts.start()

bot.run(TOKEN)