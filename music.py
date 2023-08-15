# all imports
import asyncio
import functools
import itertools
import math
import random
import discord
import yt_dlp as youtube_dl
from discord.ext import commands
from utils import cog_check
import nacl

# j, l, np, ps, res, st, sk, q, sh, r, p
# youtube dl initialization starts here
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

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)
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
            raise YTDLError(f"Couldn\'t fetch `{webpage_url}`...")
    
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
        
        duration = []
        if days > 0:
            if days == 1:
                duration.append('1 day')
            else:
                duration.append(f'{days} days')
        if hours > 0:
            if hours == 1:
                duration.append('1 hour')
            else:
                duration.append(f'{hours} hours')
        if minutes > 0:
            if minutes == 1:
                duration.append('1 minute')
            else:
                duration.append(f'{minutes} minutes')
        if seconds > 0:
            if seconds == 1:
                duration.append('1 second')
            else:
                duration.append(f'{seconds} seconds')
        return ', '.join(duration)

class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (discord.Embed(title='Now playing', description=f'**{self.source.title}**', color=discord.Color.green())
            .add_field( name='Duration', value=self.source.duration)
            .add_field(name='Requested by', value=self.requester.mention)
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
    
    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    @commands.command(name='join', aliases=['j'], invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        if await cog_check(ctx):
            destination = ctx.author.voice.channel
            ctx.voice_state.voice = await destination.connect()
            return await ctx.message.add_reaction('✅')

    @commands.command(name='leave', aliases=['l'])
    async def _leave(self, ctx: commands.Context):
        if await cog_check(ctx):
            if not ctx.voice_state.voice:
                return await ctx.reply('Wups! I\'m not connected to any voice channel...', mention_author=False)
            if ctx.voice_client:
                if ctx.voice_client.channel != ctx.author.voice.channel:
                    return await ctx.reply('Wups! You\'re not in my voice channel...', mention_author=False)
            await ctx.voice_state.stop()
            del self.voice_states[ctx.guild.id]
            await ctx.message.add_reaction('👋')

    @commands.command(name='now', aliases=['np'])
    async def _now(self, ctx: commands.Context):
        if await cog_check(ctx):
            if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
                return await ctx.reply(embed=ctx.voice_state.current.create_embed(), mention_author=False)
            else:
                return await ctx.reply('Wups! I\'m currently not playing anything...', mention_author=False)

    @commands.command(name='pause', aliases=['ps'])
    async def _pause(self, ctx: commands.Context):
        if await cog_check(ctx):
            if ctx.voice_client:
                if ctx.voice_client.channel != ctx.author.voice.channel:
                    return await ctx.reply('Wups! You\'re not in my voice channel...', mention_author=False)
            if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
                ctx.voice_state.voice.pause()
                return await ctx.message.add_reaction('⏸️')
            else:
                return await ctx.reply('Wups! Nothing to pause...', mention_author=False)

    @commands.command(name='resume', aliases=['res'])
    async def _resume(self, ctx: commands.Context):
        if await cog_check(ctx):
            if ctx.voice_client:
                if ctx.voice_client.channel != ctx.author.voice.channel:
                    return await ctx.reply('Wups! You\'re not in my voice channel...', mention_author=False)
            if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
                ctx.voice_state.voice.resume()
                await ctx.message.add_reaction('▶️')
            else:
                return await ctx.reply('Wups! Nothing to resume...', mention_author=False)
    
    @commands.command(name='stop', aliases=['st'])
    async def _stop(self, ctx: commands.Context):
        if await cog_check(ctx):
            if ctx.voice_client:
                if ctx.author.voice and ctx.voice_client.channel != ctx.author.voice.channel:
                    return await ctx.reply('Wups! You\'re not in my voice channel...', mention_author=False)
            if ctx.voice_state.is_playing:
                ctx.voice_state.songs.clear()
                ctx.voice_state.voice.stop()
                return await ctx.message.add_reaction('⏹')
            else:
                return await ctx.reply('Wups! I\'m not playing any music right now...', mention_author=False)
    
    @commands.command(name='skip', aliases=['sk'])
    async def _skip(self, ctx: commands.Context):
        if await cog_check(ctx):
            voter = ctx.message.author
            djRole = discord.utils.get(ctx.guild.roles, name="DJ")
            if ctx.voice_client:
                if ctx.voice_client.channel != voter.voice.channel:
                    return await ctx.reply('Wups! You\'re not in my voice channel...', mention_author=False)
            if not ctx.voice_state.is_playing:
                return await ctx.reply('Wups! I\'m not playing any music right now...', mention_author=False)
            if voter == ctx.voice_state.current.requester or djRole in voter.roles or voter.guild_permissions.administrator:
                ctx.voice_state.skip()
                return await ctx.message.add_reaction('⏭')
            else:
                return await ctx.reply('Wups! You didn\'t request this song to be played (DJs and adminstrators are unaffected)...', mention_author=False)
    
    @commands.command(name='queue', aliases=['q'])
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        if await cog_check(ctx):
            if page < 1:
                return await ctx.reply('Wups! Invalid page number. Must be greater than or equal to `1`...', mention_author=False)
            if len(ctx.voice_state.songs) == 0:
                return await ctx.reply('Wups! Queue is empty...', mention_author=False)
            items_per_page = 25
            pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)
            if page > pages:
                return await ctx.reply(f'Wups! Invalid page number. Must be less than or equal to `{pages}`...', mention_author=False)
            start = (page - 1) * items_per_page
            end = start + items_per_page
            queue = ''
            for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
                queue += f'`{i+1}.` **{song.source.title}** (*{song.source.duration}*)\n'
            embed = (discord.Embed(color=discord.Color.green(),description=f'**{len(ctx.voice_state.songs)} tracks:**\n\n{queue}')
                .set_footer(text=f'Viewing page {page}/{pages}'))
            return await ctx.reply(embed=embed, mention_author=False)
    
    @commands.command(name='shuffle', aliases=['sh'])
    async def _shuffle(self, ctx: commands.Context):
        if await cog_check(ctx):
            author = ctx.message.author
            djRole = discord.utils.get(ctx.guild.roles, name="DJ")
            
            if ctx.voice_client:
                if ctx.voice_client.channel != author.voice.channel:
                    return await ctx.reply('Wups! You\'re not in my voice channel...', mention_author=False)
            if author.guild_permissions.administrator or djRole in author.roles:
                if len(ctx.voice_state.songs) == 0:
                    return await ctx.reply('Wups! Queue is empty...', mention_author=False)
                else:
                    ctx.voice_state.songs.shuffle()
                    return await ctx.message.add_reaction('✅')
            else:
                return await ctx.reply('Wups! You don\'t have the permissions to use this. Must be either a DJ or administrator...', mention_author=False)
    
    @commands.command(name='remove', aliases=['r'])
    async def _remove(self, ctx: commands.Context, index: int):
        if await cog_check(ctx):
            queue = ctx.voice_state.songs
            if ctx.voice_client:
                if ctx.voice_client.channel != ctx.author.voice.channel:
                    return await ctx.reply('Wups! You\'re not in my voice channel...', mention_author=False)
            if len(queue) == 0:
                return await ctx.reply('Wups! Queue is empty...', mention_author=False)
            elif index < 0 or index == 0 or index > len(queue):
                return await ctx.reply('Wups! Index out of bounds...', mention_author=False)
            ctx.voice_state.songs.remove(index - 1)
            return await ctx.message.add_reaction('✅')
    
    @commands.command(name='play', aliases=['p'])
    async def _play(self, ctx: commands.Context, *, search: str):
        if await cog_check(ctx):
            if not ctx.voice_state.voice:
                return await ctx.reply('Wups! I\'m not connected to a voice channel...', mention_author=False)
            if ctx.voice_client:
                if ctx.voice_client.channel != ctx.author.voice.channel:
                    return await ctx.reply('Wups! I\'m already in a voice channel...', mention_author=False)
            async with ctx.typing():
                try:
                    source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
                except YTDLError as e:
                    return await ctx.reply(f'Wups! An error occurred while processing this request... ({str(e)})', mention_author=False)
                else:
                    song = Song(source)
                    await ctx.voice_state.songs.put(song)
                    await ctx.reply(f'Queued {str(source)}', mention_author=False)
    
    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.reply('Wups! You\'re not connected to any voice channel...', mention_author=False)
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                return await ctx.reply('Wups! I\'m already in a voice channel...', mention_author=False)

async def setup(bot):
    await bot.add_cog(Music(bot))
