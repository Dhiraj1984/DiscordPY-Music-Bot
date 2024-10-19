import discord
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.helpmessage = """
```
GENERAL COMMANDS:
?help - Shows this message
?ping - Shows the bot's latency
?invite - Shows the bot's invite link
--------------------------------
?join - Connects the bot to your voice channel
?play - Plays a song from YouTube
?pause - Pauses the current song
?resume - Resumes the current song
?skip - Skips the current song
?loop - Loops the current song
?volume - Changes the volume of the current song
?queue - Shows the current queue
?clear - Clears the queue
?nowplaying - Shows the current song
?leave - Disconnects the bot from the voice channel
```
"""

    @commands.command(name="help", help="Shows help message")
    async def help(self, ctx):
        return await ctx.send(self.helpmessage)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))