from asyncore import loop
import discord
from discord.ext import commands
import youtube_dl
from youtubesearchpython import VideosSearch
from pytube import YouTube
import asyncio
import urllib.request
import json
import urllib

queue = []
title_queue = []

class music(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel!")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)
    
    @commands.command()
    async def leave(self,ctx):
        await ctx.voice_client.disconnect()

    def setup(client):
        client.add_cog(music(client))

    @commands.command()
    async def play(self, ctx, *, search_key):
        #Using VideosSearch to search for the first result returned from a youtube search using the user input from discord
        videosSearch = VideosSearch(search_key,limit=1)
        url = videosSearch.result()['result'][0]['link']

        if ctx.author.voice is None:
            await ctx.send("Please join a channel first!")
        
        #Connects to the voice channel if not already in
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
            ctx.voice_client.stop()

        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format':'bestaudio'}
        vc = ctx.voice_client

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url_2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url_2, **FFMPEG_OPTIONS)
            VideoID = url.split("?v=",1)[1]
            params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % VideoID}
            url = "https://www.youtube.com/oembed"
            query_string = urllib.parse.urlencode(params)
            url = url + "?" + query_string

            with urllib.request.urlopen(url) as response:
                response_text = response.read()
                data = json.loads(response_text.decode())
                title = data['title']   
            if ctx.voice_client.is_playing():
                queue.append(source)
                title_queue.append(title)
                title_str = "Queue Position: " + str(len(title_queue))
                embed=discord.Embed(title=title_str,  
                                    description=title_queue[len(title_queue)-1], 
                                    color=0x0DC7C7)
                await ctx.send(embed=embed)

            else:
                embed=discord.Embed(title="Now playing",  
                                    description=title, 
                                    color=0x0DC7C7)
                await ctx.send(embed=embed)
                vc.play(source=source,after=lambda e:play_next())
            
                def play_next():
                    if len(queue) > 0:
                        vc = ctx.voice_client
                        embed=discord.Embed(title="Now playing",  
                                description=title_queue[0], 
                                color=0x0DC7C7)
                        asyncio.run_coroutine_threadsafe(ctx.send(embed=embed), self.client.loop)
                        vc.play(queue[0],after=lambda e:play_next())
                        del(queue[0])
                        del(title_queue[0])
    
    @commands.command()
    async def pause(self, ctx):
        await ctx.voice_client.pause()
        await ctx.send("Paused")

    @commands.command()
    async def resume(self, ctx):
        await ctx.voice_client.resume()
        await ctx.send("Resume")

    @commands.command()
    async def skip(self, ctx):
        ctx.voice_client.stop()
        await ctx.send("Skipped")

    @commands.command()
    async def queue(self,ctx, *, search_key):
        global queue
        global title_queue
        videosSearch = VideosSearch(search_key,limit=1)
        url = videosSearch.result()['result'][0]['link']
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format':'bestaudio'}

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url_2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url_2, **FFMPEG_OPTIONS)

        queue.append(source)
        VideoID = url.split("?v=",1)[1]
        params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % VideoID}
        url = "https://www.youtube.com/oembed"
        query_string = urllib.parse.urlencode(params)
        url = url + "?" + query_string

        with urllib.request.urlopen(url) as response:
            response_text = response.read()
            data = json.loads(response_text.decode())
            title = data['title'] 
        title_queue.append(title)
        title_str = "Queue Position: " + str(len(title_queue))
        embed=discord.Embed(title=title_str,  
                            description=title_queue[len(title_queue)-1], 
                            color=0x0DC7C7)
        await ctx.send(embed=embed)

    @commands.command()
    async def remove(self,ctx,number):
        global queue
        global title_queue
        try:
            del(queue[int(number)-1])
            del(title_queue[int(number)-1])
            title_str = "Queue Position: " + str(len(title_queue))
            embed=discord.Embed(title=title_str,  
                            description=title_queue[len(title_queue)-1], 
                            color=0x0DC7C7)
            await ctx.send(embed=embed)
        except:
            await ctx.send('There is no song in that queue position!')
    
    @commands.command()
    async def view(self,ctx):
        global queue
        global title_queue
        string = ""
        for i in range(len(title_queue)):
            string = string + str(i+1) + ": " + title_queue[i] + "\n"
        embed=discord.Embed(title="Queue:",  
                            description=string, 
                            color=0x0DC7C7)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(music(client))