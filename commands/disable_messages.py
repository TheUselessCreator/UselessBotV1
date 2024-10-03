import discord
from discord.ext import commands

class DisableMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='disablemessages4u')
    async def disable_messages(self, ctx):
        """Disable messages from the bot for the user."""
        user_id = str(ctx.author.id)  # Get the user's ID
        
        # Add the user ID to the user.txt file
        with open('user.txt', 'a') as f:
            f.write(f"{user_id}\n")
        
        await ctx.send("You have been added to the blacklist. You will no longer receive messages from this bot.")

# Setup function to add the cog to the bot
def setup(bot):
    bot.add_cog(DisableMessages(bot))
