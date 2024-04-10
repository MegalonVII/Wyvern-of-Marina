import discord
from discord.ext import commands
import asyncio
from googletrans import Translator
from subprocess import run
from utils import *

# misc commands start here
# ping, whomuted, avi, emote, startpoll, convert, translate, grabber
class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()
        self.emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        self.conversions = {
            ("c", "f"): lambda x: x * 9/5 + 32,
            ("f", "c"): lambda x: (x - 32) * 5/9,
            ("m", "ft"): lambda x: x * 3.28084,
            ("ft", "m"): lambda x: x * 0.3048,
            ("kg", "lb"): lambda x: x * 2.20462,
            ("lb", "kg"): lambda x: x * 0.453592,
            ("mi", "km"): lambda x: x * 1.60934,
            ("km", "mi"): lambda x: x * 0.621371,
            ("in", "cm"): lambda x: x * 2.54,
            ("cm", "in"): lambda x: x * 0.393701
        }

    @commands.command(name='ping')
    async def ping(self, ctx):
        if await cog_check(ctx):
            await ctx.message.delete()
            return await ctx.send(f'Pong! {round (self.bot.latency * 1000)}ms')
    
    @commands.command(name='whomuted')
    async def whomuted(self, ctx):
        if await cog_check(ctx):
            try:
                return await ctx.reply(", ".join([member.name for member in ctx.guild.members if member.is_timed_out()]), mention_author=False)
            except:
                await shark_react(ctx.message)
                return await ctx.reply("Wups! No one is muted currently...", mention_author=False)
    
    @commands.command(name='avatar', aliases=['avi'])
    async def avatar(self, ctx, member:discord.Member=None):
        if await cog_check(ctx):
            member = member or ctx.author
            e = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.purple())
            if member.display_avatar.url != member.avatar.url:
                e.set_thumbnail(url=member.avatar.url)
            e.set_image(url=member.display_avatar.url)
            e.set_footer(text=f"Requested by: {ctx.message.author.name}")
            return await ctx.reply(embed=e, mention_author=False)
    
    @commands.command(name='emote')
    async def emote(self, ctx, emote:discord.Emoji):
        if await cog_check(ctx):
            embed = discord.Embed(color=discord.Color.purple())
            embed.description=f"**__Emote Information__**\n**URL**: {emote.url}\n**Name**: {emote.name}\n**ID**: {emote.id}"
            embed.set_image(url=emote.url)
            return await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name='startpoll')
    async def startpoll(self, ctx):
        if await cog_check(ctx):
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            def get_emoji(number):
                return self.emojis[number - 1]
    
            prompt = await ctx.reply('You have 30 seconds to give me the question to ask!', mention_author=False)
            try:
                question = await self.bot.wait_for('message', check=check, timeout=30)
            except asyncio.TimeoutError:
                return await ctx.reply("Time's up! You didn't provide me with a question...", mention_author=False)
            await question.delete()
            prompt = await prompt.edit(content='You now have 1 minute to give me all the possible poll options! Remember, I cannot start a poll with less than 2 options and more than 10 options. Also, all options will be separated by a space.', allowed_mentions=discord.AllowedMentions.none())
            try:
                options = await self.bot.wait_for('message', check=check, timeout=60)
            except asyncio.TimeoutError:
                return await ctx.reply("Time's up! You didn't provide me with any options...", mention_author=False)
            options_list = options.content.split()
            if len(options_list) < 2:
                await shark_react(ctx.message)
                return await ctx.reply('Wups! You can\'t have a poll with less than 2 options...', mention_author=False)
            elif len(options_list) > 10:
                await shark_react(ctx.message)
                return await ctx.reply('Wups! You can\'t have a poll with more than 10 options...', mention_author=False)
            await options.delete()
            await prompt.delete()
    
            poll_embed = discord.Embed(title=f"{ctx.author.name} started a poll!", description=f"**{question.content.upper()}**", color=discord.Color.purple())
            poll_embed.set_thumbnail(url=ctx.author.avatar.url)
            for i, option in enumerate(options_list, 1):
                emoji = get_emoji(i)
                poll_embed.add_field(name=f"{emoji} Option {i}", value=option, inline=False)
            poll_embed.set_footer(text="React to vote!")
            await ctx.message.delete()
            poll_message = await ctx.send(embed=poll_embed)
            for i in range(1, len(options_list) + 1):
                emoji = get_emoji(i)
                await poll_message.add_reaction(emoji)
            return None

    @commands.command(name='convert')
    async def convert(self, ctx, value: float, org_unit: str, new_unit: str):
        if await cog_check(ctx):
            org_unit = org_unit.lower()
            new_unit = new_unit.lower()
            unit_mapping = {"f": "F", "c": "C"}

            if (org_unit, new_unit) in self.conversions:
                result = self.conversions[(org_unit, new_unit)](value)
                org_unit = unit_mapping.get(org_unit, org_unit)
                new_unit = unit_mapping.get(new_unit, new_unit)
                return await ctx.reply(f"{value} {org_unit} is equal to {result:.2f} {new_unit}.", mention_author=False)
            else:
                await shark_react(ctx.message)
                return await ctx.reply("Wups! Invalid conversion...", mention_author=False)
            
    @commands.command(name='translate')
    async def translate(self, ctx, *, phrase):
        if await cog_check(ctx):
            try:
                detected_language = self.translator.detect(phrase)
                if detected_language.lang != 'en':
                    translated_text = self.translator.translate(phrase, src=detected_language.lang, dest='en')
                    return await ctx.reply(f"Translated: {translated_text.text}\n\n*Beware of some inaccuracies. I cannot be 100% accurate...*", mention_author=False)
                else:
                    await shark_react(ctx.message)
                    return await ctx.reply("Wups! Message is already in English...", mention_author=False)
            except Exception as e:
                return await ctx.reply(f"Wups! A translation error occurred... ({e})", mention_author=False)
    
    @commands.command(name='grabber')
    async def grabber(self, ctx, platform: str, *query):
        if await cog_check(ctx) and await in_wom_shenanigans(ctx):
            if platform.lower() not in ['spotify', 'youtube']:
                await shark_react(ctx.message)
                return await reply(ctx, 'Wups! Invalid platform choice! Must be either Spotify or YouTube...')
            
            async with ctx.typing():
                msg = await ctx.reply('Hang tight! I\'m downloading your song. You\'ll be pinged with your song once I finish.', mention_author=False)

                query = " ".join(query)
                if platform == 'spotify':
                    process = await asyncio.create_subprocess_exec('spotdl', 'download', f'{query}')
                    await process.wait()
                elif platform == 'youtube':
                    process = await asyncio.create_subprocess_exec('yt-dlp', f'ytsearch:"{query}"', '-x', '--audio-format', 'mp3', '--output', '%(title)s.%(ext)s')
                    await process.wait()

            new_files = [file for file in os.listdir('.') if file.endswith(".mp3")]
            for file in new_files:
                file_path = os.path.join('.', file)
                await ctx.reply(content='Here is your song!', file=discord.File(file_path))
                os.remove(file_path)
            return await msg.delete()

            
async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))
