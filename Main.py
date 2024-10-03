import discord
import os
import random
import asyncio
from dotenv import load_dotenv
from discord.ext import commands

# Load environment variables from .env file
load_dotenv()

# Define intents for the bot
intents = discord.Intents.default()
intents.members = True  # Enable the member intent to access guild members
intents.messages = True  # Enable message intents for commands

# Define the Discord bot class
class MyBot(commands.Bot):  # Change Client to Bot
    def __init__(self, owner_id, invite_link, *args, **kwargs):
        super().__init__(command_prefix='/', intents=intents, *args, **kwargs)  # Pass intents and command prefix here
        self.owner_id = owner_id  # Store the owner ID
        self.invite_link = invite_link  # Store the invite link
        self.blacklisted_users = self.load_blacklisted_users()  # Load blacklisted user IDs from file

    def load_blacklisted_users(self):
        # Load user IDs from user.txt file and return as a set
        try:
            with open('user.txt', 'r') as f:
                return {line.strip() for line in f.readlines() if line.strip()}  # Remove whitespace and empty lines
        except FileNotFoundError:
            print("user.txt not found. No users will be blacklisted.")
            return set()

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.sync_commands()  # Sync commands with Discord
        await self.update_presence()  # Update presence when bot is ready
        self.update_presence_task = self.loop.create_task(self.update_presence_loop())  # Start the presence update task
        
        # Load all cogs (commands)
        for filename in os.listdir('./commands'):
            if filename.endswith('.py'):
                self.load_extension(f'commands.{filename[:-3]}')

        # Access the guild (server)
        for guild in self.guilds:
            print(f'Connected to server: {guild.name}')
            await self.message_random_members(guild)

    async def sync_commands(self):
        # Sync commands with Discord
        synced_commands = await self.tree.sync()  # Sync the command tree
        print(f"Synced {len(synced_commands)} commands.")

    async def update_presence(self):
        # Set the bot's status to show the number of servers
        server_count = len(self.guilds)
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"I'm in {server_count} servers")
        await self.change_presence(status=discord.Status.online, activity=activity)  # Set status to online with activity

    async def update_presence_loop(self):
        while True:
            await self.update_presence()  # Update the presence
            await asyncio.sleep(60)  # Wait for one minute (60 seconds) before updating again

    async def message_random_members(self, guild):
        while True:
            # Get all members of the guild (server)
            members = guild.members

            # Filter out bot accounts (optional)
            real_users = [member for member in members if not member.bot]

            # Select a random real user
            if not real_users:
                print("No real users available to message.")
                await asyncio.sleep(3600)  # Wait for an hour before retrying
                continue

            random_member = random.choice(real_users)

            # Check if the random member is blacklisted
            if str(random_member.id) in self.blacklisted_users:
                print(f"Skipping blacklisted user: {random_member.name}")
                continue  # Skip this user and select another

            # Send a DM to the randomly selected user
            try:
                await random_member.send(
                    f"Hey! This is UselessBot. Invite me to make it so I'm the most used bot! "
                    f"Here's my link if needed: {self.invite_link}\n"
                )
                print(f"Message sent to {random_member.name}")

                # Notify the owner about the message sent
                owner = await self.fetch_user(self.owner_id)  # Fetch the owner user object
                await owner.send(f"Message sent to: {random_member.name}")

            except Exception as e:
                print(f"Failed to send message: {e}")

            # Wait for one hour (3600 seconds) before sending the next message
            await asyncio.sleep(3600)

# Fetch the owner ID from the .env file
owner_id = int(os.getenv("OWNER_ID"))  # Convert to int

# Load the client ID from the .env file
client_id = os.getenv("CLIENT_ID")  # Fetch the client ID

# Create the invite link with only the "Add Reactions" permission
invite_link = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=64&scope=bot"

# Initialize and run the bot
bot = MyBot(owner_id, invite_link)
bot.run(os.getenv("DISCORD_TOKEN"))
