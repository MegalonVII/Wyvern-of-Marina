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
            return await reply(f"{message} {emoji}")

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
            return await reply(ctx, 'Wups! I couldn\'t connect to your voice channel. Maybe you\'re not in one or I\'m in a different one...')
      
    @commands.command(name='leave')
    async def _leave(self, ctx: commands.Context):
        if not ctx.voice_state.voice:
            await shark_react(ctx.message)
            return await reply(ctx, 'Wups! I\'m not connected to any voice channel...')
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel or ctx.author.voice is None:
                await shark_react(ctx.message)
                return await reply(ctx, 'Wups! You\'re not in my voice channel...')
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
            return await reply(ctx, 'Wups! I\'m currently not playing anything...')

    @commands.command(name='pause')
    async def _pause(self, ctx: commands.Context):
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel or ctx.author.voice is None:
                await shark_react(ctx.message)
                return await reply(ctx, 'Wups! You\'re not in my voice channel...')
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            return await Music.respond(self, ctx, 'Paused!', '⏸️')
        else:
            await shark_react(ctx.message)
            return await reply(ctx, 'Wups! Nothing to pause...')

    @commands.command(name='resume')
    async def _resume(self, ctx: commands.Context):
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel or ctx.author.voice is None:
                await shark_react(ctx.message)
                return await reply(ctx, 'Wups! You\'re not in my voice channel...')
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            return await Music.respond(self, ctx, 'Resumed!', '▶️')
        else:
            await shark_react(ctx.message)
            return await reply(ctx, 'Wups! Nothing to resume...')

    @commands.command(name='stop')
    async def _stop(self, ctx: commands.Context):
        if ctx.voice_client:
            if ctx.author.voice and ctx.voice_client.channel != ctx.author.voice.channel or ctx.author.voice is None:
                return await reply(ctx, 'Wups! You\'re not in my voice channel...')
        if ctx.voice_state.is_playing:
            ctx.voice_state.songs.clear()
            ctx.voice_state.voice.stop()
            return await Music.respond(self, ctx, 'Stopped!', '⏹️')
        else:
            return await reply(ctx, 'Wups! I\'m not playing any music right now...')

    @commands.command(name='skip')
    async def _skip(self, ctx: commands.Context):
        voter = ctx.message.author
        djRole = discord.utils.get(ctx.guild.roles, name="DJ")
        if ctx.voice_client:
            if ctx.voice_client.channel != voter.voice.channel or voter.voice is None:
                await shark_react(ctx.message)
                return await reply(ctx, 'Wups! You\'re not in my voice channel...')
        if not ctx.voice_state.is_playing:
            await shark_react(ctx.message)
            return await reply(ctx, 'Wups! I\'m not playing any music right now...')
        if voter == ctx.voice_state.current.requester or djRole in voter.roles or voter.guild_permissions.administrator:
            ctx.voice_state.skip()
            return await Music.respond(self, ctx, 'Skipped!', '⏭️')
        else:
            await shark_react(ctx.message)
            return await reply(ctx, 'Wups! You didn\'t request this song to be played (DJs and adminstrators are unaffected)...')

    @commands.command(name='queue')
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        if page < 1:
            await shark_react(ctx.message)
            return await reply(ctx, 'Wups! Invalid page number. Must be greater than or equal to `1`...')
        if len(ctx.voice_state.songs) == 0:
            await shark_react(ctx.message)
            return await reply(ctx, 'Wups! Queue is empty...')
        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)
        if page > pages:
            await shark_react(ctx.message)
            return await reply(ctx, f'Wups! Invalid page number. Must be less than or equal to `{pages}`...')
        
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
                return await reply(ctx, 'Wups! You\'re not in my voice channel...')
        if author.guild_permissions.administrator or djRole in author.roles:
            if len(ctx.voice_state.songs) == 0:
                await shark_react(ctx.message)
                return await reply(ctx, 'Wups! Queue is empty...')
            else:
                ctx.voice_state.songs.shuffle()
                return await Music.respond(self, ctx, 'Queue shuffled!', '🔀')
        else:
            await shark_react(ctx.message)
            return await reply(ctx, 'Wups! You don\'t have the permissions to use this. Must be either a DJ or administrator...')

    @commands.command(name='remove')
    async def _remove(self, ctx: commands.Context, index: int):
        queue = ctx.voice_state.songs
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel or ctx.author.voice is None:
                await shark_react(ctx.message)
                return await reply(ctx, 'Wups! You\'re not in my voice channel...')
        if len(queue) == 0:
            await shark_react(ctx.message)
            return await reply(ctx, 'Wups! Queue is empty...')
        elif index < 0 or index == 0 or index > len(queue):
            await shark_react(ctx.message)
            return await reply(ctx, 'Wups! Index out of bounds...')
        ctx.voice_state.songs.remove(index - 1)
        return await Music.respond(self, ctx, 'Song removed from queue!', '✅')

    @commands.command(name='play')
    async def _play(self, ctx: commands.Context, *, search: str):
        if not ctx.voice_state.voice:
            await shark_react(ctx.message)
            return await reply(ctx, 'Wups! I\'m not connected to a voice channel...')
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                await shark_react(ctx.message)
                return await reply(ctx, 'Wups! I\'m already in a voice channel...')
            
        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search)
            except YTDLError as e:
                await shark_react(ctx.message)
                return await reply(ctx, f'Wups! An error occurred while processing this request... ({str(e)})')
            else:
                song = Song(source)
                await ctx.voice_state.songs.put(song)
                return await reply(ctx, f'Queued {str(source)}')

async def setup(bot):
    await bot.add_cog(Music(bot))