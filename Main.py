import discord
import requests
import asyncio
import os
from dotenv import load_dotenv
from discord.ext import tasks
import logging
import time

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
STATUS_URL = os.getenv('STATUS_URL')

# Status Indicator Emojis
STATUS_EMOJIS = {
    'operational': '🟢',
    'degraded': '🟡',
    'down': '🔴'
}

# Cooldown settings and uptime tracking
last_check_time = 0
COOLDOWN_PERIOD = 300  # 5 minutes in seconds
uptime_history = []  # Stores 1 for "up" and 0 for "down"

# Set up logging for errors and security alerts
logging.basicConfig(level=logging.INFO, filename="bot_security.log", filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Function to fetch the status from the API
def check_status():
    try:
        response = requests.get(STATUS_URL)
        response.raise_for_status()
        data = response.json()
        return data.get("status")
    except requests.RequestException as e:
        logging.error(f"Error fetching status: {e}")
        return None

# Calculate average uptime as a percentage
def calculate_average_uptime():
    if not uptime_history:
        return 100.0  # Assume 100% if no data
    return (sum(uptime_history) / len(uptime_history)) * 100

# Set up the Discord client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    channel = client.get_channel(CHANNEL_ID)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="pella.app"))

    # Send initial message or find the last message
    async for message in channel.history(limit=10):
        if message.author == client.user:
            client.message_to_edit = message
            break
    else:
        client.message_to_edit = await channel.send("🔄 Checking status...")

    update_status.start()

# Task to update the message periodically
@tasks.loop(minutes=5)
async def update_status():
    global last_check_time
    
    # Anti-spam cooldown check
    current_time = time.time()
    if current_time - last_check_time < COOLDOWN_PERIOD:
        logging.warning("Cooldown active. Skipping status check.")
        return
    last_check_time = current_time

    # Temporarily show "Checking status..." status
    await client.change_presence(activity=discord.Game(name="🔄 Checking status..."))
    status = check_status()
    
    # Track uptime: record 1 if "operational" or "degraded", otherwise 0
    if status == 'operational' or status == 'degraded':
        uptime_history.append(1)
    else:
        uptime_history.append(0)

    # Calculate average uptime
    average_uptime = calculate_average_uptime()

    emoji = STATUS_EMOJIS.get(status, '❓')
    status_text = {
        'operational': 'Fully operational',
        'degraded': 'Operating with some issues',
        'down': 'Service is down'
    }.get(status, 'Unknown status')

    # Update message in the Discord channel
    if client.message_to_edit:
        try:
            await client.message_to_edit.edit(content=f"{emoji} Status: {status_text}\n📊 Average Uptime: {average_uptime:.2f}%")
        except discord.HTTPException as e:
            logging.error(f"Error updating message: {e}")

    # Reset to "Watching pella.app" status
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="pella.app"))

# Enhanced shutdown function for security
async def shutdown_bot():
    logging.critical("Security alert triggered: Shutting down bot.")
    await client.close()

@client.event
async def on_error(event, *args, **kwargs):
    logging.error(f"Error in event {event}: {args} {kwargs}")
    await shutdown_bot()

@client.event
async def on_disconnect():
    logging.warning("Bot disconnected unexpectedly.")
    await shutdown_bot()

client.run(TOKEN)
