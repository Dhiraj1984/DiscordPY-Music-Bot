import discord
from discord.ext import commands
import os
import psutil
import sys

bot = commands.Bot(command_prefix="?", intents=discord.Intents.all())

@bot.command(name="ping", help="Shows the bot's latency")
async def ping(ctx: commands.Context):
    return await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command(name="invite", help="Shows the bot's invite link")
async def invite(ctx: commands.Context):
    URL = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot"
    return await ctx.send(URL)

@bot.command(name="about", help="About the bot")
async def about(ctx: commands.Context):
    em = discord.Embed(title="About ME!", description="Here is my details")

    ram = psutil.virtual_memory().total / (1024 * 1024)
    cpu_cores = psutil.cpu_count(logical=False)
    python_version =  f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    em.add_field(name="Running on resources", value=f"RAM: {ram:.2F} MB\nCPU Cores: {cpu_cores}\nPython: {python_version}")

    return await ctx.send(embed=em)
    

@bot.event
async def on_ready():
    print("Ready")
    bot.remove_command('help')
    await bot.load_extension('music_cog')
    await bot.load_extension('help_cog')

bot.run(os.getenv("TOKEN"))