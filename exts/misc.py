import discord
from discord.ext import commands
from asyncio import subprocess, create_subprocess_shell

from utils import files
from utils import create_list, create_birthday_list, cog_check, wups, reply # utils functions

# misc commands start here
# ping, whomuted, avi, emote, convert, translate
class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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

            for file in files:
                create_list(file)
            create_birthday_list()

            return await ctx.send(f'Pong! {round (self.bot.latency * 1000)}ms')
    
    @commands.command(name='whomuted')
    async def whomuted(self, ctx):
        if await cog_check(ctx):
            try:
                return await reply(ctx, ", ".join([member.name for member in ctx.guild.members if member.is_timed_out()]))
            except:
                return await wups(ctx, "No one is muted currently", mention_author=False)
    
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
                return await reply(ctx, f"{value} {org_unit} is equal to {result:.2f} {new_unit}.")
            else:
                return await wups(ctx, "Invalid conversion")
            
    @commands.command(name='translate')
    async def translate(self, ctx, *, phrase):
        if await cog_check(ctx):
            async with ctx.typing():
                process = await create_subprocess_shell(f'trans -b :en "{phrase}"', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = await process.communicate()
                if stderr:
                    return await wups(ctx, f"A translation error occurred. ({stderr.decode().strip()})")
                return await reply(ctx, f"Translated: {stdout.decode().strip()}\n\n*Beware of some inaccuracies. I cannot be 100% accurate...*")

            
async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))
