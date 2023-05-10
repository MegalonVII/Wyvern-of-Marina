# fun commands start here
# say, custc, snipe, esnipe, choose, who, howgay, rps, 8ball, roulette, trivia, quote
import discord
import os
import csv
from discord.ext import commands
from keep_alive import keep_alive
import random
import pandas as pd
import asyncio
import datetime
import requests
import json
import urllib.parse
from utils import *

# misc commands start here
# ping, whomuted, avi, emote
class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.message.delete()
        return await ctx.send(f'Pong! {round (self.bot.latency * 1000)}ms')

    @commands.command(name='whomuted')
    async def whomuted(self, ctx):
        try:
            return await ctx.reply(", ".join([member.name for member in ctx.guild.members if member.is_timed_out()]), mention_author=False)
        except:
            return await ctx.reply("Wups! No one is muted currently...", mention_author=False)

    @commands.command(name='avatar', aliases=['avi'])
    async def avatar(self, ctx, member:discord.Member=None):
        member = member or ctx.author
        e = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.purple())
        if member.display_avatar.url != member.avatar.url:
            e.set_thumbnail(url=member.avatar.url)
        e.set_image(url=member.display_avatar.url)
        e.set_footer(text=f"Requested by: {ctx.message.author.name}")
        return await ctx.reply(embed=e, mention_author=False)

    @commands.command(name='emote')
    async def emote(self, ctx, emote:discord.Emoji):
        embed = discord.Embed(color=discord.Color.purple())
        embed.description=f"**__Emote Information__**\n**URL**: {emote.url}\n**Name**: {emote.name}\n**ID**: {emote.id}"
        embed.set_image(url=emote.url)
        return await ctx.reply(embed=embed, mention_author=False)

async def setup(bot):
    await bot.add_cog(Misc(bot))