# All imports
import asyncio
import functools
import itertools
import math
import random
import os
import discord
import yt_dlp as youtube_dl
from async_timeout import timeout
from discord.ext import commands
from keep_alive import keep_alive
from dotenv import load_dotenv
import csv

# Sets up WoM on start up
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

client = discord.Client()
bot = commands.Bot(command_prefix = '!w ')

say = print
command_list={}
members=[]
empty_file=False

if not os.path.exists('commands.csv'):
    with open('commands.csv', 'w') as creating_new_csv_file: 
        pass
with open('commands.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    rows = list(csv_reader)
    if len(rows)==0:
        empty_file=True
    else:
        command_list = {}
        for row in rows:
            dict = list(row.values())
            command_list[dict[0]]=dict[1]

bot.remove_command('help')

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds)
    botname = '{0.user.name}'.format(bot)
    members = '\n - '.join(member.name for member in guild.members)
    print(f'{botname} is connected to the following guild:\n{guild.name} (ID: {guild.id})\nMembers:\n - {members}')
  

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''

class VoiceError(Exception):
    pass

class YTDLError(Exception):
    pass

class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
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
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options':
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio,
                 *, data: dict):
        super().__init__(source)
        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data
        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}**'.format(self)

    @classmethod
    async def create_source(cls,
                            ctx: commands.Context,
                            search: str,
                            *,
                            loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()
        partial = functools.partial(cls.ytdl.extract_info,
                                    search,
                                    download=False,
                                    process=False)
        data = await loop.run_in_executor(None, partial)
        if data is None:
            return await ctx.send(
                'Wups! Couldn\'t find anything that matches `{}`...'.format(search))
        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break
            if process_info is None:
                return await ctx.send(
                  'Wups! Couldn\'t find anything that matches `{}`...'.format(search))
        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info,
                                    webpage_url,
                                    download=False)
        processed_info = await loop.run_in_executor(None, partial)
        if processed_info is None:
            return await ctx.send(
              'Wups! Couldn\'t fetch `{}`...'.format(webpage_url))
        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    return await ctx.send(
                        'Wups! Couldn\'t retrieve any matches for `{}`...'.format(
                            webpage_url))
        return cls(ctx,
                   discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS),
                   data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        duration = []
        if days > 0:
            duration.append('{} days'.format(days))
        if hours > 0:
            duration.append('{} hours'.format(hours))
        if minutes > 0:
            duration.append('{} minutes'.format(minutes))
        if seconds > 0:
            duration.append('{} seconds'.format(seconds))
        return ', '.join(duration)

class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (discord.Embed(
            title='Now playing',
            description='```css\n{0.source.title}\n```'.format(self),
            color=discord.Color.purple())
                 .add_field(name='Duration', value=self.source.duration)
                 .add_field(name='Requested by', value=self.requester.mention)
                 .set_thumbnail(url=self.source.thumbnail))
        return embed

class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(
                itertools.islice(self._queue, item.start, item.stop,
                                 item.step))
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
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()

            if not self.loop:
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with timeout(180):  # 3 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send(
                embed=self.current.create_embed())

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

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


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage(
                'This command can\'t be used in DM channels.')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context,
                                error: commands.CommandError):
        await ctx.send('An error occurred: {}'.format(str(error)))

    @commands.command(name='join', invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        try:
          destination = ctx.author.voice.channel
        except:
          return
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='leave')
    async def _leave(self, ctx: commands.Context):
        if not ctx.voice_state.voice:
            return await ctx.send('Wups! I\'m not connected to any voice channel...')
        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name='now')
    async def _now(self, ctx: commands.Context):
        try:
          await ctx.send(embed=ctx.voice_state.current.create_embed())
        except:
          return await ctx.send(f'Wups! Nothing is playing...')

    @commands.command(name='pause')
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.send('Song paused!')
        else:
            await ctx.send('Wups! There was nothing to pause...')

    @commands.command(name='resume')
    async def _resume(self, ctx: commands.Context):
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.send('Song resumed!')
        else:
            await ctx.send('Wups! There was nothing to resume...')

    @commands.command(name='stop')
    async def _stop(self, ctx: commands.Context):
        if ctx.voice_state.is_playing:
            ctx.voice_state.songs.clear()
            ctx.voice_state.voice.stop()
            await ctx.send('Queue cleared!\nSong stopped as well!')
        else:
            await ctx.send('Wups! There was no song to stop playing...')

    @commands.command(name='skip')
    async def _skip(self, ctx: commands.Context):
        if not ctx.voice_state.is_playing:
            return await ctx.send('Wups! I\'m not playing any music right now...')

        voter = ctx.message.author
        if voter == ctx.voice_state.current.requester:
            ctx.voice_state.skip()
            await ctx.send('Song skipped!')

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 3:
                await ctx.message.add_reaction('⏭')
                ctx.voice_state.skip()
            else:
                await ctx.send('Skip vote added, currently at **{}/3**'.format(
                    total_votes))

        else:
            await ctx.send('Wups! You have already voted to skip this song...')

    @commands.command(name='queue')
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        if not isinstance(page, int) or page < 1:
          return await ctx.send(f'Wups! Invalid page number...')
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Wups! Queue is empty...')
        
        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        if page > pages:
          return await ctx.send(f'Wups! You\'re looking too high...')

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end],
                                 start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(
                i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(
            len(ctx.voice_state.songs), queue)).set_footer(
                text='Viewing page {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)

    @commands.command(name='shuffle')
    async def _shuffle(self, ctx: commands.Context):
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Wups! Queue is empty...')

        ctx.voice_state.songs.shuffle()
        await ctx.send('Queue shuffled!')

    @commands.command(name='remove')
    async def _remove(self, ctx: commands.Context, index: int=0):
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Wups! Queue is empty...')
        elif index < 1 or index > len(ctx.voice_state.songs):
            return await ctx.send(f'Wups! Not a valid index...')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.send(f'Song at index {index - 1} removed!')

    # This command is very buggy. It doesn't even play the audio of the song again.
    # I don't want to mess anything up so I'll leave it in, but I don't want anyone
    # else to know of its existence until this gets ironed out
    @commands.command(name='loop')
    async def _loop(self, ctx: commands.Context):
        if not ctx.voice_state.is_playing:
            return await ctx.send('Wups! Nothing is being played at the moment...')

        ctx.voice_state.loop = not ctx.voice_state.loop
        if ctx.voice_state.loop == True:
          await ctx.send('Song looped!')
        elif ctx.voice_state.loop == False:
          await ctx.send('Song unlooped!')

    @commands.command(name='play')
    async def _play(self, ctx: commands.Context, *, search: str=None):
        if search == None:
          return await ctx.send(f'Wups! Invalid query...')
        if not ctx.author.voice or not ctx.author.voice.channel:
            return
          
        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx,search,loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('Wups! An error occurred... {}'.format(str(e)))
            else:
                song = Song(source)
                await ctx.voice_state.songs.put(song)
                await ctx.send('Queued {}!'.format(str(source)))

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send('Wups! You\'re not connected to any voice channel...')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                await ctx.send(f'Wups! I\'m already in a voice channel...')
bot.add_cog(Music(bot))

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round (bot.latency * 1000)}ms')
    await ctx.message.delete()

@bot.command()
async def say(ctx, *args):
    if len(args) < 1:
        await ctx.send(f'Wups! You need something for me to say...')
        return
    response = ''
    for arg in args:
        response = response + ' ' + arg
    await ctx.channel.send(response)
    await ctx.message.delete()
    
@bot.command()
async def createcommand(ctx, *args):
    if len(args) < 2:
        await ctx.send(f'Wups! Not the correct number of arguments! You need two arguments to create a new command...')
        # This just rules out the edge case that some moron might just do "!w createcommand" or just list a command name and no output.
    elif not ctx.author.guild_permissions.manage_messages:
        await ctx.send(f"Wups! You do not have the required permissions...")
    else:
        array = [arg for arg in args]
        name = array[0]
        output = array[1]
        for num in range(0,2):
            array.remove(array[0])
        for arg in array:
            output = output + ' ' + arg
        with open('commands.csv', 'a', newline='') as csvfile:
            fieldnames = ['command_name', 'command_output']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if empty_file:
                writer.writeheader()
            if name in list(command_list.keys()):
                await ctx.send(f'Wups! This command already exists...')
            else:
                writer.writerow({'command_name': name, 'command_output': output})
                await ctx.send(f"The command " + name + " has been created!")
                command_list[name] = output

@bot.command()
async def customcommands(ctx):
    commandList = list(command_list.keys())
    commands = ', '.join(commandList) 
    if commands == '':
        await ctx.send(f'Wups! There are no custom commands...')
    else:
        await ctx.send(commands)

@bot.command()
async def help(ctx, type=None):
    if type == None:
        embed = discord.Embed(color = discord.Color.purple())
        embed.set_author(name='Need help?')

        embed.add_field(name='!w help basic', value='Prints out all my basic commands', inline=False)
        embed.add_field(name='!w help music', value='Prints out all my music commands', inline=False)

        await ctx.send(embed=embed)
    elif type.lower() == 'basic':
        embed = discord.Embed(color = discord.Color.purple())
        embed.set_author(name='Basic Commands')

        embed.add_field(name='!w ping', value='Returns my respond time in milliseconds', inline=False)
        embed.add_field(name='!w say (input)', value='Repeats the input that the user specifies', inline=False)
        embed.add_field(name='!w createcommand (name) (output)', value='Create your own commands that make me send custom text or links [Admin Only]', inline=False)
        embed.add_field(name='!w customcommands', value="Displays a list of the server's custom commands", inline=False)

        await ctx.send(embed=embed)
    elif type.lower() == 'music':
        embed = discord.Embed(color = discord.Color.purple())
        embed.set_author(name='Music Commands')

        embed.add_field(name='!w join', value='Joins the voice chat that you are in', inline=False)
        embed.add_field(name='!w leave', value='Leaves the voice chat that I am in', inline=False)
        embed.add_field(name='!w play (YouTube URL or search query)', value='While I\'m in voice call, I will play the song from the YouTube URL you provide me. Alternatively, if you give me a search query I\'ll play the first result from search.', inline=False)
        embed.add_field(name='!w now', value='Prints whatever song I\'m playing')
        embed.add_field(name='!w pause', value='Pauses any music that I\'m playing', inline=False)
        embed.add_field(name='!w resume', value='Resumes any paused music', inline=False)
        embed.add_field(name='!w stop', value='Stops any playing music entirely', inline=False)
        embed.add_field(name='!w skip', value='Skips the song I\'m playing. If the original requestor inputs this command, I will skip automatically, otherwise 3 votes will be required to skip a song.', inline=False)
        embed.add_field(name='!w queue (optional: page number)', value='Prints out the queue of songs. Occasionally, you may need to enter a page number for the queue', inline=False)
        embed.add_field(name='!w shuffle', value='Shuffles the queue', inline=False)
        embed.add_field(name='!w remove (index)', value='Removes a song from the queue at the specified index')

        await ctx.send(embed=embed)
    else:
        await ctx.send(f'Wups! Invalid query...')

@bot.event
async def on_message(message):
    if message.content[0:3] == "!w " and message.content.split()[1] in list(command_list.keys()):
        await message.channel.send(command_list[message.content.split()[1]])
    else:   
        if message.content.lower() == "me":
            await message.channel.send('<:WoM:836128658828558336>')
        if "yoshi" in message.content.lower().split(" "):
            await message.add_reaction('<:full:1028536660918550568>')
        if "3ds" in message.content.lower().split(" "):
            await message.add_reaction('<:megalon:1078914494132129802>')
        if "yuri" in message.content.lower().split(" "):
            await message.add_reaction('<:vers:804766992644702238>')
        if "verstie" in message.content.lower().split(" "):
            await message.add_reaction('<:verstie:1078929624429498430>')
            
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if not ctx.message.content.split()[1] in list(command_list.keys()):
        await ctx.send(f'Wups! Try `!w help`... ({error})')

keep_alive()
bot.run(TOKEN)
