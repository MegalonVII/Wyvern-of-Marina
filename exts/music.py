import discord
from discord.ext import commands
import math
from colorama import Fore, Style
from utils import *
import nacl

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    # frontend helpers
    # these functions make the bot act according to certain contexts, such as being used in dms or being used as an interaction
    async def respond(self, ctx: commands.Context, message: str, emoji: str):
        try:
            return await ctx.message.add_reaction(emoji)
        except:
            return await ctx.reply(f"{message} {emoji}", mention_author=False)

    async def cog_check(self, ctx: commands.Context) -> bool:
        if not ctx.guild:
            return False
        return True
    
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

    # commands that are usable
    # join*, leave*, now, pause*, resume*, stop*, skip*, queue, shuffle*, remove*, play
    @commands.command(name='join')
    async def _join(self, ctx: commands.Context):
        destination = ctx.author.voice.channel if ctx.author.voice else None 
        try:
            ctx.voice_state.voice = await destination.connect()
            print(f'{Style.BRIGHT}Joined {Style.RESET_ALL}{Fore.BLUE}{ctx.author.voice.channel.name}{Fore.RESET}{Style.BRIGHT} in {Style.RESET_ALL}{Fore.GREEN}{ctx.author.guild.name} ({ctx.author.guild.id}){Fore.RESET}')
            return await Music.respond(self, ctx, f'Joined `{ctx.author.voice.channel.name}`!', '✅')
        except:
            await shark_react(ctx.message)
            return await ctx.reply('Wups! I couldn\'t connect to your voice channel. Maybe you\'re not in one or I\'m in a different one...', mention_author=False, ephemeral=True)
      
    @commands.command(name='leave')
    async def _leave(self, ctx: commands.Context):
        if not ctx.voice_state.voice:
            await shark_react(ctx.message)
            return await ctx.reply('Wups! I\'m not connected to any voice channel...', mention_author=False)
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel or ctx.author.voice is None:
                await shark_react(ctx.message)
                return await ctx.reply('Wups! You\'re not in my voice channel...', mention_author=False)
        await ctx.voice_state.stop()
        print(f'{Style.BRIGHT}Left {Style.RESET_ALL}{Fore.BLUE}{ctx.author.voice.channel.name}{Fore.RESET}{Style.BRIGHT} in {Style.RESET_ALL}{Fore.GREEN}{ctx.author.guild.name} ({ctx.author.guild.id}){Fore.RESET}')
        del self.voice_states[ctx.guild.id]
        return await Music.respond(self, ctx, 'Goodbye!', '👋')

    @commands.command(name='now')
    async def _now(self, ctx: commands.Context):
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            return await ctx.reply(embed=ctx.voice_state.current.create_embed(), mention_author=False)
        else:
            await shark_react(ctx.message)
            return await ctx.reply('Wups! I\'m currently not playing anything...', mention_author=False, ephemeral=True)

    @commands.command(name='pause')
    async def _pause(self, ctx: commands.Context):
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel or ctx.author.voice is None:
                await shark_react(ctx.message)
                return await ctx.reply('Wups! You\'re not in my voice channel...', mention_author=False, ephemeral=True)
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            return await Music.respond(self, ctx, 'Paused!', '⏸️')
        else:
            await shark_react(ctx.message)
            return await ctx.reply('Wups! Nothing to pause...', mention_author=False, ephemeral=True)

    @commands.command(name='resume')
    async def _resume(self, ctx: commands.Context):
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel or ctx.author.voice is None:
                await shark_react(ctx.message)
                return await ctx.reply('Wups! You\'re not in my voice channel...', mention_author=False, ephemeral=True)
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            return await Music.respond(self, ctx, 'Resumed!', '▶️')
        else:
            await shark_react(ctx.message)
            return await ctx.reply('Wups! Nothing to resume...', mention_author=False, ephemeral=True)

    @commands.command(name='stop')
    async def _stop(self, ctx: commands.Context):
        if ctx.voice_client:
            if ctx.author.voice and ctx.voice_client.channel != ctx.author.voice.channel or ctx.author.voice is None:
                return await ctx.reply('Wups! You\'re not in my voice channel...', mention_author=False, ephemeral=True)
        if ctx.voice_state.is_playing:
            ctx.voice_state.songs.clear()
            ctx.voice_state.voice.stop()
            return await Music.respond(self, ctx, 'Stopped!', '⏹️')
        else:
            return await ctx.reply('Wups! I\'m not playing any music right now...', mention_author=False, ephemeral=True)

    @commands.command(name='skip')
    async def _skip(self, ctx: commands.Context):
        voter = ctx.message.author
        djRole = discord.utils.get(ctx.guild.roles, name="DJ")
        if ctx.voice_client:
            if ctx.voice_client.channel != voter.voice.channel or voter.voice is None:
                await shark_react(ctx.message)
                return await ctx.reply('Wups! You\'re not in my voice channel...', mention_author=False, ephemeral=True)
        if not ctx.voice_state.is_playing:
            await shark_react(ctx.message)
            return await ctx.reply('Wups! I\'m not playing any music right now...', mention_author=False, ephemeral=True)
        if voter == ctx.voice_state.current.requester or djRole in voter.roles or voter.guild_permissions.administrator:
            ctx.voice_state.skip()
            return await Music.respond(self, ctx, 'Skipped!', '⏭️')
        else:
            await shark_react(ctx.message)
            return await ctx.reply('Wups! You didn\'t request this song to be played (DJs and adminstrators are unaffected)...', mention_author=False)

    @commands.command(name='queue')
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        if page < 1:
            await shark_react(ctx.message)
            return await ctx.reply('Wups! Invalid page number. Must be greater than or equal to `1`...', mention_author=False, ephemeral=True)
        if len(ctx.voice_state.songs) == 0:
            await shark_react(ctx.message)
            return await ctx.reply('Wups! Queue is empty...', mention_author=False, ephemeral=True)
        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)
        if page > pages:
            await shark_react(ctx.message)
            return await ctx.reply(f'Wups! Invalid page number. Must be less than or equal to `{pages}`...', mention_author=False, ephemeral=True)
        
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
                await shark_react(ctx.message)
                return await ctx.reply('Wups! You\'re not in my voice channel...', mention_author=False)
        if author.guild_permissions.administrator or djRole in author.roles:
            if len(ctx.voice_state.songs) == 0:
                await shark_react(ctx.message)
                return await ctx.reply('Wups! Queue is empty...', mention_author=False)
            else:
                ctx.voice_state.songs.shuffle()
                return await Music.respond(self, ctx, 'Queue shuffled!', '🔀')
        else:
            await shark_react(ctx.message)
            return await ctx.reply('Wups! You don\'t have the permissions to use this. Must be either a DJ or administrator...', mention_author=False)

    @commands.command(name='remove')
    async def _remove(self, ctx: commands.Context, index: int):
        queue = ctx.voice_state.songs
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel or ctx.author.voice is None:
                await shark_react(ctx.message)
                return await ctx.reply('Wups! You\'re not in my voice channel...', mention_author=False, ephemeral=True)
        if len(queue) == 0:
            await shark_react(ctx.message)
            return await ctx.reply('Wups! Queue is empty...', mention_author=False, ephemeral=True)
        elif index < 0 or index == 0 or index > len(queue):
            await shark_react(ctx.message)
            return await ctx.reply('Wups! Index out of bounds...', mention_author=False, ephemeral=True)
        ctx.voice_state.songs.remove(index - 1)
        return await Music.respond(self, ctx, 'Song removed from queue!', '✅')

    @commands.command(name='play')
    async def _play(self, ctx: commands.Context, *, search: str):
        if not ctx.voice_state.voice:
            await shark_react(ctx.message)
            return await ctx.reply('Wups! I\'m not connected to a voice channel...', mention_author=False, ephemeral=True)
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                await shark_react(ctx.message)
                return await ctx.reply('Wups! I\'m already in a voice channel...', mention_author=False, ephemeral=True)
            
        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search)
            except YTDLError as e:
                await shark_react(ctx.message)
                return await ctx.reply(f'Wups! An error occurred while processing this request... ({str(e)})', mention_author=False, ephemeral=True)
            else:
                song = Song(source)
                await ctx.voice_state.songs.put(song)
                return await ctx.reply(f'Queued {str(source)}', mention_author=False)

async def setup(bot):
    await bot.add_cog(Music(bot))