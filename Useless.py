import discord
import os
import random
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define the Discord bot class
class MyBot(discord.Client):
    def __init__(self, owner_id, invite_link, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner_id = owner_id  # Store the owner ID
        self.invite_link = invite_link  # Store the invite link

    async def on_ready(self):
        print(f'Logged in as {self.user}')

        # Access the guild (server)
        for guild in self.guilds:
            print(f'Connected to server: {guild.name}')
            await self.message_random_members(guild)

    async def message_random_members(self, guild):
        while True:
            # Get all members of the guild (server)
            members = guild.members

            # Filter out bot accounts (optional)
            real_users = [member for member in members if not member.bot]

            # Select a random real user
            random_member = random.choice(real_users)

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

# Create the invite link
invite_link = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=0&scope=bot"

# Initialize and run the bot
bot = MyBot(owner_id, invite_link)
bot.run(os.getenv("DISCORD_TOKEN"))
