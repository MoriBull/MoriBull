import discord
import json
import requests
import youtube_dl
import os
import asyncio
import PIL
import glob

from discord.ext import commands, tasks
from config import settings
from discord import FFmpegAudio
from PIL import Image

bot = commands.Bot(command_prefix = settings['prefix'])

@bot.command() # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def hello(ctx): # Создаём функцию и передаём аргумент ctx.
    author = ctx.message.author # Объявляем переменную author и записываем туда информацию об авторе.
    await ctx.send(f'Hello, {author.mention}!') # Выводим сообщение с упоминанием автора, обращаясь к переменной author.


@bot.command() # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def you_cool(ctx): # Создаём функцию и передаём аргумент ctx.
    author = ctx.message.author # Объявляем переменную author и записываем туда информацию об авторе.
    await ctx.send(f'You too, {author.mention}!') # Выводим сообщение с упоминанием автора, обращаясь к переменной author.

@bot.command()
async def kiss(ctx, member: discord.Member):


    embed = discord.Embed(title=" Yoooo maaan!", description="**{1}** kiss **{0}**!".format(member.name, ctx.message.author.name), color = discord.Color.purple())
    embed.set_image(url = 'https://c.tenor.com/wL_BPLh3K7QAAAAS/billy-herrington-cyberpunk.gif')
    await ctx.send(embed=embed) 

from PIL import Image
from io import BytesIO

@bot.command()
async def Master(ctx, member: discord.Member):
    response = requests.get('https://media.tenor.com/NfSy4OGyV-IAAAAC/vergil-devil-may-cry.gif')

    embed = discord.Embed(title=" D&D Master is", description="**{0}**!".format(member.name, ctx.message.author.name), color = discord.Color.purple())
    embed.set_image(url='attachment://vergil-devil-may-cry.gif')  # Устанавливаем URL напрямую

    file = BytesIO(response.content)
    await ctx.send(embed=embed, file=discord.File(file, 'vergil-devil-may-cry.gif'))


@bot.command()
async def hug(ctx, member: discord.Member):
    response = requests.get('https://usagif.com/wp-content/uploads/gif/anime-hug-12.gif')

    embed = discord.Embed(title=" Hug!", description="{1} hug {0}**!".format(member.name, ctx.message.author.name), color=discord.Color.purple())
    embed.set_image(url='attachment://hug.gif')  # Устанавливаем URL напрямую

    file = BytesIO(response.content)
    await ctx.send(embed=embed, file=discord.File(file, 'hug.gif')) 

''' Тут был тест функций с Some-random-api, однако сервис умер в 2023 '''

'''
@bot.command()
async def fox(ctx):
    response = requests.get('https://some-random-api.ml/endpoints/animal/fox') # Get-запрос на ссылку картинки дискорда
    json_data = json.loads(response.text) # Извлекаем JSON

    embed = discord.Embed(color = 0xff9900, title = 'Random Fox') # Создание Embed'a
    embed.set_image(url = json_data['link']) # Устанавливаем картинку Embed'a
    await ctx.send(embed = embed) # Отправляем Embed 

@bot.command()
async def cat(ctx):
    response = requests.get('https://some-random-api.ml/endpoints/animal/cat') # Get-запрос
    json_data = json.loads(response.text) # Извлекаем JSON

    embed = discord.Embed(color = 0xff9900, title = 'Random Cat') # Создание Embed'a
    embed.set_image(url = json_data['link']) # Устанавливаем картинку Embed'a
    await ctx.send(embed = embed) # Отправляем Embed


@bot.command()
async def dogfact(ctx):
    response = requests.get('https://some-random-api.ml/endpoints/animal/dog')
    json_data = json.loads(response.text) #не трогать уже
    embed = discord.Embed(color = 0xff9900, title = 'Random dogfact') # Создание Embed'a
    embed.set_footer(text = json_data['fact']) # Устанавливаем картинку Embed'a
    await ctx.send(embed=embed) # Отправляем Embed
'''

    

''' Часть для встравивания в чат видео с ютюба '''


youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = "" 

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename       


    @bot.command(name='join', help='Tells the bot to join the voice channel')
    async def join(ctx):
        if not ctx.message.author.voice:
            await ctx.send("{} did not connect to the voice chat".format(ctx.message.author.name))
            return
        else:
            channel = ctx.message.author.voice.channel
        await channel.connect()

    @bot.command(name='leave', help='To make the bot leave the voice channel')
    async def leave(ctx):
           voice_client = ctx.message.guild.voice_client
           if voice_client.is_connected():
                await voice_client.disconnect()
           else:
                await ctx.send("The bot is not connected to the voice channel.")

@bot.command(name='play', help='To play song')
    async def play(ctx,url):
        try :
            server = ctx.message.guild
            voice_channel = server.voice_client

            async with ctx.typing():
                filename = await YTDLSource.from_url(url, loop=bot.loop)
                voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
            embed = discord.Embed(color = 0xff9900, title = 'Now playing: ', description = url) # Создание Embed'a
            await ctx.send(embed = embed)
            #await ctx.send('Сейчас играет: {}'.format(filename))
        except:
            await ctx.send("Oohhh hell, bot can't connect to the chat. Maybe it's time to exorcise the Wi-Fi?")
            
@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at this moment")
    
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot has not played anything before. Use the command *play")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at this moment")


bot.run(settings['token']) # Обращаемся к словарю settings с ключом token, для получения токена
