import discord
from discord.ext import commands
import math
import os
import re
from colorama import Fore, Back, Style
from asyncio import subprocess, create_subprocess_shell
import nacl # necessary for opus

from utils import VoiceState, YTDLSource, YTDLError, Song # utils classes 
from utils import reply, wups, parse_total_duration, in_channels # utils functions

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}
        self.platforms = ['spotify', 'youtube', 'soundcloud']

    # backend helpers
    # this is to initiate the voice call that the bot will be in
    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state
        return state

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def _run_download(self, cmd: str, name: str, colors: tuple, error_checks: dict = None):
        """Helper to run download subprocess and handle output."""
        print(f"{Style.BRIGHT}Downloading from {colors[0]}{colors[1]}{name}{Fore.RESET}{Back.RESET}{Style.RESET_ALL}...")
        proc = await create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        stdout_str, stderr_str = stdout.decode(), stderr.decode()
        print(f"{Style.BRIGHT}Out{Style.RESET_ALL}:\n{stdout_str}{Style.BRIGHT}Err{Style.RESET_ALL}:\n{stderr_str}\n")
        
        if error_checks:
            for check, error_msg in error_checks.items():
                if check in stdout_str or check in stderr_str:
                    return False, error_msg
        if proc.returncode != 0:
            return False, "I couldn't download anything. Try again"
        return True, None

    async def _send_downloaded_files(self, ctx, msg):
        """Helper to send downloaded MP3 files and clean up."""
        new_files = [f for f in os.listdir('.') if f.endswith(".mp3")]
        for file in new_files:
            file_path = os.path.join('.', file)
            try:
                await ctx.reply(content='Here is your song!', file=discord.File(file_path))
            except:
                os.remove(file_path)
                await msg.delete()
                return await wups(ctx, 'The file was too big for me to send')
            os.remove(file_path)
        return await msg.delete()

    # commands that are usable
    # join, leave, now, pause, resume, stop, skip, queue, shuffle, remove, moveto, play, grabber
    @commands.command(name='join')
    async def _join(self, ctx: commands.Context):
        destination = ctx.author.voice.channel if ctx.author.voice else None 
        try:
            ctx.voice_state.voice = await destination.connect()
            print(f'{Style.BRIGHT}Joined {Style.RESET_ALL}{Fore.BLUE}{ctx.author.voice.channel.name}{Fore.RESET}')
            return await ctx.message.add_reaction('✅')
        except:
            return await wups(ctx, 'I couldn\'t connect to your voice channel. Maybe you\'re not in one or I\'m in a different one')
      
    @commands.command(name='leave')
    async def _leave(self, ctx: commands.Context):
        if not ctx.voice_state.voice:
            return await wups(ctx, 'I\'m not connected to any voice channel')
        if ctx.voice_client:
            if ctx.author.voice is None or ctx.voice_client.channel != ctx.author.voice.channel:
                return await wups(ctx, 'You\'re not in my voice channel')
        await ctx.voice_state.stop()
        print(f'{Style.BRIGHT}Left {Style.RESET_ALL}{Fore.BLUE}{ctx.author.voice.channel.name}{Fore.RESET}')
        del self.voice_states[ctx.guild.id]
        return await ctx.message.add_reaction('👋')

    @commands.command(name='now')
    async def _now(self, ctx: commands.Context):
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            return await ctx.reply(embed=ctx.voice_state.current.create_embed(), mention_author=False)
        else:
            return await wups(ctx, 'I\'m currently not playing anything')

    @commands.command(name='pause')
    async def _pause(self, ctx: commands.Context):
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel or ctx.author.voice is None:
                return await wups(ctx, 'You\'re not in my voice channel')
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            return await ctx.message.add_reaction('⏸️')
        else:
            return await wups(ctx, 'Nothing to pause')

    @commands.command(name='resume')
    async def _resume(self, ctx: commands.Context):
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel or ctx.author.voice is None:
                return await wups(ctx, 'You\'re not in my voice channel')
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            return await ctx.message.add_reaction('▶️')
        else:
            return await wups(ctx, 'Nothing to resume')

    @commands.command(name='stop')
    async def _stop(self, ctx: commands.Context):
        if ctx.voice_client:
            if ctx.author.voice and ctx.voice_client.channel != ctx.author.voice.channel or ctx.author.voice is None:
                return await wups(ctx, 'You\'re not in my voice channel')
        if ctx.voice_state.is_playing:
            ctx.voice_state.songs.clear()
            ctx.voice_state.voice.stop()
            return await ctx.message.add_reaction('⏹️')
        else:
            return await wups(ctx, 'I\'m not playing any music right now')

    @commands.command(name='skip')
    async def _skip(self, ctx: commands.Context):
        voter = ctx.message.author
        djRole = discord.utils.get(ctx.guild.roles, name="DJ")
        if ctx.voice_client:
            if ctx.voice_client.channel != voter.voice.channel or voter.voice is None:
                return await wups(ctx, 'You\'re not in my voice channel')
        if not ctx.voice_state.is_playing:
            return await wups(ctx, 'I\'m not playing any music right now')
        if voter == ctx.voice_state.current.requester or djRole in voter.roles or voter.guild_permissions.administrator:
            ctx.voice_state.skip()
            return await ctx.message.add_reaction('⏭️')
        else:
            return await wups(ctx, 'You didn\'t request this song to be played (DJs and adminstrators are unaffected)')

    @commands.command(name='queue')
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        if page < 1:
            return await wups(ctx, 'Invalid page number. Must be greater than or equal to `1`')
        if len(ctx.voice_state.songs) == 0:
            return await wups(ctx, 'Queue is empty')
        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)
        if page > pages:
            return await wups(ctx, f'Invalid page number. Must be less than or equal to `{pages}`')
        
        start = (page - 1) * items_per_page
        end = start + items_per_page
        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += f'`{i+1}.` **{song.source.title}** (*{song.source.duration}*){'\n' if i != end else ''}'
        embed = (discord.Embed(color=discord.Color.purple(), title=f'**__{len(ctx.voice_state.songs)} Track{'s' if len(ctx.voice_state.songs) > 1 else ''}__**', description=queue)
                .set_footer(text=f'Viewing page {page}/{pages}\nQueue length: {parse_total_duration([song.source.duration for song in ctx.voice_state.songs])}'))
        return await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name='shuffle')
    async def _shuffle(self, ctx: commands.Context):
        author = ctx.message.author
        djRole = discord.utils.get(ctx.guild.roles, name="DJ")

        if ctx.voice_client:
            if ctx.voice_client.channel != author.voice.channel or author.voice is None:
                return await wups(ctx, 'You\'re not in my voice channel')
        if author.guild_permissions.administrator or djRole in author.roles:
            if len(ctx.voice_state.songs) == 0:
                return await wups(ctx, 'Queue is empty')
            else:
                ctx.voice_state.songs.shuffle()
                return await ctx.message.add_reaction('🔀')
        else:
            return await wups(ctx, 'You don\'t have the permissions to use this. Must be either a DJ or administrator')

    @commands.command(name='remove')
    async def _remove(self, ctx: commands.Context, index: int):
        queue = ctx.voice_state.songs
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel or ctx.author.voice is None:
                return await wups(ctx, 'You\'re not in my voice channel')
        if len(queue) == 0:
            return await wups(ctx, 'Queue is empty')
        elif index < 0 or index == 0 or index > len(queue):
            return await wups(ctx, 'Index out of bounds')
        ctx.voice_state.songs.remove(index - 1)
        return await ctx.message.add_reaction('✅')

    @commands.command(name='moveto')
    async def _moveto(self, ctx: commands.Context, from_index: int, to_index: int):
        author = ctx.message.author
        djRole = discord.utils.get(ctx.guild.roles, name="DJ")
        
        queue = ctx.voice_state.songs
        if ctx.voice_client:
            if ctx.author.voice is None or ctx.voice_client.channel != ctx.author.voice.channel:
                return await wups(ctx, 'You\'re not in my voice channel')
        if author.guild_permissions.administrator or djRole in author.roles:
            if len(queue) == 0:
                return await wups(ctx, 'Queue is empty')
            if from_index < 1 or from_index > len(queue):
                return await wups(ctx, f'Source index out of bounds (must be between 1 and {len(queue)})')
            if to_index < 1 or to_index > len(queue):
                return await wups(ctx, f'Destination index out of bounds (must be between 1 and {len(queue)})')
            if from_index == to_index:
                return await wups(ctx, 'Source and destination positions are the same')
            
            # convert to 0-based indexing
            from_pos = from_index - 1
            to_pos = to_index - 1
            
            # move the song
            song = queue._queue[from_pos]
            del queue._queue[from_pos]
            queue._queue.insert(to_pos, song)
            
            return await ctx.message.add_reaction('✅')
        else:
            return await wups(ctx, 'You don\'t have the permissions to use this. Must be either a DJ or administrator')

    @commands.command(name='play')
    async def _play(self, ctx: commands.Context, *, search: str):
        if not ctx.voice_state.voice: # bot not in vc at all
            return await wups(ctx, 'I\'m not connected to a voice channel')
        if ctx.voice_client:
            if ctx.author.voice is None: # user not in vc at all but bot is
                return await wups(ctx, 'You\'re not connected to a voice channel')
            elif ctx.voice_client.channel != ctx.author.voice.channel: # user in different vc than bot
                return await wups(ctx, 'I\'m already in a different voice channel')
            
        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search)
            except YTDLError as e:
                return await wups(ctx, f'An error occurred while processing this request (`{str(e)}`)')
            else:
                song = Song(source)
                await ctx.voice_state.songs.put(song)
                return await reply(ctx, f'Queued {str(source)}')
            
    @commands.command(name='grabber')
    async def grabber(self, ctx, platform: str, *query):
        query = " ".join(query)
        try:
            if query[0] == '<' and query[-1] == '>':
                query = query[1:-1]
            elif query[0] == '[' and query[-1] == ')':
                return await wups(ctx, "I couldn't download anything in an embedded link. Try again")
            query = re.sub(r'[?&]si=[a-zA-Z0-9_-]+', '', query)
        except IndexError:
            return await wups(ctx, "I need a search query")
        
        if await in_channels(ctx, ["wom-shenanigans", "good-tunes"], True):
            if platform.lower() not in self.platforms:
                return await wups(ctx, 'Invalid platform choice! Must be either `Spotify`, `YouTube`, or `SoundCloud`')
            
            async with ctx.typing():
                msg = await ctx.reply('Hang tight! I\'ll try downloading your song. You\'ll be pinged with your song once I finish.', mention_author=False)
                platform_lower = platform.lower()
                
                if platform_lower == 'spotify':
                    success, error = await self._run_download(
                        f'spotdl download "{query}" --format mp3 --output "{{artist}} - {{title}}.{{output-ext}}" --lyrics synced',
                        'Spotify', (Fore.BLACK, Back.GREEN),
                        {"LookupError": "I couldn't find a song on Spotify with that query. Try again"}
                    )
                elif platform_lower == 'youtube':
                    youtube_url_pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?v=|embed/)|youtu\.be/|m\.youtube\.com/watch\?v=)'
                    download_query = query if re.search(youtube_url_pattern, query) else f'ytsearch:"{query}"'
                    success, error = await self._run_download(
                        f'yt-dlp {download_query} -x --audio-format mp3 -o "%(title)s.%(ext)s" --no-playlist --embed-metadata --embed-thumbnail --remote-components ejs:github',
                        'YouTube', (Fore.WHITE, Back.RED),
                        {'Downloading 0 items': "I couldn't download anything. Try again (Most likely, your search query was invalid.)"}
                    )
                elif platform_lower == 'soundcloud':
                    if not query.startswith('https://soundcloud.com/'):
                        await msg.delete()
                        return await wups(ctx, "I couldn't download anything. Try again (Due to API requirements, you must make sure that you are providing a `https://soundcloud.com/` link as your query.)")
                    query = query[:query.find("?in=")] if "?in=" in query else query
                    query = query.rstrip('/')
                    success, error = await self._run_download(
                        f'scdl -l {query} --onlymp3 --force-metadata --no-playlist',
                        'SoundCloud', (Fore.WHITE, Back.LIGHTRED_EX),
                        {'Found a playlist': "I don't want to bombard you with pings! Try downloading songs individually",
                        'URL is not valid': "Invalid URL! Try again"}
                    )
                
                if not success:
                    await msg.delete()
                    return await wups(ctx, error)
                
                return await self._send_downloaded_files(ctx, msg)


async def setup(bot):
    await bot.add_cog(Music(bot))
