import discord
from discord.ext import commands
import random
import time
import os
import csv
import asyncio
import functools
import itertools
import yt_dlp as youtube_dl
from platform import system
from datetime import datetime
from pytz import timezone
from colorama import Fore, Style

files=["commands", "flairs", "coins", "bank", "delivery", "shell", "bomb", "ticket", "letter", "banana"]
file_checks={file:False for file in files}
lists={file:{} for file in files}
user_info={}
snipe_data={"content":{}, "author":{}, "id":{}, "attachment":{}}
editsnipe_data={"content":{}, "author":{}, "id":{}}
prev_steal_targets={}
target_counts={}
cooldowns={"roulette":10.0, "howgay":10.0, "which":10.0, "rps":5.0, "8ball":5.0, "clear":5.0, "trivia":25.0, "slots":10.0, "steal":30.0, 'bet':30.0, 'quote':45.0, "heist":600.0}
last_executed={cooldown:0 for cooldown in cooldowns}
starboard_emoji='<:spuperman:670852114070634527>'
shame_emoji='🪳'
starboard_count=4
zenny='<:zenny:1104179194780450906>'
youtube_dl.utils.bug_reports_message = lambda: ''

# music functionality
# all sorts of classes
class VoiceError(Exception):
    pass

class YTDLError(Exception):
    pass

class YTDLSource(discord.PCMVolumeTransformer):
    common_options = {
        'format': 'bestaudio/best',
        'extractaudio': True,
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
        'source_address': '0.0.0.0'
    }
    YTDL_OPTIONS = common_options.copy()
    if system() == 'Darwin':
        YTDL_OPTIONS['ffmpeg_location'] = '/opt/homebrew/Cellar/ffmpeg/6.1.1_3/bin/ffmpeg'

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)
        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')

    def __str__(self):
        return f'**{self.title}**'

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()
        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            return await ctx.reply(f"Wups! Couldn\'t find anything that matches `{search}`...", mention_author=False)
        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break
            if process_info is None:
                return await ctx.reply(f"Wups! Couldn\'t find anything that matches `{search}`...", mention_author=False)

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError(f"Wups! Couldn\'t fetch `{webpage_url}`...")

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
        while info is None:
            try:
                info = processed_info['entries'].pop(0)
            except IndexError:
                return await ctx.reply(f'Wups! Couldn\'t retrieve any matches for `{webpage_url}`...', mention_author=False)

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = [unit for value, unit in zip([days, hours, minutes, seconds], ["day", "hour", "minute", "second"]) if value != 0]
        duration = [f"{value} {unit}{'s' if value != 1 else ''}" for value, unit in zip([days, hours, minutes, seconds], ["day", "hour", "minute", "second"]) if value != 0]
        return ", ".join(duration)

class Song:
    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (discord.Embed(title='Now playing', description=f'**{self.source.title}**', color=discord.Color.purple())
            .add_field( name='Duration', value=self.source.duration)
            .add_field(name='Requested by', value=self.requester.mention)
            .add_field(name='URL', value=f"[Link](<{self.source.url}>)")
            .set_thumbnail(url=self.source.thumbnail))
        return embed
    
class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]

class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx
        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()
        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()
            try:
                self.current = await self.songs.get()
            except:
                self.bot.loop.create_task(self.stop())
                return
            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)
            print(f'{Style.BRIGHT}Playing {Fore.MAGENTA}{self.current.source.__str__()[2:-2]}{Fore.RESET} in {Style.RESET_ALL}{Fore.BLUE}{self.voice.channel.name}{Fore.RESET}{Style.BRIGHT} in {Style.RESET_ALL}{Fore.GREEN}{self.voice.channel.guild.name} ({self.voice.channel.guild.id}){Fore.RESET}')
            await self.current.source.channel.send(embed=self.current.create_embed())
            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            VoiceError(str(error))
        self.next.set()

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()
        if self.voice:
            await self.voice.disconnect()
            self.voice = None


# bot helper functions
# create_list, update_birthday, check_reaction_board, add_to_board, add_coins, subtract_coins, add_item, subtract_item, dep, wd, direct_to_bank, stolen_funds, in_wom_shenanigans, assert_cooldown, capitalize_string, shark_react, parse_total_duration, cog_check, get_login_time
def create_list(filename):
    global file_checks
    global lists
    file_checks[filename]=False
    if not os.path.exists(f'csv/{filename}.csv'):
        with open(f'csv/{filename}.csv', 'w'):
            pass # creates csv file
    with open(f'csv/{filename}.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows = list(csv_reader)
        if len(rows)==0:
            file_checks[filename]=True
        else:
            lists[filename]={}
            for row in rows:
                dict = list(row.values())
                lists[filename][dict[0]]=dict[1]

def update_birthday(user_id: int, birthdate: str, tz: str):
    fieldnames = ['user_id', 'birthdate', 'timezone']
    found = False
    rows = []
    with open('csv/birthdays.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user_id'] == str(user_id):
                row = {'user_id': row['user_id'], 'birthdate': birthdate, 'timezone': tz}
                found = True
            rows.append(row)
    if not found:
        rows.append({'user_id': str(user_id), 'birthdate': birthdate, 'timezone': tz})
    with open('csv/birthdays.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    create_birthday_list()

def create_birthday_list():
    with open(f'csv/birthdays.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows = list(csv_reader)
        for row in rows:
            user_id = int(row['user_id'])
            birthdate = row['birthdate']
            timezone = row['timezone']
            user_info[user_id] = {'birthdate': birthdate, 'timezone': timezone}

async def check_reaction_board(message, reaction_type):
    emoji, count = None, None

    if reaction_type == "starboard":
        emoji, count = starboard_emoji, starboard_count
    elif reaction_type == "shameboard":
        emoji, count = shame_emoji, starboard_count
    if message.reactions:
        for reaction in message.reactions:
            if str(reaction.emoji) == emoji and reaction.count >= count:
                return True
    return False

async def add_to_board(message, board_type):
    board_name = "hot-seat" if board_type == "starboard" else "cold-seat"
    board_emoji = starboard_emoji if board_type == "starboard" else shame_emoji
    board_text = "⭐" if board_type == "starboard" else "🍅"

    channel = discord.utils.get(message.guild.channels, name=board_name)
    embed = discord.Embed(color=discord.Color.gold(), description=f'[Original Message]({message.jump_url})')
    embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
    embed.set_thumbnail(url=message.author.avatar.url)
    embed.add_field(name='Channel', value=f'<#{message.channel.id}>', inline=True)
    embed.add_field(name='Message', value=f'{str(message.content)}', inline=True)
    if message.attachments:
        embed.set_image(url=message.attachments[0].url)
    for reaction in message.reactions:
        if str(reaction.emoji) == board_emoji:
            board_reaction = reaction
            embed.set_footer(text=f'{board_reaction.count} {board_text}')
            break
    async for board_msg in channel.history():
        if board_msg.embeds and board_msg.embeds[0].description == f'[Original Message]({message.jump_url})':
            embed = board_msg.embeds[0]
            for reaction in message.reactions:
                if str(reaction.emoji) == board_emoji:
                    board_reaction = reaction
                    embed.set_footer(text=f'{board_reaction.count} {board_text}')
                    break
            return await board_msg.edit(embed=embed)
    return await channel.send(embed=embed)

async def reply(ctx, content: str):
    return await ctx.reply(content, mention_author=False)

def add_coins(userID: int, coins: int):
    fieldnames = ['user_id', 'coins']
    found = False
    rows = []
    with open('csv/coins.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user_id'] == str(userID):
                row = {'user_id': row['user_id'], 'coins': int(row['coins']) + coins}
                found = True
            rows.append(row)
    if not found:
        rows.append({'user_id': str(userID), 'coins': coins})
    with open('csv/coins.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    create_list("coins")

def subtract_coins(userID: int, coins: int) -> bool:
    fieldnames = ['user_id', 'coins']
    found = False
    rows = []
    with open('csv/coins.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user_id'] == str(userID):
                balance = int(row['coins'])
                if balance >= coins:
                    row = {'user_id': row['user_id'], 'coins': balance - coins}
                    found = True
                else:
                    return False
            rows.append(row)
    if not found:
        return False
    with open('csv/coins.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    create_list("coins")
    return True

def add_item(itemName:str, userID:int, quantity:int):
    fieldnames = ['user_id', f'{itemName}s']
    found = False
    rows = []
    with open(f'csv/{itemName}.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user_id'] == str(userID):
                row = {'user_id': str(userID), f'{itemName}s': int(row[f'{itemName}s']) + quantity}
                found = True
            rows.append(row)
    if not found:
        rows.append({'user_id': str(userID), f'{itemName}s': quantity})
    with open(f'csv/{itemName}.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    create_list(itemName)

def subtract_item(itemName:str, userID:int, quantity:int) -> bool:
    fieldnames = ['user_id', f'{itemName}s']
    found = False
    rows = []
    with open(f'csv/{itemName}.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user_id'] == str(userID):
                balance = int(row[f'{itemName}s'])
                if balance >= quantity:
                    row = {'user_id': row['user_id'], f'{itemName}s': balance - quantity}
                    found = True
                else:
                    return False
            rows.append(row)
    if not found:
        return False
    with open(f'csv/{itemName}.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    create_list(itemName)
    return True

def dep(userID: int, coins: int) -> bool:
    if subtract_coins(userID, coins):
        fieldnames = ['user_id', 'coins']
        found = False
        rows = []
        with open('csv/bank.csv', 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['user_id'] == str(userID):
                    row = {'user_id': row['user_id'], 'coins': int(row['coins']) + coins}
                    found = True
                rows.append(row)
        if not found:
            rows.append({'user_id': str(userID), 'coins': coins})
        with open('csv/bank.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        create_list("bank")
        return True
    return False

def wd(userID: int, coins: int) -> bool:
    fieldnames = ['user_id', 'coins']
    found = False
    rows = []
    with open('csv/bank.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user_id'] == str(userID):
                if int(row['coins']) >= coins:
                    row = {'user_id': row['user_id'], 'coins': int(row['coins']) - coins}
                    found = True
                else:
                    return False
            rows.append(row)
    if not found:
        return False
    with open('csv/bank.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    create_list("bank")
    add_coins(userID, coins)
    return True

def direct_to_bank(userID: int, coins: int):
    fieldnames = ['user_id', 'coins']
    found = False
    rows = []
    with open('csv/bank.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user_id'] == str(userID):
                row = {'user_id': row['user_id'], 'coins': int(row['coins']) + coins}
                found = True
            rows.append(row)
    if not found:
        rows.append({'user_id': str(userID), 'coins': coins})
    with open('csv/bank.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    create_list("bank")

def stolen_funds(userID: int, coins: int) -> bool:
    fieldnames = ['user_id', 'coins']
    found = False
    rows = []
    with open('csv/bank.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user_id'] == str(userID):
                balance = int(row['coins'])
                if balance >= coins:
                    row = {'user_id': row['user_id'], 'coins': balance - coins}
                    found = True
                else:
                    return False
            rows.append(row)
    if not found:
        return False
    with open('csv/bank.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    create_list("bank")
    return True

async def in_wom_shenanigans(ctx):
    wom_shenanigans = discord.utils.get(ctx.guild.channels, name='wom-shenanigans')
    if wom_shenanigans is None:
        await shark_react(ctx.message)
        await ctx.reply("ask for or make a wom-shenanigans channel first, stupid", mention_author=False)
        return False
    if not ctx.message.channel.id == wom_shenanigans.id:
        await shark_react(ctx.message)
        await ctx.reply(f"go to <#{wom_shenanigans.id}>, jackass", mention_author=False)
        return False
    return True

def assert_cooldown(command):
    global last_executed
    if last_executed[command] + cooldowns[command] < time.time():
        last_executed[command] = time.time()
        return 0
    return round(last_executed[command] + cooldowns[command] - time.time())

def capitalize_string(string: str) -> str:
    return ' '.join(word.capitalize() for word in string.split('-'))

def parse_total_duration(total_duration: list) -> str:
    all_seconds = 0
    conversion_factors = {
        'second': 1,
        'minute': 60,
        'hour': 3600,
        'day': 86400
    }

    for duration in total_duration:
        parts = duration.split(', ')
        seconds = 0
        for part in parts:
            value, unit = part.split(' ')
            value = int(value)
            if unit.endswith('s'):
                unit = unit[:-1]
            seconds += value * conversion_factors[unit]
        all_seconds += seconds

    days, remainder = divmod(all_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    result = [unit for value, unit in zip([days, hours, minutes, seconds], ["day", "hour", "minute", "second"]) if value != 0]
    result = [f"{value} {unit}{'s' if value != 1 else ''}" for value, unit in zip([days, hours, minutes, seconds], ["day", "hour", "minute", "second"]) if value != 0]
    return ', '.join(result)

async def shark_react(message: discord.Message):
    return await message.add_reaction('🦈')

async def cog_check(ctx):
    if not ctx.guild:
        return False
    return True

def get_login_time(tz: str) -> str:
    return f"Time: {datetime.now(timezone(tz)).strftime('%m/%d/%Y, %I:%M:%S %p')}\nTimezone: {tz}\n"