import discord
from discord.ext import commands
import random
import time
import os
import csv
import asyncio
import functools
import itertools
import json
import audioop

from datetime import datetime
from pytz import timezone
from typing import Optional
from colorama import Fore, Style

# global variable declarations, with 1 exception that mix_settings is a function that defines the default global mix settings
files=["commands", "flairs", "coins", "bank", "voucher", "shell", "bomb", "ticket", "letter", "banana", "karma", "voice"]
file_checks={file:False for file in files}
lists={file:{} for file in files}
user_info={}
snipe_data={item:{} for item in ["content", "author", "id", "attachment"]}
editsnipe_data={item:{} for item in ["content", "author", "id"]}
prev_steal_targets={}
target_counts={}
cooldowns={"roulette":10.0, "howgay":10.0, "which":10.0, "itt":10.0, "react":5.0, "rps":5.0, "8ball":5.0, "clear":5.0, "trivia":25.0, "slots":10.0, "steal":30.0, 'bet':30.0, 'heist':600.0}
last_executed={cooldown:{} for cooldown in cooldowns}
starboard_emoji='<:spuperman:670852114070634527>'
shame_emoji='🪳'
starboard_count=4
zenny='<:zenny:1104179194780450906>'
tts_voice_aliases = {
    "male1": "en-US-GuyNeural",
    "male2": "en-US-AndrewMultilingualNeural",
    "male3": "en-US-BrianMultilingualNeural",
    "female1": "en-US-JennyNeural",
    "female2": "en-US-AriaNeural",
    "female3": "en-US-EmmaMultilingualNeural",
}
voice_id_to_alias = {v: f"{k[:-1]} {k[-1]}" for k, v in tts_voice_aliases.items()}
default_tts_voice = "en-US-JennyNeural"

def mix_settings(music_volume: Optional[float] = None, tts_volume: Optional[float] = None) -> tuple[float, float]:
    global volume_adjustment, tts_volume_adjustment
    file_path = os.path.join(os.path.dirname(__file__), "csv", "mix.csv")

    if music_volume is None and tts_volume is None:
        music_volume, tts_volume = 0.2, 1.0
        try:
            with open(file_path, "r", newline="") as mix_file:
                reader = csv.DictReader(mix_file)
                row = next(reader, None)
            if row:
                try:
                    music_volume = float(row.get("music", music_volume))
                except (TypeError, ValueError):
                    pass
                try:
                    tts_volume = float(row.get("tts", tts_volume))
                except (TypeError, ValueError):
                    pass
        except Exception:
            pass

    try:
        music_volume = float(music_volume)
    except (TypeError, ValueError):
        music_volume = 0.2
    try:
        tts_volume = float(tts_volume)
    except (TypeError, ValueError):
        tts_volume = 1.0

    if music_volume < 0.0:
        music_volume = 0.0
    if music_volume > 1.0:
        music_volume = 1.0
    if tts_volume < 0.0:
        tts_volume = 0.0
    if tts_volume > 1.0:
        tts_volume = 1.0

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", newline="") as mix_file:
        writer = csv.DictWriter(mix_file, fieldnames=["music", "tts"])
        writer.writeheader()
        writer.writerow({"music": f"{music_volume:.3f}", "tts": f"{tts_volume:.3f}"})

    volume_adjustment = music_volume
    tts_volume_adjustment = tts_volume
    return music_volume, tts_volume

volume_adjustment, tts_volume_adjustment = mix_settings()

# on_message event handler class
# just because i didn't think these functions would be necessary elsewhere
class MessageHandlers:
    @staticmethod
    async def custom_commands(message, lists):
        # handle custom commands from lists["commands"]
        if message.content.startswith("!w "):
            parts = message.content.split()
            if len(parts) > 1 and parts[1] in lists["commands"]:
                await message.reply(lists["commands"][parts[1]], mention_author=False)
    
    @staticmethod
    async def phrase_triggers(message):
        # handle exact phrase matches like 'skill issue', 'me', etc
        from random import choice
        
        content = message.content.strip().lower()
        
        if content == "skill issue":
            await message.channel.send(file=discord.File("img/skill-issue.gif"))
        elif content == "me":
            await message.channel.send('<:WoM:836128658828558336>')
        elif content == "which":
            if assert_cooldown("which", message.author.id) == 0:
                members = [m.display_name.lower() for m in message.guild.members if not m.bot]
                await message.channel.send(choice(members))
            else:
                await shark_react(message)
        elif content == "hi guys":
            try:
                await message.add_reaction("🍅")
            except:
                pass
    
    @staticmethod
    async def trigger_reactions(message, triggers, trigger_emojis):
        # handle emoji reactions based on trigger words
        from re import escape, search
        
        if message.channel.name in ['venting', 'serious-talk']:
            return
        
        content_lower = message.content.lower()
        for trigger, emoji in zip(triggers, trigger_emojis):
            if trigger == "persona" and message.channel.name == "the-velvet-room":
                continue
            
            pattern = r'\b' + escape(trigger) + r'\b'
            if search(pattern, content_lower):
                try:
                    await message.add_reaction(emoji)
                except:
                    pass
    
    @staticmethod
    async def shiny_spawn(message, zenny):
        # handle rare shiny spawns
        from random import randint
        
        if message.channel.name in ['venting', 'serious-talk']:
            return
        
        if randint(1, 8192) == 1:
            direct_to_bank(message.author.id, 500)
            with open("img/shiny.png", "rb") as f:
                file = discord.File(f)
                await message.channel.send(
                    content=f"{message.author.name} stumbled across 500 {zenny} and a wild Wyvern of Marina! ✨",
                    file=file
                )
    
    @staticmethod
    async def ping_responses(message, reply_choices, reactions):
        # handle ping interactions
        from re import compile, IGNORECASE
        from random import choice
        import asyncio
        
        wom = discord.utils.get(message.guild.members, bot=True, name="Wyvern of Marina")
        if not wom:
            return
        
        content = message.content.strip()
        
        # "is this true" pattern
        the_thing = compile(rf"<@!?{wom.id}>\s+is this true[\s\?\!\.\,]*$", IGNORECASE)
        if the_thing.fullmatch(content):
            if wom.nick and wom.nick.lower() == "wrok":
                if assert_cooldown("itt", message.author.id) == 0:
                    async with message.channel.typing():
                        await asyncio.sleep(1)
                        await message.reply(choice(reply_choices), mention_author=False)
                else:
                    await shark_react(message)
            else:
                await shark_react(message)
                await message.reply("Wups! I need to be nicknamed \"Wrok\" for this to work...", mention_author=False)
            return
        
        # general ping pattern
        the_thing2 = compile(rf"<@!?{wom.id}>\s+.+", IGNORECASE)
        if the_thing2.fullmatch(content):
            if assert_cooldown("react", message.author.id) == 0:
                async with message.channel.typing():
                    await asyncio.sleep(3)
                    await message.reply(choice(reactions), mention_author=False)
            else:
                await shark_react(message)

# music functionality
# all sorts of classes for playing songs in vc. you may mostly ignore these since vc implementation is mostly complete.
class VoiceError(Exception):
    pass

class YTDLError(Exception):
    pass

class MixedAudioSource(discord.AudioSource):
    def __init__(self, music_source: discord.AudioSource, *, music_volume_when_tts: float = volume_adjustment, tts_volume_when_mixed: float = tts_volume_adjustment) -> None:
        self.music_source = music_source
        self.tts_source: Optional[discord.AudioSource] = None
        self.music_volume_when_tts = music_volume_when_tts
        self.tts_volume_when_mixed = tts_volume_when_mixed
        self._tts_done: Optional[asyncio.Event] = None

    def start_tts(self, tts_source: discord.AudioSource) -> asyncio.Event:
        self.tts_source = tts_source
        self._tts_done = asyncio.Event()
        return self._tts_done

    def clear_tts(self) -> None:
        self.tts_source = None
        if self._tts_done and not self._tts_done.is_set():
            self._tts_done.set()
        self._tts_done = None

    def is_opus(self) -> bool:
        return False

    def _mix_frames(self, music_frame: bytes, tts_frame: bytes) -> bytes:
        if not music_frame and not tts_frame:
            return b""

        max_len = max(len(music_frame), len(tts_frame))
        if len(music_frame) < max_len:
            music_frame = music_frame.ljust(max_len, b"\x00")
        if len(tts_frame) < max_len:
            tts_frame = tts_frame.ljust(max_len, b"\x00")

        scaled_music = audioop.mul(music_frame, 2, self.music_volume_when_tts)
        scaled_tts = audioop.mul(tts_frame, 2, self.tts_volume_when_mixed)

        mixed = audioop.add(scaled_music, scaled_tts, 2)
        return mixed

    def read(self) -> bytes:
        music_frame = b""
        if self.music_source:
            music_frame = self.music_source.read()

        if not self.tts_source:
            return music_frame

        tts_frame = self.tts_source.read()

        if not tts_frame:
            if self._tts_done and not self._tts_done.is_set():
                self._tts_done.set()
            self.tts_source = None
            self._tts_done = None
            return music_frame

        return self._mix_frames(music_frame, tts_frame)

    def cleanup(self) -> None:
        if self.music_source:
            self.music_source.cleanup()
        if self.tts_source:
            self.tts_source.cleanup()

class YTDLSource(discord.PCMVolumeTransformer):
    YTDLP_COOKIES_BROWSER = 'firefox'
    # change the browser if you want to test,
    # but then change back to firefox once finished testing as that is the browser neel's server relies on.
    # MAKE SURE YOU ARE SIGNED INTO YOUTUBE ON YOUR BROWSER WITH THE ASSOCIATED COOKIES!

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 1.0):
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
    async def _extract_info(cls, search: str):
        cmd = [
            'yt-dlp',
            '--dump-single-json',
            '--no-playlist',
            '--default-search', 'auto',
            '--no-check-certificate',
            '--remote-components', 'ejs:github',
            '-f', 'bestaudio[ext=m4a]/bestaudio/best',
            '--cookies-from-browser', cls.YTDLP_COOKIES_BROWSER,
            search,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            stderr_str = stderr.decode(errors='replace').strip()
            raise YTDLError(f'Wups! yt-dlp failed: {stderr_str or "unknown error"}')

        stdout_str = stdout.decode(errors='replace').strip()
        if not stdout_str:
            raise YTDLError("Wups! yt-dlp returned no data")

        try:
            return json.loads(stdout_str)
        except json.JSONDecodeError:
            raise YTDLError("Wups! Couldn't parse yt-dlp output")

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        data = await cls._extract_info(search)
        if data is None:
            raise YTDLError(f"Wups! Couldn\'t find anything that matches `{search}`")

        if 'entries' in data:
            info = None
            for entry in data['entries']:
                if entry:
                    info = entry
                    break
        else:
            info = data

        if not info:
            raise YTDLError(f"Wups! Couldn\'t find anything that matches `{search}`")

        return cls(
            ctx,
            discord.FFmpegPCMAudio(
                info['url'],
                before_options='-re -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                options='-vn',
            ),
            data=info,
        )

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        parts = [days, hours, minutes, seconds]
        start_idx = None
        for i, part in enumerate(parts):
            if part != 0:
                start_idx = i
                break
        if start_idx is None or start_idx > 2:
            start_idx = 2

        formatted_parts = [f"{part:02d}" for part in parts[start_idx:]]
        return ':'.join(formatted_parts)

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
        self.mixer = None
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
            except asyncio.CancelledError:
                if self.voice and not self.voice.is_connected():
                    await self.stop()
                return
            except Exception as e:
                print(f"Unexpected error in audio_player_task: {e}")
                await self.stop()
                return

            # ensure current song respects volume
            self.current.source.volume = self._volume

            # create a mixed audio source for this song, allowing tts overlay
            self.mixer = MixedAudioSource(self.current.source, music_volume_when_tts=volume_adjustment)
            self.voice.play(self.mixer, after=self.play_next_song)
            print(f'{Style.BRIGHT}Playing {Fore.MAGENTA}{self.current.source.__str__()[2:-2]}{Fore.RESET} in {Style.RESET_ALL}{Fore.BLUE}{self.voice.channel.name}{Fore.RESET}')
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
        if hasattr(self, 'audio_player') and not self.audio_player.done():
            self.audio_player.cancel()
            try:
                await self.audio_player
            except asyncio.CancelledError:
                pass
        if self.voice:
            await self.voice.disconnect()
            self.voice = None

# bot helper functions
# create_list, update_birthday, create_birthday_list, check_reaction_board, add_to_board, reply, set_voice, add_coins, subtract_coins, dual_spend, add_item, subtract_item, dep, wd, direct_to_bank, stolen_funds, in_wom_shenanigans, in_channels, in_threads, assert_cooldown, capitalize_string, parse_total_duration, shark_react, wups, get_login_time, load_info, load_emulation
def create_list(filename):
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
    if not os.path.exists('csv/birthdays.csv'):
        with open(f'csv/birthdays.csv', 'w'):
            pass # creates csv file
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
    already_on_board = False
    board_msg = None

    async for msg in channel.history():
        if msg.embeds and msg.embeds[0].description == f'[Original Message]({message.jump_url})':
            already_on_board = True
            board_msg = msg
            break

    embed = discord.Embed(color=discord.Color.gold(), description=f'[Original Message]({message.jump_url})')
    embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
    embed.set_thumbnail(url=message.author.avatar.url)
    embed.add_field(name='Channel', value=f'<#{message.channel.id}>', inline=True)
    embed.add_field(name='Message', value=f'{str(message.content)}', inline=True)

    if not already_on_board:
        try:
            id = message.author.id
            karma = int(lists["karma"][str(id)])
            if board_name == "hot-seat":
                if karma < 6:
                    add_item("karma", id, 1)
            else:
                if karma > 2:
                    if subtract_item("karma", id, 1):
                        pass
        except:
            pass # probably a bot

    if message.attachments:
        embed.set_image(url=message.attachments[0].url)

    for reaction in message.reactions:
        if str(reaction.emoji) == board_emoji:
            board_reaction = reaction
            embed.set_footer(text=f'{board_reaction.count} {board_text}')
            break

    if already_on_board and board_msg is not None:
        return await board_msg.edit(embed=embed)
    else:
        return await channel.send(embed=embed)

async def reply(ctx, content: str):
    return await ctx.reply(content, mention_author=False)

def set_voice(userID: int, voice_id: str):
    fieldnames = ['user_id', 'voice']
    found = False
    rows = []
    if os.path.exists('csv/voice.csv'):
        with open('csv/voice.csv', 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row.get('user_id') == str(userID):
                    rows.append({'user_id': str(userID), 'voice': voice_id})
                    found = True
                else:
                    rows.append(row)
    if not found:
        rows.append({'user_id': str(userID), 'voice': voice_id})
    os.makedirs('csv', exist_ok=True)
    with open('csv/voice.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    create_list("voice")


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

def dual_spend(userID: int, spending: int) -> bool:
    handBal = int(lists['coins'][str(userID)])
    bankBal = int(lists['bank'][str(userID)])
    totalBal = handBal + bankBal

    if totalBal < spending:
        return False

    spendingLeft = spending

    if handBal < spending:
        if subtract_coins(userID, handBal):
            spendingLeft -= handBal
        if stolen_funds(userID, spendingLeft):
            pass
        return True
    else:
        if subtract_coins(userID, spending):
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
        await reply(ctx, "ask for or make a wom-shenanigans channel first, stupid")
        return False
    if not ctx.message.channel.id == wom_shenanigans.id:
        await shark_react(ctx.message)
        await reply(ctx, f"go to <#{wom_shenanigans.id}>, jackass")
        return False
    return True

async def in_channels(ctx, channels: list, giveResponse: bool):
    channelName = ctx.message.channel.name
    ids = []
    for channel in channels:
        ids.append(f"<#{discord.utils.get(ctx.guild.channels, name=channel).id}>")
    if channelName not in channels:
        if giveResponse:
            await shark_react(ctx.message)
            await reply(ctx, f"this command can only be used in the following channels: {", ".join(ids)}. go to one of those channels, jackass")
        return False
    return True

async def in_threads(ctx, threads: list, giveResponse: bool):
    threadName = ctx.message.channel.name
    ids = []
    for thread in threads:
        ids.append(f"<#{discord.utils.get(ctx.guild.threads, name=thread).id}>")
    if threadName not in threads:
        if giveResponse:
            await shark_react(ctx.message)
            await reply(ctx, f"this command can only be used in the following threads: {", ".join(ids)}. go to one of those channels, jackass")
        return False
    return True

def assert_cooldown(command, user_id):
    global last_executed

    def cleanup_old_cooldowns(command):
        global last_executed
        current_time = time.time()
        to_remove = [user_id for user_id, timestamp in last_executed[command].items() 
                    if current_time - timestamp > 3600]
        for user_id in to_remove:
            del last_executed[command][user_id]

    if random.randint(1, 100) == 1:
        cleanup_old_cooldowns(command)
    if user_id not in last_executed[command] or last_executed[command][user_id] + cooldowns[command] < time.time():
        last_executed[command][user_id] = time.time()
        return 0
    return round(last_executed[command][user_id] + cooldowns[command] - time.time())

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
        if ':' in duration:
            parts = duration.split(':')
            if len(parts) == 4:
                days, hours, minutes, seconds = map(int, parts)
                all_seconds += days * 86400 + hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                all_seconds += hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2:
                minutes, seconds = map(int, parts)
                all_seconds += minutes * 60 + seconds
        else:
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

    parts = [days, hours, minutes, seconds]
    start_idx = None
    for i, part in enumerate(parts):
        if part != 0:
            start_idx = i
            break
    if start_idx is None or start_idx > 2:
        start_idx = 2
    
    formatted_parts = [f"{part:02d}" for part in parts[start_idx:]]
    return ':'.join(formatted_parts)

async def shark_react(message: discord.Message):
    return await message.add_reaction('🦈')

async def wups(ctx, content: str):
    await shark_react(ctx.message)
    return await reply(ctx, content=f"Wups! {content}...")

def get_login_time(tz: str) -> str:
    return f"Time: {datetime.now(timezone(tz)).strftime('%m/%d/%Y, %I:%M:%S %p')}\nTimezone: {tz}\n"

def load_info(info: str):
    file_path = os.path.join(os.path.dirname(__file__), "docs", f"{info}.txt")
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

def load_emulation():
    file_path = os.path.join(os.path.dirname(__file__), "docs", "consoles.txt")
    with open(file_path, "r", encoding="utf-8") as file:
        emuDict = {
            line.strip(): {
                "links": [],
                "instructions": ""
            }
            for line in file if line.strip()
        }
    file_path = os.path.join(os.path.dirname(__file__), "docs", "links.txt")
    with open(file_path, "r", encoding="utf-8") as file:
        for key in emuDict.keys():
            line = file.readline().strip()
            emuDict[key]["links"] = [part.strip() for part in line.split(",")]
    file_path = os.path.join(os.path.dirname(__file__), "docs", "instructions.txt")
    with open(file_path, "r", encoding="utf-8") as file:
        for key in emuDict.keys():
            emuDict[key]["instructions"] = file.readline().strip().replace("\\n", "\n")

    return emuDict
