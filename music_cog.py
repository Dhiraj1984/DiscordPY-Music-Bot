import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
import asyncio

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.current_song = None

        # Conditions
        self.playing = False
        self.paused = False
        self.looping = False
        self.stopped = False

        self.voice = None

        self.YTDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    def search_yt(self, item):
        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:
                return False

        return {'source': info['url'], 'title': info['title']}

    async def play_next(self, ctx):
        if self.looping:
            m_url = self.current_song['source']

            self.playing = True
            self.paused = False
            self.looping = True

            source = discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS)
            self.voice.play(discord.PCMVolumeTransformer(source, volume=1), after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
            return
        if len(self.queue) > 0:
            m_url = self.queue[0]['source']
            m_title = self.queue[0]['title']

            self.current_song = self.queue.pop(0)

            self.playing = True
            self.paused = False
            self.looping = False

            source = discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS)
            self.voice.play(discord.PCMVolumeTransformer(source, volume=1), after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
            await ctx.send(f"Now playing: {m_title}")
            return
        else:
            if self.stopped:
                self.stopped = False
                self.current_song = None
                return
            else:
                self.current_song = None
                await ctx.send("Queue is empty. Use `?play` to add more songs.")
                return

    async def play_music(self, ctx):
        if len(self.queue) > 0:
            m_url = self.queue[0]['source']
            m_title = self.queue[0]['title']

            self.current_song = self.queue.pop(0)

            self.playing = True
            self.paused = False
            self.looping = False

            source = discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS)
            self.voice.play(discord.PCMVolumeTransformer(source, volume=1), after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
            await ctx.send(f"Now playing: {m_title}")
        else:
            await ctx.send("Queue is empty. Use `?play` to add more songs.")

    @commands.command(name="join", help="Connect the bot to a voice channel")
    async def join(self, ctx):
        if self.voice is None and ctx.author.voice is not None:
            self.voice = await ctx.author.voice.channel.connect()
            await ctx.send("Connected!")
            return
        if self.voice != ctx.author.voice.channel:
            await self.voice.move_to(ctx.author.voice.channel)
            await ctx.send("Moved and connected!")
            return
        else:
            return await ctx.send("Join a voice channel first!")
    
    @commands.command(name="play", help="Plays a song from YouTube")
    async def play(self, ctx, *, query):
        if not self.voice:
            if ctx.author.voice:
                self.voice = await ctx.author.voice.channel.connect()
            else:
                return await ctx.send("Join a voice channel first!")

        song = self.search_yt(query)
        if type(song) == type(True):
            return await ctx.send("Could not download the song. Incorrect format try another keyword.")

        else:
            self.queue.append((song))
            if not self.playing:
                await ctx.send(f"Added to queue: {song['title']}")
                await self.play_music(ctx)
            else:
                await ctx.send(f"Added to queue: {song['title']}")
            return 

    @commands.command(name="pause", help="Pauses the current song")
    async def pause(self, ctx):
        if self.playing:
            self.paused = True
            self.playing = False
            self.voice.pause()
            await ctx.send("Paused")
        else:
            await ctx.send("Nothing is playing right now.")

    @commands.command(name="resume", help="Resumes the current song")
    async def resume(self, ctx):
        if self.paused:
            self.paused = False
            self.playing = True
            self.voice.resume()
            await ctx.send("Resumed")
        else:
            await ctx.send("Nothing is paused right now.")

    @commands.command(name="skip", help="Skips the current song")
    async def skip(self, ctx):
        if self.playing:
            self.voice.stop()
            await ctx.send("Skipped")
        else:
            await ctx.send("Nothing is playing right now.")

    @commands.command(name="loop", description="Loops the current song")
    async def loop(self, ctx):
        if self.playing or self.paused:
            if self.looping:
                self.looping = False
                await ctx.send("Looping disabled.")
                return
            if self.looping == False:
                self.looping = True
                await ctx.send("Looping enabled.")
                return
        else:
            await ctx.send("Nothing is playing right now.")

    @commands.command(name="volume", help="Changes the volume of the current song")
    async def volume(self, ctx, volume: int):
        if self.voice and self.playing:
            vlm = volume / 100
            self.voice.source.volume = vlm
            await ctx.send(f"Volume set to {volume}%")
            return
        else:
            await ctx.send("Nothing is playing right now.")

    @commands.command(name="queue", help="Shows the current queue")
    async def queue(self, ctx):
        if len(self.queue) > 0:
            queue_list = ""
            for i, song in enumerate(self.queue):
                queue_list += f"{i+1}. {song['title']}\n"
            await ctx.send(f"Queue:\n{queue_list}")
        else:
            await ctx.send("Queue is empty.")

    @commands.command(name="clear", help="Clears the queue")
    async def clear(self, ctx):
        self.queue = []
        await ctx.send("Queue cleared.")

    @commands.command(name="nowplaying", help="Shows the current song")
    async def nowplaying(self, ctx):
        if self.current_song:
            m_title = self.current_song['title']
            return await ctx.send(f"Now playing: {m_title}")
        else:
            return await ctx.send("Nothing is playing right now.")

    @commands.command(name="stop", help="Stop the player")
    async def stop(self, ctx):
        if self.voice and self.playing or self.paused:
            self.queue = []
            self.playing = False
            self.paused = False
            self.looping = False
            self.voice.stop()
            self.stopped = True
            await ctx.send("Stopped")
            return
        else:
            return await ctx.send("Nothing is happening")

    @commands.command(name="leave", help="Disconnects the bot from the voice channel")
    async def disconnect(self, ctx):
        if self.voice:
            self.queue = []
            self.current_song = None
            self.playing = False
            self.paused = False
            self.looping = False
            await self.voice.disconnect()
            self.voice = None
            await ctx.send("Disconnected")
            return
        else:
            await ctx.send("Not connected to a voice channel.")
            return
            


async def setup(bot):
    await bot.add_cog(MusicCog(bot))
        
            
            